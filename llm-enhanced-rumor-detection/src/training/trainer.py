import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
from typing import Dict, List, Optional, Tuple
import json

# Optional TensorBoard import
try:
    from torch.utils.tensorboard import SummaryWriter
    TENSORBOARD_AVAILABLE = True
except ImportError:
    print("Warning: TensorBoard not available. Logging will be disabled.")
    SummaryWriter = None
    TENSORBOARD_AVAILABLE = False

from tqdm import tqdm
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from typing import Dict, Optional
from collections import Counter

from ..models.llm_enhanced_mil import LLMEnhancedMIL, create_model
from ..data.data_loader import create_data_loaders


class Trainer:
    """
    Trainer class for LLM-Enhanced MIL model.
    Two-stage training (paper):
      Phase 1: train PostEncoder + binary classifiers + HierarchicalAttention
      Phase 2: freeze Phase-1 params; train only BinaryModelsAggregation
    """

    def __init__(self, config):
        self.config = config
        self.device = torch.device(config.device if torch.cuda.is_available() else 'cpu')

        self.model = create_model(config).to(self.device)

        # Phase-1 optimizer: all params
        self.optimizer_p1 = optim.Adam(
            self.model.parameters(),
            lr=config.training.learning_rate,
            weight_decay=config.training.weight_decay,
        )
        self.scheduler_p1 = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer_p1, mode='min', patience=10, factor=0.5
        )

        # Phase-2 optimizer: aggregation module only
        self.optimizer_p2 = optim.Adam(
            self.model.aggregation.parameters(),
            lr=config.training.learning_rate,
            weight_decay=config.training.weight_decay,
        )
        self.scheduler_p2 = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer_p2, mode='min', patience=10, factor=0.5
        )

        # Epoch counts
        self.num_epochs_phase1 = getattr(config.training, 'num_epochs_phase1', 200)
        self.num_epochs_phase2 = getattr(config.training, 'num_epochs_phase2', 100)

        # Data loaders
        use_mock_llm = getattr(config, 'use_mock_llm', True)
        self.train_loader, self.val_loader, self.test_loader = create_data_loaders(
            config, use_mock_llm=use_mock_llm
        )

        # Training state
        self.current_epoch = 0
        self.best_val_loss = float('inf')
        self.patience_counter = 0
        self.current_phase = 1

        if TENSORBOARD_AVAILABLE:
            self.writer = SummaryWriter(log_dir=config.logging.log_dir)
        else:
            self.writer = None

        self.train_losses = []
        self.val_losses = []

        os.makedirs(config.logging.log_dir, exist_ok=True)
        os.makedirs('checkpoints', exist_ok=True)

    def _freeze_phase1_params(self):
        """Freeze all params except aggregation for Phase 2."""
        for param in self.model.parameters():
            param.requires_grad = False
        for param in self.model.aggregation.parameters():
            param.requires_grad = True

    def _unfreeze_all_params(self):
        """Restore all params to trainable (Phase 1 / reset)."""
        for param in self.model.parameters():
            param.requires_grad = True
        
    def train_epoch(self, phase: int = 1) -> Dict[str, float]:
        """Train for one epoch in the given phase (1 or 2)."""
        self.model.train()
        epoch_losses = []

        optimizer  = self.optimizer_p1  if phase == 1 else self.optimizer_p2
        phase_name = f'Phase{phase}/Ep{self.current_epoch}'

        progress_bar = tqdm(self.train_loader, desc=phase_name)

        for batch_idx, batch_data in enumerate(progress_bar):
            batch_data = self._move_to_device(batch_data)

            # Forward pass
            outputs = self.model(batch_data)

            # Compute loss for the current phase
            losses = self.model.compute_loss(outputs, batch_data, phase=phase)
            total_loss = losses['total_loss']

            # Backward pass
            optimizer.zero_grad()
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(
                filter(lambda p: p.requires_grad, self.model.parameters()),
                self.config.training.gradient_clip_norm,
            )
            optimizer.step()

            epoch_losses.append(total_loss.item())

            progress_bar.set_postfix({
                'loss': f'{total_loss.item():.4f}',
                'lr': f'{optimizer.param_groups[0]["lr"]:.6f}'
            })
            
            if self.writer is not None:
                global_step = self.current_epoch * len(self.train_loader) + batch_idx
                self.writer.add_scalar(f'Phase{self.current_phase}/BatchLoss', total_loss.item(), global_step)
        
        return {'loss': np.mean(epoch_losses) if epoch_losses else 0.0}
    
    def validate_epoch(self, phase: int = 1) -> Dict[str, float]:
        """Validate for one epoch."""
        self.model.eval()
        epoch_losses = []

        with torch.no_grad():
            for batch_data in tqdm(self.val_loader, desc='Validation'):
                batch_data = self._move_to_device(batch_data)
                outputs = self.model(batch_data)
                losses  = self.model.compute_loss(outputs, batch_data, phase=phase)
                epoch_losses.append(losses['total_loss'].item())

        loss_metric = {'loss': np.mean(epoch_losses) if epoch_losses else 0.0}
        eval_metrics = self.evaluate(self.val_loader, phase=phase)
        loss_metric.update(eval_metrics)
        return loss_metric
    
    def train(self):
        """Two-stage training loop (paper §5)."""
        print(f"Device: {self.device}")
        print(f"Model params: {sum(p.numel() for p in self.model.parameters()):,}")
        print(f"Phase 1 epochs: {self.num_epochs_phase1} | Phase 2 epochs: {self.num_epochs_phase2}")

        # ── Phase 1 ─────────────────────────────────────────────────────────
        print("\n=== Phase 1: Training binary classifiers + encoder ===")
        self._unfreeze_all_params()
        self.current_phase = 1
        self.best_val_loss = float('inf')
        self.patience_counter = 0

        for epoch in range(self.num_epochs_phase1):
            self.current_epoch = epoch
            train_metrics = self.train_epoch(phase=1)
            val_metrics   = self.validate_epoch(phase=1)
            self.scheduler_p1.step(val_metrics['loss'])
            self._log_epoch_metrics(train_metrics, val_metrics, phase=1)

            if epoch % self.config.logging.save_every_n_epochs == 0:
                self._save_checkpoint(epoch, val_metrics['loss'], tag='p1')

            if val_metrics['loss'] < self.best_val_loss:
                self.best_val_loss = val_metrics['loss']
                self.patience_counter = 0
                self._save_best_model(tag='p1')
            else:
                self.patience_counter += 1
            if self.patience_counter >= self.config.training.patience:
                print(f"Phase 1 early stop at epoch {epoch}")
                break

        # ── Phase 2 ─────────────────────────────────────────────────────────
        print("\n=== Phase 2: Training aggregation module only ===")
        self._freeze_phase1_params()
        self.current_phase = 2
        self.best_val_loss = float('inf')
        self.patience_counter = 0

        for epoch in range(self.num_epochs_phase2):
            self.current_epoch = epoch
            train_metrics = self.train_epoch(phase=2)
            val_metrics   = self.validate_epoch(phase=2)
            self.scheduler_p2.step(val_metrics['loss'])
            self._log_epoch_metrics(train_metrics, val_metrics, phase=2)

            if epoch % self.config.logging.save_every_n_epochs == 0:
                self._save_checkpoint(epoch, val_metrics['loss'], tag='p2')

            if val_metrics['loss'] < self.best_val_loss:
                self.best_val_loss = val_metrics['loss']
                self.patience_counter = 0
                self._save_best_model(tag='p2')
            else:
                self.patience_counter += 1
            if self.patience_counter >= self.config.training.patience:
                print(f"Phase 2 early stop at epoch {epoch}")
                break

        self._unfreeze_all_params()
        print("\nTraining completed!")
        if self.writer is not None:
            self.writer.close()
    
    def evaluate(self, data_loader=None, phase: int = None) -> Dict[str, float]:
        """Evaluate the model.
        
        Args:
            data_loader: Data loader to evaluate on
            phase: Training phase (1 or 2). If None, use current_phase.
        """
        if data_loader is None:
            data_loader = self.test_loader
        
        if phase is None:
            phase = self.current_phase
        
        self.model.eval()
        all_rumor_preds = []
        all_rumor_labels = []
        all_stance_preds = []
        all_stance_labels = []
        
        with torch.no_grad():
            for batch_data in tqdm(data_loader, desc='Evaluation'):
                batch_data = self._move_to_device(batch_data)
                
                # Get predictions (use Phase 1 logic if in Phase 1)
                use_phase1_logic = (phase == 1)
                predictions = self.model.predict(batch_data, use_phase1_logic=use_phase1_logic)
                
                # Collect results
                rumor_pred = predictions['rumor_class'].cpu().numpy()
                rumor_label = batch_data['rumor_label'].cpu().numpy() if isinstance(batch_data['rumor_label'], torch.Tensor) else batch_data['rumor_label']
                
                # 确保是标量值
                if hasattr(rumor_pred, 'item'):
                    rumor_pred = rumor_pred.item()
                if hasattr(rumor_label, 'item'):
                    rumor_label = rumor_label.item()
                    
                all_rumor_preds.append(rumor_pred)
                all_rumor_labels.append(rumor_label)
                
                if 'stance_labels' in batch_data:
                    all_stance_preds.extend(predictions['stance_classes'].cpu().numpy())
                    all_stance_labels.extend(batch_data['stance_labels'].cpu().numpy())
        
        # Compute metrics
        metrics = {}
        
        # Rumor detection metrics
        if all_rumor_preds and all_rumor_labels:
            rumor_acc = accuracy_score(all_rumor_labels, all_rumor_preds)
            
            rumor_precision, rumor_recall, rumor_f1, _ = precision_recall_fscore_support(
                all_rumor_labels, all_rumor_preds, average='macro'
            )
            metrics.update({
                'rumor_accuracy': rumor_acc,
                'rumor_precision': rumor_precision,
                'rumor_recall': rumor_recall,
                'rumor_f1': rumor_f1
            })
        
        # Stance detection metrics
        if all_stance_preds and all_stance_labels:
            stance_acc = accuracy_score(all_stance_labels, all_stance_preds)
            stance_precision, stance_recall, stance_f1, _ = precision_recall_fscore_support(
                all_stance_labels, all_stance_preds, average='macro'
            )
            metrics.update({
                'stance_accuracy': stance_acc,
                'stance_precision': stance_precision,
                'stance_recall': stance_recall,
                'stance_f1': stance_f1
            })
        
        return metrics
    
    def _move_to_device(self, batch_data: Dict) -> Dict:
        """Move batch data to device."""
        if isinstance(batch_data.get('rumor_label'), torch.Tensor):
            batch_data['rumor_label'] = batch_data['rumor_label'].to(self.device)
        elif isinstance(batch_data.get('rumor_label'), (int, np.integer)):
            batch_data['rumor_label'] = torch.tensor(batch_data['rumor_label']).to(self.device)
        
        if 'stance_labels' in batch_data:
            batch_data['stance_labels'] = batch_data['stance_labels'].to(self.device)
        
        return batch_data
    
    def _log_epoch_metrics(self, train_metrics: Dict, val_metrics: Dict, phase: int = 1):
        """Log metrics for the epoch."""
        print(f"\n[P{phase}] Epoch {self.current_epoch}: "
              f"train_loss={train_metrics['loss']:.4f}  val_loss={val_metrics['loss']:.4f}")
        if 'rumor_accuracy' in val_metrics:
            print(f"  rumor_acc={val_metrics['rumor_accuracy']:.4f}  "
                  f"rumor_f1={val_metrics.get('rumor_f1', 0):.4f}")
        if self.writer is not None:
            prefix = f'Phase{phase}'
            self.writer.add_scalar(f'{prefix}/TrainLoss', train_metrics['loss'], self.current_epoch)
            self.writer.add_scalar(f'{prefix}/ValLoss',   val_metrics['loss'],   self.current_epoch)
            for key, value in val_metrics.items():
                if key != 'loss':
                    self.writer.add_scalar(f'{prefix}/{key}', value, self.current_epoch)
    
    def _save_checkpoint(self, epoch: int, val_loss: float, tag: str = ''):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'val_loss': val_loss,
            'config': self.config,
        }
        path = f'checkpoints/checkpoint_{tag}_epoch_{epoch}.pt'
        torch.save(checkpoint, path)
        print(f"Checkpoint saved: {path}")

    def _save_best_model(self, tag: str = ''):
        """Save the best model."""
        path = f'checkpoints/best_model_{tag}.pt' if tag else 'checkpoints/best_model.pt'
        torch.save(self.model.state_dict(), path)
        print(f"Best model saved: {path}")
    
    def load_checkpoint(self, checkpoint_path: str):
        """Load model from checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.current_epoch  = checkpoint.get('epoch', 0)
        self.best_val_loss  = checkpoint.get('val_loss', float('inf'))
        print(f"Checkpoint loaded from {checkpoint_path}")


def create_trainer(config) -> Trainer:
    """Factory function to create trainer."""
    return Trainer(config)

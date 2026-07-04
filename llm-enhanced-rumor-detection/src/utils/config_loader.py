import yaml
import os
from typing import Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ModelConfig:
    name: str = "LLMEnhancedMIL"
    
    @dataclass
    class PostEncoder:
        sentence_bert_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
        bert_model: str = "bert-base-chinese"
        hidden_dim: int = 768
        dropout: float = 0.1
        retention_ratio: float = 0.3
    
    @dataclass
    class MIL:
        num_rumor_classes: int = 2
        num_stance_classes: int = 4
        num_binary_classifiers: int = 8
    
    @dataclass
    class Attention:
        local_retention_ratio: float = 0.5
        global_attention_dim: int = 256
    
    @dataclass
    class LLM:
        model: str = "gpt-3.5-turbo"
        max_tokens: int = 150
        temperature: float = 0.3
    
    post_encoder: PostEncoder = field(default_factory=PostEncoder)
    mil: MIL = field(default_factory=MIL)
    attention: Attention = field(default_factory=Attention)
    llm: LLM = field(default_factory=LLM)


@dataclass
class TrainingConfig:
    batch_size: int = 1
    learning_rate: float = 0.001
    num_epochs_phase1: int = 200
    num_epochs_phase2: int = 100
    warmup_steps: int = 0
    weight_decay: float = 0.0
    gradient_clip_norm: float = 1.0
    patience: int = 30
    min_delta: float = 0.001


@dataclass
class DataConfig:
    max_posts_per_claim: int = 100
    max_post_length: int = 128
    max_explanation_length: int = 256
    train_data: str = "data/train.json"
    val_data: str = "data/val.json"
    test_data: str = "data/test.json"


@dataclass
class EvaluationConfig:
    metrics: list = field(default_factory=lambda: ["accuracy", "precision", "recall", "f1"])
    save_predictions: bool = True


@dataclass
class LoggingConfig:
    log_dir: str = "logs"
    tensorboard_dir: str = "runs"
    save_every_n_epochs: int = 5


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    device: str = "cuda"
    num_workers: int = 4
    pin_memory: bool = True
    use_mock_llm: bool = True  # Default to mock for safety, set to False for real LLM


def load_config(config_path: str) -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration object
    """
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        print("Using default configuration")
        return Config()
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
    
    # Create config object from dictionary
    config = Config()
    
    # Update model config
    if 'model' in config_dict:
        model_dict = config_dict['model']
        if 'post_encoder' in model_dict:
            for key, value in model_dict['post_encoder'].items():
                # yaml may use 'model_name' as alias for 'sentence_bert_model'
                if key == 'model_name':
                    key = 'sentence_bert_model'
                setattr(config.model.post_encoder, key, value)
        if 'mil' in model_dict:
            for key, value in model_dict['mil'].items():
                setattr(config.model.mil, key, value)
        if 'attention' in model_dict:
            for key, value in model_dict['attention'].items():
                setattr(config.model.attention, key, value)
        if 'llm' in model_dict:
            for key, value in model_dict['llm'].items():
                setattr(config.model.llm, key, value)
    
    # Update training config
    if 'training' in config_dict:
        for key, value in config_dict['training'].items():
            setattr(config.training, key, value)
    
    # Update data config
    if 'data' in config_dict:
        for key, value in config_dict['data'].items():
            setattr(config.data, key, value)
    
    # Update evaluation config
    if 'evaluation' in config_dict:
        for key, value in config_dict['evaluation'].items():
            setattr(config.evaluation, key, value)
    
    # Update logging config
    if 'logging' in config_dict:
        for key, value in config_dict['logging'].items():
            setattr(config.logging, key, value)
    
    # Update top-level config
    for key in ['device', 'num_workers', 'pin_memory', 'use_mock_llm']:
        if key in config_dict:
            setattr(config, key, config_dict[key])
    
    return config


def save_config(config: Config, config_path: str):
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration object
        config_path: Path to save the configuration
    """
    config_dict = {
        'model': {
            'name': config.model.name,
            'post_encoder': {
                'sentence_bert_model': config.model.post_encoder.sentence_bert_model,
                'bert_model': config.model.post_encoder.bert_model,
                'hidden_dim': config.model.post_encoder.hidden_dim,
                'dropout': config.model.post_encoder.dropout,
                'retention_ratio': config.model.post_encoder.retention_ratio
            },
            'mil': {
                'num_rumor_classes': config.model.mil.num_rumor_classes,
                'num_stance_classes': config.model.mil.num_stance_classes,
                'num_binary_classifiers': config.model.mil.num_binary_classifiers
            },
            'attention': {
                'local_retention_ratio': config.model.attention.local_retention_ratio,
                'global_attention_dim': config.model.attention.global_attention_dim
            },
            'llm': {
                'model': config.model.llm.model,
                'max_tokens': config.model.llm.max_tokens,
                'temperature': config.model.llm.temperature
            }
        },
        'training': {
            'batch_size': config.training.batch_size,
            'learning_rate': config.training.learning_rate,
            'num_epochs_phase1': config.training.num_epochs_phase1,
            'num_epochs_phase2': config.training.num_epochs_phase2,
            'warmup_steps': config.training.warmup_steps,
            'weight_decay': config.training.weight_decay,
            'gradient_clip_norm': config.training.gradient_clip_norm,
            'patience': config.training.patience,
            'min_delta': config.training.min_delta
        },
        'data': {
            'max_posts_per_claim': config.data.max_posts_per_claim,
            'max_post_length': config.data.max_post_length,
            'max_explanation_length': config.data.max_explanation_length,
            'train_data': config.data.train_data,
            'val_data': config.data.val_data,
            'test_data': config.data.test_data
        },
        'evaluation': {
            'metrics': config.evaluation.metrics,
            'save_predictions': config.evaluation.save_predictions
        },
        'logging': {
            'log_dir': config.logging.log_dir,
            'tensorboard_dir': config.logging.tensorboard_dir,
            'save_every_n_epochs': config.logging.save_every_n_epochs
        },
        'device': config.device,
        'num_workers': config.num_workers,
        'pin_memory': config.pin_memory,
        'use_mock_llm': config.use_mock_llm
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_dict, f, default_flow_style=False, indent=2)

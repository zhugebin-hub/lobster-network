#!/usr/bin/env python3
"""
小龙虾网络V3.0 - 跨域学员档案 (Cross-Domain Student Profile)

Aggregates learning data from multiple domains (go / networking / stock)
into a single unified profile per student.

Usage:
    python -m core.student_profile build-all
    python -m core.student_profile show qoder
    python -m core.student_profile show xiaochen
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# 路径配置
# ============================================================

REPO_ROOT = Path(__file__).parent.parent

# Go training data
TRAINING_RESULTS_DIR = REPO_ROOT / "docs" / "training_results"
SHARED_GO_DIR = REPO_ROOT / ".shared" / "training" / "go"

# Networking data
NETWORK_PROGRESS_FILE = (
    REPO_ROOT / "domains" / "networking" / "trainers" / "state"
    / "network_learning_progress.json"
)

# Stock data
STOCK_STATE_DIR = REPO_ROOT / "domains" / "learning" / "state"

# Output
PROFILES_DIR = REPO_ROOT / ".shared" / "profiles"

# Default total chapters in the networking course
DEFAULT_TOTAL_CHAPTERS = 7

# ============================================================
# 名称映射 (student_id <-> display_name)
# ============================================================

STUDENT_DISPLAY_NAMES: Dict[str, str] = {
    "qoder": "qoder小龙虾",
    "xiaochen": "小陈",
    "zhuguxia": "诸葛虾",
    "zhuguma": "诸葛马",
    "xiaowei": "小魏",
    "院史馆小龙虾": "院史馆小龙虾",
}

# Reverse map: Chinese display name -> student_id
DISPLAY_TO_ID: Dict[str, str] = {v: k for k, v in STUDENT_DISPLAY_NAMES.items()}

# ============================================================
# 辅助函数
# ============================================================


def _parse_pct(value) -> float:
    """Parse a percentage string like '87.3%' into a float (87.3).
    Returns 0.0 for non-string or unparseable values."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        m = re.search(r"([\d.]+)", value.replace("%", ""))
        if m:
            return float(m.group(1))
    return 0.0


def _safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Division that returns *default* when denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def _discover_active_students() -> List[str]:
    """Scan all data sources and return a deduplicated list of student IDs."""
    students = set()

    # From go training results
    if TRAINING_RESULTS_DIR.is_dir():
        for p in TRAINING_RESULTS_DIR.glob("day*_result_*.json"):
            # e.g. day1_result_qoder.json -> qoder
            parts = p.stem.split("_result_")
            if len(parts) == 2:
                students.add(parts[1])

    # From .shared/training/go/from-{student}/
    if SHARED_GO_DIR.is_dir():
        for d in SHARED_GO_DIR.iterdir():
            if d.is_dir() and d.name.startswith("from-"):
                students.add(d.name[len("from-"):])

    # From networking progress
    if NETWORK_PROGRESS_FILE.is_file():
        try:
            data = json.loads(NETWORK_PROGRESS_FILE.read_text(encoding="utf-8"))
            for display_name in data.get("students", {}):
                sid = DISPLAY_TO_ID.get(display_name, display_name)
                students.add(sid)
        except (json.JSONDecodeError, OSError):
            pass

    return sorted(students)


# ============================================================
# StudentProfile
# ============================================================


class StudentProfile:
    """Unified cross-domain student profile for the Lobster Network."""

    def __init__(self, student_id: str):
        self.student_id: str = student_id
        self.display_name: str = STUDENT_DISPLAY_NAMES.get(student_id) or (
            student_id
            if any("\u4e00" <= c <= "\u9fff" for c in student_id)
            else student_id + "小龙虾"
        )

        # Per-domain raw data (populated by load_* methods)
        self._go_data: Dict = {}
        self._network_data: Dict = {}
        self._stock_data: Dict = {}

        # Final aggregated profile
        self.profile: Optional[Dict] = None

    # ----------------------------------------------------------
    # Go (围棋)
    # ----------------------------------------------------------

    def load_go_training(self) -> Dict:
        """Parse Go training data from docs/training_results/ and
        .shared/training/go/from-{student}/.

        Returns a dict with keys:
            days_completed, total_problems, correct_problems, accuracy,
            total_games, wins, losses, win_rate
        """
        all_problems: List[dict] = []
        all_games: List[dict] = []
        days_seen: set = set()
        aggregated_problems_total = 0
        aggregated_problems_correct = 0
        aggregated_games_total = 0
        aggregated_games_wins = 0
        has_summary = False

        # Collect JSON files from both directories
        json_files: List[Path] = []
        if TRAINING_RESULTS_DIR.is_dir():
            json_files.extend(
                TRAINING_RESULTS_DIR.glob(f"day*_result_{self.student_id}.json")
            )
        student_shared = SHARED_GO_DIR / f"from-{self.student_id}"
        if student_shared.is_dir():
            json_files.extend(student_shared.glob("day*.json"))

        for jf in sorted(json_files):
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            # Track which day this belongs to
            day = data.get("day")
            if day is not None:
                days_seen.add(day)

            # Prefer pre-computed summaries when available
            ps = data.get("problems_summary")
            gs = data.get("games_summary")

            if ps and isinstance(ps, dict) and "total" in ps:
                has_summary = True
                aggregated_problems_total += int(ps.get("total", 0))
                aggregated_problems_correct += int(ps.get("correct", 0))
            else:
                # Fall back to raw problems array
                raw_probs = data.get("problems", [])
                if isinstance(raw_probs, list):
                    all_problems.extend(raw_probs)

            if gs and isinstance(gs, dict) and "total" in gs:
                has_summary = True
                aggregated_games_total += int(gs.get("total", 0))
                aggregated_games_wins += int(gs.get("wins", 0))
            else:
                # Fall back to raw games array
                raw_games_list = data.get("games", [])
                if isinstance(raw_games_list, list):
                    all_games.extend(raw_games_list)

        # Compute from raw arrays for items without summaries
        raw_total = len(all_problems)
        raw_correct = sum(1 for p in all_problems if p.get("is_correct"))
        raw_games = len(all_games)
        raw_wins = sum(1 for g in all_games if g.get("is_win"))

        total_problems = aggregated_problems_total + raw_total
        correct_problems = aggregated_problems_correct + raw_correct
        total_games = aggregated_games_total + raw_games
        wins = aggregated_games_wins + raw_wins
        losses = total_games - wins

        accuracy = _safe_div(correct_problems, total_problems) * 100
        win_rate = _safe_div(wins, total_games) * 100

        self._go_data = {
            "days_completed": len(days_seen),
            "total_problems": total_problems,
            "correct_problems": correct_problems,
            "accuracy": round(accuracy, 1),
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 1),
        }
        return self._go_data

    # ----------------------------------------------------------
    # Networking (网络)
    # ----------------------------------------------------------

    def load_network_progress(self) -> Dict:
        """Parse networking learning progress from
        domains/networking/trainers/state/network_learning_progress.json.

        Returns a dict with keys:
            type, chapters_completed, total_chapters, progress_pct,
            problems_solved, problems_correct, accuracy
        """
        if not NETWORK_PROGRESS_FILE.is_file():
            self._network_data = self._empty_network()
            return self._network_data

        try:
            data = json.loads(NETWORK_PROGRESS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._network_data = self._empty_network()
            return self._network_data

        # Look up by display name or raw student_id
        display = self.display_name
        students = data.get("students", {})
        student_record = students.get(display) or students.get(self.student_id)

        if not student_record:
            # Try partial match
            for name, rec in students.items():
                if self.student_id in name or name in self.student_id:
                    student_record = rec
                    break

        if not student_record:
            self._network_data = self._empty_network()
            return self._network_data

        completed = student_record.get("completed_chapters", [])
        solved = int(student_record.get("problems_solved", 0))
        correct = int(student_record.get("problems_correct", 0))
        student_type = student_record.get("type", "未知")
        total_chapters = int(data.get("total_chapters", DEFAULT_TOTAL_CHAPTERS))
        progress_pct = round(_safe_div(len(completed), total_chapters) * 100, 1)
        accuracy = round(_safe_div(correct, solved) * 100, 1)

        self._network_data = {
            "type": student_type,
            "chapters_completed": len(completed),
            "total_chapters": total_chapters,
            "progress_pct": progress_pct,
            "problems_solved": solved,
            "problems_correct": correct,
            "accuracy": accuracy,
        }
        return self._network_data

    @staticmethod
    def _empty_network() -> Dict:
        return {
            "type": "未知",
            "chapters_completed": 0,
            "total_chapters": DEFAULT_TOTAL_CHAPTERS,
            "progress_pct": 0.0,
            "problems_solved": 0,
            "problems_correct": 0,
            "accuracy": 0.0,
        }

    # ----------------------------------------------------------
    # Stock (股票)
    # ----------------------------------------------------------

    def load_stock_progress(self) -> Dict:
        """Parse stock/finance learning data from
        domains/learning/state/ (if available).

        Returns a dict with keys:
            problems, correct, accuracy
        """
        if not STOCK_STATE_DIR.is_dir():
            self._stock_data = self._empty_stock()
            return self._stock_data

        # Look for files that might contain this student's stock data
        total_problems = 0
        total_correct = 0
        found = False

        for jf in STOCK_STATE_DIR.glob("*.json"):
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            # Try dict-style (keyed by student) or direct
            if isinstance(data, dict):
                student_rec = (
                    data.get(self.student_id)
                    or data.get(self.display_name)
                )
                if student_rec and isinstance(student_rec, dict):
                    total_problems += int(student_rec.get("problems", 0))
                    total_correct += int(student_rec.get("correct", 0))
                    found = True
                elif "problems" in data and "student_id" in data:
                    if data.get("student_id") == self.student_id:
                        total_problems += int(data.get("problems", 0))
                        total_correct += int(data.get("correct", 0))
                        found = True

        if not found:
            self._stock_data = self._empty_stock()
            return self._stock_data

        accuracy = round(_safe_div(total_correct, total_problems) * 100, 1)
        self._stock_data = {
            "problems": total_problems,
            "correct": total_correct,
            "accuracy": accuracy,
        }
        return self._stock_data

    @staticmethod
    def _empty_stock() -> Dict:
        return {
            "problems": 0,
            "correct": 0,
            "accuracy": None,  # signals "N/A"
        }

    # ----------------------------------------------------------
    # Aggregation
    # ----------------------------------------------------------

    def build_profile(self) -> Dict:
        """Aggregate all domain data into a unified profile dict."""
        if not self._go_data:
            self.load_go_training()
        if not self._network_data:
            self.load_network_progress()
        if not self._stock_data:
            self.load_stock_progress()

        go = self._go_data
        net = self._network_data
        stk = self._stock_data

        # Determine student type from network data (most informative source)
        student_type = net.get("type", "未知")

        # Format domain summaries
        go_domain = {
            "days_completed": go["days_completed"],
            "total_problems": go["total_problems"],
            "accuracy": f"{go['accuracy']}%" if go["total_problems"] else "N/A",
            "total_games": go["total_games"],
            "win_rate": f"{go['win_rate']}%" if go["total_games"] else "N/A",
        }

        net_domain = {
            "chapters_completed": net["chapters_completed"],
            "total": net["total_chapters"],
            "progress": f"{net['progress_pct']}%",
            "accuracy": f"{net['accuracy']}%" if net["problems_solved"] else "N/A",
        }

        stk_domain = {
            "problems": stk["problems"],
            "accuracy": f"{stk['accuracy']}%" if stk["accuracy"] is not None else "N/A",
        }

        # Composite score (use raw numeric values; treat missing as 0)
        go_acc = go["accuracy"] if go["total_problems"] else 0.0
        net_pct = net["progress_pct"]
        stk_acc = stk["accuracy"] if stk["accuracy"] is not None else 0.0

        composite = round(go_acc * 0.4 + net_pct * 0.3 + stk_acc * 0.3, 1)

        self.profile = {
            "student_id": self.student_id,
            "display_name": self.display_name,
            "type": student_type,
            "domains": {
                "go": go_domain,
                "networking": net_domain,
                "stock": stk_domain,
            },
            "composite_score": composite,
            "ranking": 0,  # filled in by get_ranking / build_all_profiles
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        return self.profile

    def save_profile(self) -> Path:
        """Write profile to .shared/profiles/{student_id}.json.
        Returns the output path."""
        if self.profile is None:
            self.build_profile()

        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        out = PROFILES_DIR / f"{self.student_id}.json"
        out.write_text(
            json.dumps(self.profile, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return out

    # ----------------------------------------------------------
    # Ranking
    # ----------------------------------------------------------

    def get_ranking(self) -> float:
        """Return the composite score (used for cross-domain ranking).
        Also stores it in self.profile['ranking'] when profile exists."""
        if self.profile is None:
            self.build_profile()
        return self.profile["composite_score"]


# ============================================================
# Batch operations
# ============================================================


def build_all_profiles() -> Dict[str, Dict]:
    """Build and save profiles for all active students.
    Returns a dict mapping student_id -> profile, sorted by composite score
    (ranking field is populated)."""
    student_ids = _discover_active_students()
    profiles: List[Tuple[str, Dict]] = []

    for sid in student_ids:
        sp = StudentProfile(sid)
        sp.build_profile()
        profiles.append((sid, sp.profile))

    # Sort descending by composite score and assign ranking
    profiles.sort(key=lambda x: x[1]["composite_score"], reverse=True)
    for rank, (sid, prof) in enumerate(profiles, start=1):
        prof["ranking"] = rank

    # Save all profiles
    results: Dict[str, Dict] = {}
    for sid, prof in profiles:
        sp = StudentProfile(sid)
        sp.profile = prof
        sp.save_profile()
        results[sid] = prof

    return results


# ============================================================
# CLI
# ============================================================


def _print_profile(profile: Dict) -> None:
    """Pretty-print a single profile to stdout."""
    print(json.dumps(profile, ensure_ascii=False, indent=2))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__.strip())
        print()
        print("Commands:")
        print("  build-all              Build & save profiles for all students")
        print("  show <student_id>      Show profile for one student")
        sys.exit(0)

    command = sys.argv[1]

    if command == "build-all":
        results = build_all_profiles()
        if not results:
            print("No active students found.")
            sys.exit(0)

        print(f"Built {len(results)} profile(s). Saved to {PROFILES_DIR}/\n")
        print(f"{'Rank':<6}{'Student':<20}{'Score':<10}{'Type':<10}")
        print("-" * 46)
        for sid, prof in results.items():
            print(
                f"{prof['ranking']:<6}"
                f"{prof['display_name']:<20}"
                f"{prof['composite_score']:<10}"
                f"{prof['type']:<10}"
            )
        print()
        print("To view individual profiles:")
        for sid in results:
            print(f"  python -m core.student_profile show {sid}")

    elif command == "show":
        if len(sys.argv) < 3:
            print("Usage: python -m core.student_profile show <student_id>")
            sys.exit(1)
        sid = sys.argv[2]
        sp = StudentProfile(sid)
        profile = sp.build_profile()
        _print_profile(profile)

    else:
        print(f"Unknown command: {command}")
        print("Available commands: build-all, show")
        sys.exit(1)


if __name__ == "__main__":
    main()

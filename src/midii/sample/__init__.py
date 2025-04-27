from pathlib import Path

sample_path = Path(__file__).parent
dataset = sorted(
    [f for f in (sample_path / "dataset").rglob("*.mid") if f.is_file()]
)
simple = sorted(
    [f for f in (sample_path / "simple").rglob("*.mid") if f.is_file()]
)

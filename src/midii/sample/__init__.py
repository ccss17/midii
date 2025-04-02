from pathlib import Path

sample_path = Path(__file__).parent
dataset = [f for f in (sample_path / "dataset").rglob("*.mid") if f.is_file()]
real = [f for f in (sample_path / "real").rglob("*.mid") if f.is_file()]
simple = [f for f in (sample_path / "simple").rglob("*.mid") if f.is_file()]

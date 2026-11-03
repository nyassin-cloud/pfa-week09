from pathlib import Path

script = Path(
    r"C:\Users\free\Documents\Codex\2026-11-02"
    r"\i-need-help-creating-a-new\outputs\sketch_bloom.py"
)

exec(
    compile(script.read_text(encoding="utf-8-sig"), str(script), "exec"),
    {"__name__": "__main__", "__file__": str(script)}
)

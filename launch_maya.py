"""Run this file via exec(...) in Maya's Python Script Editor."""
from pathlib import Path
import sys
ROOT = str(Path(__file__).resolve().parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from sketch_bloom import maya_app
WINDOW = maya_app.show()

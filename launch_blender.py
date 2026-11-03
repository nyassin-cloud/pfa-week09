"""Open this saved file in Blender's Text Editor and click Run Script."""
from pathlib import Path
import sys
import bpy
text = bpy.context.space_data.text if bpy.context.area and bpy.context.area.type == 'TEXT_EDITOR' else None
if not text or not text.filepath:
    raise RuntimeError('Open the saved launch_blender.py in the Text Editor first.')
ROOT = str(Path(bpy.path.abspath(text.filepath)).resolve().parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from sketch_bloom import blender_app
blender_app.register()
print('Sketch Bloom registered. 3D Viewport > N > Sketch Bloom.')

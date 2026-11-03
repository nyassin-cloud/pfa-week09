# Sketch Bloom

Sketch Bloom turns drawings into 3D tubes, curves, and filled shapes. I started it in Maya for Week 8. For Week 9, I added a Low Poly option, a Blender version, and OBJ export.

The tool runs inside **Maya or Blender**. You can export meshes to other 3D apps that import OBJ.

## Demo

Recording coming soon. I still need to add the 1–3 minute video link before submitting.

## Download

Download this repository using **Code > Download ZIP**, then extract it. Keep the whole folder together; the launch scripts need the `sketch_bloom` folder beside them.

Or clone it with Git:

```sh
git clone https://github.com/nyassin-cloud/pfa-week09.git
```

You need Maya or Blender installed. There are no extra Python packages to install. The intended versions are Maya 2024–2026 and Blender 4.2/4.3; the Week 9 version still needs testing in the apps.

## Run in Maya

1. Open **Windows > General Editors > Script Editor**.
2. Choose a **Python** tab.
3. Paste the code below. Replace the example folder with the location where you extracted or cloned the project. Use forward slashes in the path.
4. Select both lines and run them with **Ctrl + Enter**.

```python
import runpy
runpy.run_path("C:/projects/pfa-week09/launch_maya.py", run_name="__main__")
```

In the **Draw** tab, drag on the canvas to make a stroke, or choose a shape and click **Add shape**. Choose Tube, Curve, or Filled shape to change what you draw. Click a drawing to edit it.

Click **Low Poly mode** for fewer polygons. **Standard density** restores the more detailed settings. Select a mesh to see its actual face count.

The **Assemble Parts** tab includes a teacup starter. To compare low and standard density, turn off **Fuse teacup body and handle** before creating each cup. Save your Maya scene to keep your objects.

## Run in Blender

1. Open Blender and switch to the **Scripting** workspace.
2. In the Text Editor, choose **Text > Open** and open `launch_blender.py` from the project folder.
3. Click **Run Script**. Open the saved file rather than pasting its code into a new text block.
4. Return to **Layout**. Move your mouse over the 3D Viewport, press **N**, and open the **Sketch Bloom** tab.
5. Stay in **Object Mode** to use the tool.

Choose Tube, Filled, or Curve, then click **Draw Stroke**. Drag with the left mouse button in the viewport and release to create the result. Press Esc to cancel. You can also use **Create Filled Preset** or **Create Teacup Parts**.

**Low Poly mode** starts enabled. Turn it off for more detail. Select a result to see its face count, or press **Tab** to edit its vertices or curve points with Blender tools. Return to Object Mode before using another Bloom action.

Save your `.blend` file to keep your objects. Run the launcher again when you start a new Blender session.

## Low Poly mode

My peer asked for a way to make lighter meshes. Low Poly uses fewer samples along a stroke and fewer sides around a tube. It also lowers the teacup density. The result can look more angular, but it is easier to keep the face count down.

Low Poly changes how geometry is created. It does not automatically simplify every object already in the scene. You can still change the settings afterward, and subdivision adds polygons.

For an existing mesh, Maya has **Retopology > Use Selected Object > Retopologize Copy**. Blender has **Decimate copy** to reduce faces; it does not create new quad topology. Both work on copies.

## Export to other apps

Select your polygon meshes and use **Export selected meshes OBJ** in Maya or **Export Selected Meshes OBJ** in Blender. Choose a file location, then import the OBJ into your other 3D app.

This exports geometry only. Materials, UVs, rigs, animation, and curves are not included. Check the scale and orientation after importing.

## Peer run — A6

> I had my AI agent follow the README and it successfully installed the tool then ran it. I did not find any errors from testing the tool manually but I was confused about how high-poly the retopology was and wondered if there could be an implementation to offer a low-poly mode? Overall, it ran smoothly and nothing broke.

**What I fixed:** I added Low Poly presets and face counts so it is easier to control how dense the results are. I also clarified which settings create fewer polygons and which add detail. This feedback is from Week 8; the Week 9 changes still need testing in Maya and Blender.

## What does not work yet

- The Week 9 Maya and Blender interfaces still need a full test from a fresh download. The shared Python tests are separate from app testing.
- Blender has a smaller shape library and no live preview while drawing. Results appear when you release the mouse.
- Blender does not yet have Maya-style retopology or the full Maya studio interface.
- Filled surface drawing is not supported. Some tangled outlines and tight tube bends can fail or intersect themselves.
- Fusing parts needs overlapping solids and may fail on complex geometry.

The app test checklist is in [docs/TESTING.md](docs/TESTING.md).

## What I would build next

I would add a live drawing preview in Blender, expand its shape library, and make point editing more consistent between the two apps. I would also improve export so materials and UVs can be carried over.

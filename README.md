# Sketch Bloom

Sketch Bloom is a Maya script that turns drawings into 3D tubes, curves, and filled shapes. For Week 9, I added a Low Poly option to make lighter meshes and show their face counts.

## How to run

You only need Maya and the script. No project folders or extra Python packages are required.

1. Open [sketch_bloom.py](sketch_bloom.py) and click **Raw**. Copy all the code.
2. In Maya, open **Windows > General Editors > Script Editor**.
3. Choose a **Python** tab and paste the code.
4. Select all the pasted code and press **Ctrl + Enter**.

## How to use it

- In the **Draw** tab, drag on the canvas to draw. Choose **Tube**, **Curve**, or **Filled shape** to change the result.
- Click a drawing to edit it. Drag a point to reshape it, or drag the outline to move it.
- Choose a shape from the library and click **Add shape** for a starting outline.
- Click **Low Poly mode** for fewer polygons, or **Standard density** for more detail. Select a mesh to see its actual face count.

Low Poly changes the drawing settings and the density of the next drawing. It does not automatically reduce every mesh in the scene. Subdivision adds polygons. To rebuild an existing mesh, use **Retopology > Use Selected Object > Retopologize Copy**; the target count is approximate.

## Peer run — A6

> I had my AI agent follow the README and it successfully installed the tool then ran it. I did not find any errors from testing the tool manually but I was confused about how high-poly the retopology was and wondered if there could be an implementation to offer a low-poly mode? Overall, it ran smoothly and nothing broke.

**What I fixed:** I added Low Poly presets and face counts so it is easier to control how dense the results are.

## What does not work yet

- This version runs in Maya. It does not run in Blender.
- Low Poly can make curves look angular. It does not guarantee an exact face count.

## What I would build next

I would make a separate Blender script with the same simple setup.

# Sketch Bloom — Week 09

Sketch Bloom is an in-app Python tool for Maya and Blender, with shared geometry code and separate interfaces. It is not a standalone drawing application.

What it does:

Draw tubes, curves, and filled outlines; create silhouette presets and hollow teacup parts; edit geometry; combine or boolean-union parts; subdivide copies; and export selected polygon meshes to OBJ. Maya retains the Week 8 studio interface. Blender supplies a sidebar with native mesh/curve editing. The shared geometry module has no Maya, Blender, Qt, or third-party dependencies.

## Install and launch from a fresh clone

Target environments: Maya 2024–2026 with its bundled Python and PySide2/PySide6, and Blender 4.2/4.3 with its bundled Python. These are **intended targets, not tested compatibility claims**. Test your exact host version before submission. No pip install is required. Ordinary Python 3.9+ can run the shared-code tests, but cannot launch either interface without its host application.

After publishing the repository, clone it:

```sh
git clone https://github.com/nyassin-cloud/pfa-week09.git
cd pfa-week09
```

Alternatively, download and extract the repository ZIP, then use that folder as the project root.

### Maya

1. Open Maya and a new scene. Open **Windows > General Editors > Script Editor** and choose a **Python** tab.
2. Paste the following, change the path to your actual clone folder, select the complete snippet, and execute it:

```python
from pathlib import Path
root = Path(r"C:\projects\pfa-week09")  # macOS/Linux: Path("/your/path/pfa-week09")
launcher = root / "launch_maya.py"
exec(compile(launcher.read_text(encoding="utf-8-sig"), str(launcher), "exec"),
     {"__name__": "__main__", "__file__": str(launcher)})
```

3. The Sketch Bloom window opens. Use **Draw**, choose a shape in the library, and click **Add shape**, or drag on the canvas. Click a drawing to edit its points. Use **Low Poly mode** to apply the generation preset to the active brush and selected Bloom drawing. It also sets the density of the next teacup.
4. Use the **Assemble Parts** tab to create a teacup. For a clear density comparison, disable **Fuse teacup body and handle**, create the cup, and select its parts to read their actual counts. Boolean union changes topology and counts.
5. To draw on a surface, capture a selected mesh using **Use selected surface**, choose Tube or Curve, and start drawing. Filled surface drawing is not supported.
6. **Retopology > Use Selected Object > Retopologize Copy** calls Maya's native retopology. The source is retained; the returned face count is measured, while the target is approximate. Availability and accepted options depend on Maya's installation.
7. Select polygon objects, then click **Export selected meshes OBJ**. Pick a writable location. Groups export their descendant meshes; curves require native conversion to polygons first.
8. Save the Maya scene to retain finished objects. Re-run the launcher to reopen the interface. Restart Maya after editing the Python source to avoid cached modules.

### Blender

1. Open Blender, switch to **Scripting**, and choose **Text > Open** in the Text Editor.
2. Open the saved `launch_blender.py` inside the clone. Click **Run Script**. Do not paste it into an unnamed text block: it uses the saved file path to locate its package.
3. Return to **Layout**. In the 3D Viewport, press **N**, then open the **Sketch Bloom** sidebar tab. Use **Object Mode** for creation and processing.
4. **Low Poly mode** starts enabled. Click **Create Teacup Parts**, or choose a shape and **Create Filled Preset**. Objects appear at the 3D cursor.
5. For freehand input, choose Tube, Filled, or Curve; click **Draw Stroke**, move into the viewport, drag the left mouse button, then release. Geometry appears on release; there is no live stroke preview. Esc/right-click cancels. Plane strokes use a camera-facing plane through the 3D cursor. Avoid changing views during a stroke.
6. For surface strokes, select the target mesh, enable **Draw on active mesh**, choose Tube or Curve, then draw. Leaving the surface cancels the stroke to avoid connecting across a missed ray. Sampling connects hits with straight edges, so tight curvature may still cause intersections.
7. Select the created object and press **Tab** for native Edit Mode point/vertex editing. Return to Object Mode before using Bloom actions. Curves are polygonal splines with no polygon faces.
8. Select two or more mesh parts for **Combine copies** or **Boolean union copies**. The result is selected; original parts are retained and hidden. Unhide them in the Outliner. Combine collects shells; union needs overlapping valid solids and may still leave disconnected shells.
9. **Decimate copy** reduces an existing mesh using an approximate retained fraction. It is **not quad retopology**. **Subdivide copy** increases density. Both leave the source present, so comparison copies overlap until you move or hide one.
10. Select meshes in Object Mode, click **Export Selected Meshes OBJ**, choose a writable path, and confirm. Export includes evaluated modifiers. Save the `.blend` file for geometry; rerun the launcher each Blender session to register the panel. This is a script integration, not a packaged installable Blender extension.

## Polygon controls and Low Poly mode

A **face** is one stored polygon; a quad or n-gon is still one face. Another application's triangulated count can be higher. Smooth shading changes appearance without reducing faces.

| Control | Meaning |
| --- | --- |
| Path samples | Rings along a tube; more rings follow bends more closely and add faces. |
| Tube sides | Vertices around each ring; more sides look rounder and add faces. |
| Depth/wall segments | Layers along filled walls or cup height; more layers add faces. |
| Subdivision | Adds faces; it is not a low-poly operation. |
| Maya “Aim for polygon count” | Approximate generation sampling/layer goal, not existing-mesh retopology. |
| Maya retopology target | Approximate desired quads for native retopology of an existing mesh copy. |
| Blender Decimate fraction | Approximate retained triangle fraction on an existing mesh copy; no guaranteed face target or quad layout. |

Maya **Low Poly mode** applies 16 path samples, 6 tube sides, 1 depth layer, 0 subdivision, n-gon tube caps, and disables the generation target override. The next cup uses 16 radial and 1 wall segment; its handle uses 16 samples and 6 sides. **Standard density** applies 96 samples, 12 tube sides, triangle tube caps, 1 depth layer, 0 subdivision, and cup settings of 96 radial/16 wall segments. These buttons set editable presets; manually changing settings afterward can raise density. Selecting another existing drawing loads that drawing's stored settings. Low Poly is not a persistent global clamp. Detailed filled outlines retain their boundary detail in Maya; reducing wall layers alone may not reduce a silhouette with already minimal walls.

Blender Low Poly uses 16 samples/6 tube sides and the same cup density preset; unchecked uses the editable tube settings and the standard cup. Filled outlines use a larger simplification tolerance in Low Poly; sharp corners are preserved where the algorithm requires them. Blender generation does not add subdivision automatically.

For the shared cup generator, code tests measured **172 total faces** in the low-density parts (body 80 + handle 92), versus **4,502** in standard parts (body 3,360 + handle 1,142), before union or other modifiers. These are Python geometry results, not a claim that either host was manually tested. Ordinary Maya brush tubes with triangle caps have a different cap count than n-gon-capped cup handles. The UI displays **actual selected Maya scene counts** and **Blender base/evaluated mesh counts**. Maya's canvas also shows a separately labeled subdivision estimate; the scene count is the measured result.

**Low-density generation starts with fewer faces. Retopology rebuilds an existing mesh's topology. Decimation reduces an existing mesh without promising a clean quad layout. These are separate operations.**

## Week 8 feature differences

| Feature | Maya Week 09 | Blender Week 09 |
| --- | --- | --- |
| Freehand tube/curve/fill | Original canvas and live viewport tools retained | Viewport modal stroke; result on release |
| Point editing | Original canvas handles and native Maya editing | Native Edit Mode vertices/spline points; no Bloom source-stroke regeneration |
| Shape library | Original categories and animal variants retained | Nine starter silhouettes; shared preset code |
| Surface drawing | Original captured surface tools | Active-mesh ray casting, Tube/Curve only |
| Teacup | Original configurable body/handle and optional fuse | Fixed-size starter at cursor, separate parts |
| Combine/fuse | Original copy-based combine/boolean with source retention | Copy-based join/boolean; sources hidden on success |
| Subdivision | Original copy tools and generation controls | One-level native subdivision on a copy |
| Existing mesh retopology | Maya native `polyRetopo`, subject to installation | Not implemented; decimation explicitly labeled separately |
| Undo/session | Original Maya/Qt behavior retained; must retest | Native undo for creation/actions; no custom canvas history |
| OBJ | Selected world-space polygon geometry | Selected evaluated world-space polygon geometry |

## OBJ scope

The exporter writes positions, polygon faces, and object names using a shared geometry-only writer. It uses Y-up coordinates and the hosts' numeric scene units; Blender's Z-up coordinates are converted at the integration boundary. OBJ has no reliable unit metadata. Match scale/up-axis in the receiving importer. Export does not include UVs, materials, textures, rigging, animation, curves, or explicit vertex normals. Recalculate normals in the receiving app if necessary. Meshes with mirrored transforms may need winding/normals repair. Export a small test before relying on a downstream pipeline.

## Peer run — A6

> I had my AI agent follow the README and it successfully installed the tool then ran it. I did not find any errors from testing the tool manually but I was confused about how high-poly the retopology was and wondered if there could be an implementation to offer a low-poly mode? Overall, it ran smoothly and nothing broke.

**What I fixed:** Added explicit Low Poly generation presets, reduced cup and handle sampling under those presets, added explanations for path/radial/wall/subdivision controls, and exposed actual scene mesh face counts. Corrected the canvas label from “Retopology target” to “Generation goal” for sampling-based density adjustment. Kept Maya's existing-mesh native retopology as an explicit copy action with an approximate target and measured result. Blender's existing-mesh reduction is a separate decimation action, not a claim of retopology. Added shared geometry and OBJ export with separate Maya/Blender integrations. These changes are implemented in code; host runtime validation remains outstanding. The quote is the actual Week 8 A6 feedback, not a new Week 9 test result.

## What does not work yet / limits

- Host runtime testing is outstanding. Neither complete interface has been run in Maya or Blender during project preparation; passing core tests cannot prove host compatibility or a fresh-clone launch.
- Blender does not reproduce Maya's complete studio UI, continuous preview, stored stroke regeneration, full library browser, or native quad retopology.
- Shared filled outlines reject self-crossing/degenerate contours and do not support holes. Maya retains its Qt winding-contour fallback, which has different behavior.
- Booleans depend on valid, intersecting solids; neither integration repairs arbitrary input or bridges gaps. A cup handle is not fused unless a union succeeds.
- Strong path bends can self-intersect. Low Poly can visibly facet curves or lose small details. It is not an exact polygon budget or production retopology solver.
- UVs, skinning, blend shapes, and animation are not transferred by retopology/export. Surface strokes are separate geometry, not automatically rigged.
- Maya's original UI and operations are preserved as code, not certified by new manual testing. Native command differences, Qt enum behavior, and undo interactions require testing in the chosen host version.

## Verification and remaining tests

From the repository root with ordinary Python:

```sh
python -m unittest discover -s tests -v
python -m compileall -q sketch_bloom launch_maya.py launch_blender.py
```

Project preparation ran **7 shared-code test methods successfully on Python 3.11**, covering density/count formulas, closed-edge incidence and winding, concave extrusion, crossing rejection, starter presets, invalid tube input, and OBJ face-index offsets. Source compilation also passed. These checks do not import either host integration into its real application.

Follow [the host test checklist](docs/TESTING.md) and record actual versions/results before claiming the project runs from a fresh clone. In particular, test both launchers, each drawing output, surface hits/misses, point editing, Low Poly comparisons, undo, union, native retopology availability, and OBJ reimport. Do not mark unperformed tests as passed.

## What I would build next

Add Blender live stroke preview and regenerable source-point editing; unify more preset and fill behavior; add an evaluated density budget before creation; implement an explicitly separate Blender quad-retopology workflow; preserve UVs/materials in richer export formats; and automate host smoke tests once target Maya/Blender versions are available.

## Demo recording and showcase

**Recording link: pending.** Record and upload a real 1–3 minute run, then replace this sentence with a Markdown link to the viewable video. Use [the approximately two-minute recording script](docs/DEMO_SCRIPT.md). The video should show the tool doing the chore, actual counts, a density comparison, and OBJ export/reimport. Only show successful operations you have tested.

For the Tuesday, November 3 showcase: use a fresh clone, share one application window, run the tool, and explain `tube()` in `sketch_bloom/geometry.py`. The walkthrough in the demo script explains how rings and face indices create the mesh.

## Submission and future updates

1. Complete host tests and record actual results in `docs/TESTING.md`.
2. The repository is [nyassin-cloud/pfa-week09](https://github.com/nyassin-cloud/pfa-week09).
3. For later changes, work from a clone and run:

```sh
git add .
git commit -m "Update Sketch Bloom Week 09"
git push origin main
```

4. Add the uploaded video link to this README, commit, and push the update.
5. Clone the published repository to a different folder and verify the README alone is sufficient. Submit the real repo link and linked video; do not submit a pending placeholder as a finished requirement.

## Folder structure

```text
pfa-week09/
  README.md
  .gitignore
  launch_maya.py
  launch_blender.py
  sketch_bloom/
    __init__.py
    geometry.py          # standard-library sampling, tubes, fills, cup, presets, OBJ
    maya_app.py          # retained studio + shared imports + density/export UI
    blender_app.py       # sidebar, modal drawing, native editing/processing
  reference/
    week08_maya_original.py
  tests/
    test_geometry.py
  docs/
    DEMO_SCRIPT.md
    TESTING.md
```

API references consulted: [Blender object ray casting](https://docs.blender.org/api/4.3/bpy.types.Object.html) and [Maya native polyRetopo](https://help.autodesk.com/cloudhelp/2026/ENU/Maya-Tech-Docs/CommandsPython/polyRetopo.html). These document host operations; they are not runtime test evidence. Ownership/license of the supplied Week 8 code is retained; no new license is assumed.

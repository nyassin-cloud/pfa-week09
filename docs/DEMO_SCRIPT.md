# Recording script — approximately 2 minutes

Record only after the relevant host checks pass. Share one application window. Keep a fresh clone ready before recording. This script uses Blender; Maya can demonstrate the same density/export chore with its documented controls.

- **0:00–0:20:** Show the fresh clone's saved `launch_blender.py` in Blender's Text Editor. Run it, then show the Sketch Bloom sidebar. Say: “Sketch Bloom turns a stroke or shape into mesh geometry. Week 9 separates shared geometry from Maya and Blender integrations.”
- **0:20–0:40:** With Low Poly checked, draw a Tube stroke and release. Select it and show the actual face count. Tab into Edit Mode, move one vertex or ring, then return to Object Mode. Say: “Path samples control rings along the stroke; sides control the ring's cross section.”
- **0:40–1:10:** Create a Low Poly teacup. Select its body: 80 faces before modifiers. Rename it if helpful and move the parts aside together. Uncheck Low Poly, create another cup, and select its body: 3,360 faces before modifiers. Say: “This is lower-density generation. I build fewer faces initially. It does not retopologize an existing object.” Show observed counts, not these expected counts if they differ.
- **1:10–1:35:** Select just the low-density cup parts. Export OBJ to a known folder. Use Blender's native OBJ importer to import the saved file, choosing the appropriate axis settings (Y-up file to Z-up Blender). Move or hide the originals so the imported result is visible. Say: “OBJ transfers polygon geometry; it does not carry the tool's UI, rigging, UVs, or materials.”
- **1:35–2:00:** Show `geometry.py` in the Text Editor at `tube()`. Say: “For each sampled path point, this function computes a tangent and two perpendicular directions. It places a ring of vertices around that point. Adjacent rings are connected with quads, then the ends are capped. With 16 samples and 6 sides, that is 15 times 6 plus 2 n-gon caps: 92 faces.”
- **2:00–2:15, optional:** Show **Decimate copy (not retopology)**. Explain that it reduces an existing mesh approximately. In Maya, show the separate native Retopologize Copy action only after testing it.

Keep the final recording between one and three minutes. Upload it to a location your instructor can view without requesting access. Add the actual Markdown link in the README and test the link in a signed-out browser.

# Five-minute showcase preparation

Reserve the extra time for launching from a fresh clone, explaining the function in your own words, and answering questions. Be ready to explain why samples and sides multiply, why smooth shading does not remove faces, why a boolean may change counts, and why Blender decimation is different from Maya native retopology. Do not describe an untested integration as verified.

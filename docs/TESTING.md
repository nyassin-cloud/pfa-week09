# Test record

## Completed during preparation

- Python 3.11: 7 shared-code unittest methods passed.
- All supplied Python files compiled successfully.
- Shared cup generation: low body/handle = 80/92 faces; standard = 3,360/1,142 faces.
- No Maya or Blender runtime was used. No video was recorded.

## Host tests to perform

Record version, OS, exact steps, observed result, and pass/fail. All items below are pending.

| Test | Maya | Blender |
| --- | --- | --- |
| Launch from fresh clone using only README | Pending | Pending |
| Re-run launcher without duplicate UI/errors | Pending | Pending |
| Tube, curve, filled stroke creation | Pending | Pending |
| Edit points and undo; unrelated objects retained | Pending | Pending |
| Presets including concave Heart/Star | Pending | Pending |
| Low/standard cup counts before union | Pending | Pending |
| Low Poly on current Bloom stroke / new stroke | Pending | New generation only; pending |
| Surface drawing on transformed mesh; miss/cancel | Pending | Pending |
| Filled surface mode rejected | Pending | Pending |
| Combine copies; sources retained | Pending | Pending |
| Union overlapping solids; failure handling | Pending | Pending |
| Existing mesh retopology target/result | Pending | Not implemented |
| Decimate copy leaves source unchanged | Not added | Pending |
| Subdivision copy increases density; source retained | Pending | Pending |
| Export one and multiple meshes with transforms | Pending | Pending |
| OBJ reimport: size, axes, normals, counts | Pending | Pending |
| Save/reopen scene and relaunch tool | Pending | Pending |
| Close/cancel operations; no stray preview geometry | Pending | Pending |

Check that OBJ exports exclude curves and include only intended meshes. For Blender, test modifiers and nonuniform transforms; for Maya, test selected groups. Compare polygon faces separately from triangulated importer counts. Capture any console traceback verbatim, fix the problem, and repeat that failed check.

## Submission checks

- [x] GitHub repository created: https://github.com/nyassin-cloud/pfa-week09
- [ ] A second clone follows README successfully.
- [ ] Exact app versions/results recorded above.
- [ ] Real 1–3 minute recording uploaded and permission-tested.
- [ ] Real repo and recording links replace README pending text.
- [ ] Final changes committed and pushed.

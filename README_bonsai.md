# MMX Visual Reconstruction

MMX spacecraft visual reconstruction from public reference imagery and 3D data.

## Scope

- Import an available STL model into Blender with `bpy`.
- Convert/export the model to GLB for browser viewing.
- Provide a small Three.js viewer with orbit, zoom, and reset controls.
- Compare renders against official MMX reference imagery and document uncertainty.

## Out of scope

BOM and procurement, physical assembly, 3D-print tolerances, electronics, spacecraft operation or dynamics simulation, and fiction-writing features.

## Quick start

1. Put a legally usable source model in `models/source.stl` (large/source assets may stay local and be documented rather than committed).
2. Run Blender with `blender/import_mmx.py` to import and save a `.blend` file.
3. Export a browser asset to `web/models/mmx.glb`.
4. Serve the repository root over HTTP and open `web/index.html`.

See `docs/ASSETS.md` for source and licensing notes.

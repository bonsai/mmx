"""Import an MMX STL into Blender and export a browser-ready GLB.

Run from the repository root:
  blender --background --python blender/import_mmx.py

Place the source model at models/source.stl. Generated assets are ignored by git.
Tested API target: Blender 4.0+; Blender operator names can vary by version.
"""
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
STL_PATH = ROOT / "models" / "source.stl"
BLEND_PATH = ROOT / "models" / "mmx.blend"
GLB_PATH = ROOT / "web" / "models" / "mmx.glb"

if not STL_PATH.exists():
    raise FileNotFoundError(
        f"Missing {STL_PATH}. Place the source STL there, "
        "or update STL_PATH in this script."
    )

# Start with an empty scene for repeatable imports.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Blender 4.0+ provides wm.stl_import. Older versions may use import_mesh.stl.
if hasattr(bpy.ops.wm, "stl_import"):
    bpy.ops.wm.stl_import(filepath=str(STL_PATH))
elif hasattr(bpy.ops.import_mesh, "stl"):
    bpy.ops.import_mesh.stl(filepath=str(STL_PATH))
else:
    raise RuntimeError("This Blender build has no STL import operator.")

meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
if not meshes:
    raise RuntimeError("The STL import did not create any mesh objects.")

# Neutral preview material; replace/tune it against reference imagery.
material = bpy.data.materials.get("MMX_Neutral")
if material is None:
    material = bpy.data.materials.new("MMX_Neutral")
material.diffuse_color = (0.58, 0.63, 0.70, 1.0)

for obj in meshes:
    if not obj.data.materials:
        obj.data.materials.append(material)

# Keep source mesh geometry unchanged; avoid automatic scaling without known units.
GLB_PATH.parent.mkdir(parents=True, exist_ok=True)
BLEND_PATH.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(
    filepath=str(GLB_PATH),
    export_format="GLB",
    use_selection=False,
)

print(f"Imported {len(meshes)} mesh object(s)")
print(f"Saved Blender project: {BLEND_PATH}")
print(f"Exported browser model: {GLB_PATH}")

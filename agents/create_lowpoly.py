import bpy, os, struct, bmesh
from mathutils import Vector

# Load the combined assembly scene
blend_file = "C:/Users/0501JP/mmx/MMX_assembly_clean.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

# Select all mesh objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
    else:
        obj.select_set(False)

bpy.context.view_layer.objects.active = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Join all into one mesh
bpy.ops.object.join()

# Now we have one combined object
obj = bpy.context.active_object
obj.name = "MMX_Combined"

print(f"Combined mesh: {len(obj.data.vertices)} vertices, {len(obj.data.polygons)} faces")

# Apply Decimate modifier for low-poly
target_ratio = 0.05  # 5% of original = low poly

decimate = obj.modifiers.new(name="Decimate", type='DECIMATE')
decimate.ratio = target_ratio
decimate.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier="Decimate")

print(f"After decimate: {len(obj.data.vertices)} vertices, {len(obj.data.polygons)} faces")

# Recalculate normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Add neutral material (like bonsai script)
material = bpy.data.materials.get("MMX_Neutral")
if material is None:
    material = bpy.data.materials.new("MMX_Neutral")
material.use_nodes = True
nodes = material.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.58, 0.63, 0.70, 1.0)
    bsdf.inputs['Metallic'].default_value = 0.1
    bsdf.inputs['Roughness'].default_value = 0.5

if not obj.data.materials:
    obj.data.materials.append(material)

# Create lowpoly collection and move
lowpoly_collection = bpy.data.collections.new("LowPoly")
bpy.context.scene.collection.children.link(lowpoly_collection)
bpy.context.scene.collection.objects.unlink(obj)
lowpoly_collection.objects.link(obj)

# Set origin to geometry center
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Save
output_blend = "C:/Users/0501JP/mmx/models/mmx_lowpoly.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_blend)
print(f"Saved lowpoly blend: {output_blend}")

# Export GLB
glb_path = "C:/Users/0501JP/mmx/web/models/mmx_lowpoly.glb"
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(
    filepath=glb_path,
    export_format='GLB',
    use_selection=False,
)
print(f"Exported GLB: {glb_path}")


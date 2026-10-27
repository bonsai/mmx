import bpy, os, json, math
from mathutils import Vector, Euler

# Load color config
with open("C:/Users/0501JP/mmx/mmx_colors.json", "r") as f:
    config = json.load(f)

# Load ORIGINAL assembly (not joined)
blend_file = "C:/Users/0501JP/mmx/MMX_assembly_clean.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

# Apply materials to each separate object
for part_config in config['parts']:
    name = part_config['name']
    obj = bpy.data.objects.get(name)
    if not obj:
        print(f"Object not found: {name}")
        continue
    
    mat_name = f"Mat_{name}"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(mat_name)
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (*part_config['color'], 1.0)
    bsdf.inputs['Metallic'].default_value = part_config['metallic']
    bsdf.inputs['Roughness'].default_value = part_config['roughness']
    
    if part_config['emissive_strength'] > 0:
        bsdf.inputs['Emission Color'].default_value = (*part_config['emissive'], 1.0)
        bsdf.inputs['Emission Strength'].default_value = part_config['emissive_strength']
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    print(f"Applied material to {name}: {part_config['color']}")

# Save colored assembly
colored_blend = "C:/Users/0501JP/mmx/models/mmx_colored_assembly.blend"
bpy.ops.wm.save_as_mainfile(filepath=colored_blend)
print(f"Saved colored assembly: {colored_blend}")

# Now create low-poly version preserving materials
# Join all, decimate, keep material slots
bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active = [o for o in bpy.context.selected_objects if o.type == 'MESH'][0]
bpy.ops.object.join()

mmx_obj = bpy.context.active_object
mmx_obj.name = "MMX_Colored"

# Decimate
decimate = mmx_obj.modifiers.new(name="Decimate", type='DECIMATE')
decimate.ratio = 0.05
decimate.use_collapse_triangulate = True
bpy.ops.object.modifier_apply(modifier="Decimate")

print(f"Decimated: {len(mmx_obj.data.vertices)} verts, {len(mmx_obj.data.polygons)} faces, {len(mmx_obj.data.materials)} materials")

# Save low-poly colored
colored_lowpoly = "C:/Users/0501JP/mmx/models/mmx_colored_lowpoly.blend"
bpy.ops.wm.save_as_mainfile(filepath=colored_lowpoly)
print(f"Saved colored low-poly: {colored_lowpoly}")

import bpy

# Load colored assembly
bpy.ops.wm.open_mainfile(filepath="C:/Users/0501JP/mmx/models/mmx_colored_assembly.blend")

print("Objects in scene:")
for obj in bpy.data.objects:
    print(f"  {obj.name}: type={obj.type}")

# Select all meshes
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        obj.select_set(True)
    else:
        obj.select_set(False)

meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']
print(f"Mesh objects to join: {len(meshes)}")
for m in meshes:
    print(f"  {m.name}")

if meshes:
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    
    mmx_obj = bpy.context.active_object
    mmx_obj.name = "MMX_Colored"
    
    print(f"Before decimate: {len(mmx_obj.data.vertices)} verts, {len(mmx_obj.data.polygons)} faces, {len(mmx_obj.data.materials)} materials")
    
    # Decimate
    decimate = mmx_obj.modifiers.new(name="Decimate", type='DECIMATE')
    decimate.ratio = 0.05
    decimate.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier="Decimate")
    
    print(f"After decimate: {len(mmx_obj.data.vertices)} verts, {len(mmx_obj.data.polygons)} faces, {len(mmx_obj.data.materials)} materials")
    
    colored_lowpoly = "C:/Users/0501JP/mmx/models/mmx_colored_lowpoly.blend"
    bpy.ops.wm.save_as_mainfile(filepath=colored_lowpoly)
    print(f"Saved colored low-poly: {colored_lowpoly}")

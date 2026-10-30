import bpy

# Load colored assembly
bpy.ops.wm.open_mainfile(filepath="C:/Users/0501JP/mmx/models/mmx_colored_assembly.blend")

# Join and decimate
bpy.ops.object.select_all(action='SELECT')
meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']
if meshes:
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    
    mmx_obj = bpy.context.active_object
    mmx_obj.name = "MMX_Colored"
    
    # Decimate
    decimate = mmx_obj.modifiers.new(name="Decimate", type='DECIMATE')
    decimate.ratio = 0.05
    decimate.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier="Decimate")
    
    print(f"Decimated: {len(mmx_obj.data.vertices)} verts, {len(mmx_obj.data.polygons)} faces, {len(mmx_obj.data.materials)} materials")
    
    colored_lowpoly = "C:/Users/0501JP/mmx/models/mmx_colored_lowpoly.blend"
    bpy.ops.wm.save_as_mainfile(filepath=colored_lowpoly)
    print(f"Saved colored low-poly: {colored_lowpoly}")

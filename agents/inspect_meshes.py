import bpy, os

# Load the blend file
blend_file = "C:/Users/0501JP/mmx/MMX_assembly.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

# Get all objects
objects = bpy.data.objects

for obj in objects:
    if obj.type == 'MESH':
        mesh = obj.data
        print(f"{obj.name}: {len(mesh.vertices)} verts, {len(mesh.polygons)} faces")
        
        # Check for non-manifold edges
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_non_manifold()
        
        # Count selected (non-manifold) verts/edges
        import bmesh
        bm = bmesh.from_mesh(mesh)
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        non_manifold_verts = sum(1 for v in bm.verts if v.select)
        print(f"  Non-manifold vertices: {non_manifold_verts}")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bm.free()


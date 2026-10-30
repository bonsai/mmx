import bpy, os, mathutils

# Load the blend file
blend_file = "C:/Users/0501JP/mmx/MMX_assembly.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

# Set render engine to Cycles for proper repair visualization
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# Create collection for repaired objects
repaired_collection = bpy.data.collections.new("Repaired")
bpy.context.scene.collection.children.link(repaired_collection)

# Function to find non-manifold edges
def find_non_manifold_edges(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()
    
    # Count non-manifold edges
    bm = bmesh.from_edit_mesh(obj.data)
    non_manifold_edges = [e for e in bm.edges if e.select]
    bpy.ops.object.mode_set(mode='OBJECT')
    return len(non_manifold_edges), len(bm.edges)

# Find and repair problematic objects
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
        
    print(f"\nAnalyzing {obj.name}: {len(obj.data.vertices)} vertices, {len(obj.data.polygons)} faces")
    
    # Check for non-manifold geometry
    non_manifold_count, total_edges = find_non_manifold_edges(obj)
    if non_manifold_count > 0:
        print(f"  Found {non_manifold_count} non-manifold edges out of {total_edges} total")
        
        # Create a copy for repair
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.name = f"Repaired_{obj.name}"
        repaired_collection.objects.link(new_obj)
        
        # Focus on non-manifold edges
        bpy.context.view_layer.objects.active = new_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(new_obj.data)
        bm.edges.ensure_lookup_table()
        
        # Select and fill holes
        bpy.ops.mesh.select_non_manifold()
        if bpy.context.selected_objects:
            bpy.ops.mesh.fill_holes()
            
        # Recalculate normals
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        print(f"  Repaired: {new_obj.name}")

print("\nRepair process completed!")

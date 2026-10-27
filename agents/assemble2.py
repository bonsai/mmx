import bpy, os
from pathlib import Path

stl_files = [
    "1_PAF(stand).stl",
    "2_PropM(Lower).stl", 
    "3_PropM(Upper).stl",
    "4_ReturnM(Lower).stl",
    "5_RetunM(Upper).stl",
    "6_ExplorationM.stl",
    "7_LandingLeg(normal).stl",
    "8_LandingLeg(P-SMP).stl",
    "9_SolarPaddle.stl",
    "10_Miscellaneous.stl"
]

# Clear all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Import each STL using bmesh
for i, filename in enumerate(stl_files):
    filepath = os.path.join("C:/Users/0501JP/mmx/STL_data", filename)
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        continue
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Check format
    if data[:5] == b'solid':
        print(f"ASCII STL: {filename}")
    else:
        # Binary STL - read facet count from header (bytes 80-82)
        facet_count = int.from_bytes(data[80:82], 'little')
        print(f"Binary STL: {filename} - {facet_count} facets")
    
    # Import using bmesh
    bm = bmesh.new()
    from mathutils import Vector
    
    # Parse binary STL
    if data[:5] != b'solid':
        normal_index = 0
        facet_count_raw = int.from_bytes(data[80:82], 'little')
        
        for f_idx in range(facet_count_raw):
            if normal_index + 50 > len(data):
                break
            # Read normal vector (3 floats = 12 bytes)
            normal = struct.unpack_from('<fff', data, normal_index)
            nx, ny, nz = normal
            
            # Read vertex count (2 bytes)
            vertex_count = struct.unpack_from('<H', data, normal_index + 12)[0]
            
            # Skip 2 bytes (attribute byte count)
            vertex_data_start = normal_index + 14
            
            # Read vertices
            for v_idx in range(vertex_count):
                if vertex_data_start + 12 > len(data) - 2:
                    break
                vx, vy, vz = struct.unpack_from('<fff', data, vertex_data_start)
                vertex = Vector((vx, vy, vz))
                bm.verts.new(vertex)
                vertex_data_start += 12
            
            # Read triangle indices (3 * 2 bytes)
            # We need to reconstruct triangles
            # Skip attribute byte count (2 bytes)
            # Actually let's just use the binary format properly
            
            normal_index = vertex_data_start
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(f"{filename}_mesh")
    bm.to_mesh(mesh)
    obj = bpy.data.objects.new(filename, mesh)
    bpy.context.collection.objects.link(obj)
    print(f"  Created object with {len(bm.verts)} verts, {len(bm.faces)} faces")
    bm.free()

print("\nAssembly complete!")

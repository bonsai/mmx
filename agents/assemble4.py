import bpy, os, struct, bmesh
from mathutils import Vector

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

def parse_binary_stl(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    facets = []
    offset = 80
    facet_count = struct.unpack_from('<I', data, offset)[0]
    offset += 4
    
    for i in range(facet_count):
        if offset + 50 > len(data):
            break
        normal = struct.unpack_from('<fff', data, offset)
        v1 = struct.unpack_from('<fff', data, offset + 12)
        v2 = struct.unpack_from('<fff', data, offset + 24)
        v3 = struct.unpack_from('<fff', data, offset + 36)
        offset += 50
        facets.append((normal, [v1, v2, v3]))
    return facets

def parse_ascii_stl(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    facets = []
    normal = None
    vertices = []
    
    for line in lines:
        line = line.strip()
        if line.startswith('facet normal'):
            normal = tuple(map(float, line.split()[2:5]))
            vertices = []
        elif line.startswith('vertex'):
            vertices.append(tuple(map(float, line.split()[1:4])))
        elif line.startswith('endloop'):
            if len(vertices) == 3:
                facets.append((normal, vertices))
    return facets

for filename in stl_files:
    filepath = os.path.join("C:/Users/0501JP/mmx/STL_data", filename)
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found")
        continue
    
    with open(filepath, 'rb') as f:
        data = f.read()
    
    is_ascii = data[:5] == b'solid'
    
    if is_ascii:
        facets = parse_ascii_stl(filepath)
    else:
        facets = parse_binary_stl(filepath)
    
    print(f"Importing {filename}: {len(facets)} facets")
    
    mesh = bpy.data.meshes.new(filename)
    bm = bmesh.new()
    
    vert_map = {}
    for normal, verts in facets:
        face_verts = []
        for v in verts:
            # Use frozen vector as key
            key = (v[0], v[1], v[2])
            if key not in vert_map:
                vert_map[key] = bm.verts.new(Vector(v))
            face_verts.append(vert_map[key])
        
        if len(face_verts) == 3:
            try:
                bm.faces.new(face_verts)
            except:
                pass
    
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(filename, mesh)
    bpy.context.collection.objects.link(obj)
    print(f"  Created object with {len(mesh.vertices)} verts, {len(mesh.polygons)} faces")

# Camera setup
bpy.context.scene.camera.location = (0, -10, 5)
bpy.context.scene.camera.rotation_euler = (1.0, 0, 0)

bpy.context.scene.render.engine = 'CYCLES'

print("\nAssembly complete!")

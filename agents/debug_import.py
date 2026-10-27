import bpy, os, json, struct, bmesh
from mathutils import Vector

# Load color config
with open("C:/Users/0501JP/mmx/mmx_colors.json", "r") as f:
    config = json.load(f)

stl_files = [
    ("1_PAF(stand).stl", "PAF_Stand"),
    ("2_PropM(Lower).stl", "Propulsion_Lower"),
]

# Clear all
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
        if offset + 50 > len(data): break
        normal = struct.unpack_from('<fff', data, offset)
        v1 = struct.unpack_from('<fff', data, offset + 12)
        v2 = struct.unpack_from('<fff', data, offset + 24)
        v3 = struct.unpack_from('<fff', data, offset + 36)
        offset += 50
        facets.append((normal, [v1, v2, v3]))
    return facets

objects = []
for filename, clean_name in stl_files:
    filepath = os.path.join("C:/Users/0501JP/mmx/STL_data", filename)
    print(f"Checking {filepath}: exists={os.path.exists(filepath)}")
    if not os.path.exists(filepath): continue
    
    with open(filepath, 'rb') as f:
        data = f.read()
    is_ascii = data[:5] == b'solid'
    facets = parse_binary_stl(filepath)
    print(f"  Facets: {len(facets)}")
    
    mesh = bpy.data.meshes.new(clean_name)
    bm = bmesh.new()
    vert_map = {}
    for normal, verts in facets:
        face_verts = []
        for v in verts:
            key = (round(v[0], 6), round(v[1], 6), round(v[2], 6))
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
    
    obj = bpy.data.objects.new(clean_name, mesh)
    bpy.context.collection.objects.link(obj)
    objects.append(obj)
    print(f"  Created object: {obj.name}")

print(f"Total objects: {len(objects)}")
for o in objects:
    print(f"  {o.name}")

assembly_blend = "C:/Users/0501JP/mmx/models/test_import.blend"
bpy.ops.wm.save_as_mainfile(filepath=assembly_blend)

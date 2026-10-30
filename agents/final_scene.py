import bpy, os, struct, bmesh
from mathutils import Vector

stl_files = [
    ("1_PAF(stand).stl", "PAF_Stand"),
    ("2_PropM(Lower).stl", "Propulsion_Lower"),
    ("3_PropM(Upper).stl", "Propulsion_Upper"),
    ("4_ReturnM(Lower).stl", "Return_Lower"),
    ("5_RetunM(Upper).stl", "Return_Upper"),
    ("6_ExplorationM.stl", "Exploration"),
    ("7_LandingLeg(normal).stl", "LandingLeg_Normal"),
    ("8_LandingLeg(P-SMP).stl", "LandingLeg_PSMP"),
    ("9_SolarPaddle.stl", "SolarPaddle"),
    ("10_Miscellaneous.stl", "Miscellaneous")
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

# Import all STLs with clean names
for filename, clean_name in stl_files:
    filepath = os.path.join("C:/Users/0501JP/mmx/STL_data", filename)
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'rb') as f:
        data = f.read()
    is_ascii = data[:5] == b'solid'
    facets = parse_ascii_stl(filepath) if is_ascii else parse_binary_stl(filepath)
    print(f"Importing {clean_name}: {len(facets)} facets")
    
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

# Create camera
cam_data = bpy.data.cameras.new('Camera')
cam_obj = bpy.data.objects.new('Camera', cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (0, -12, 8)
cam_obj.rotation_euler = (1.1, 0, 0)

# Set world background to white
world = bpy.data.worlds.new("World")
world["use_nodes"] = True
bpy.context.scene.world = world
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs[0].default_value = (1, 1, 1, 1)

# Add sun light for better rendering
light_data = bpy.data.lights.new(name='Sun', type='SUN')
light_obj = bpy.data.objects.new('Sun', light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.rotation_euler = (0.5, 0.3, 0)
light_data.energy = 5.0

# Set render engine
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# Save blend file
output_path = "C:/Users/0501JP/mmx/MMX_assembly_clean.blend"
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"\nSaved to {output_path}")


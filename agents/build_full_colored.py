import bpy, os, json, struct, bmesh, math
from mathutils import Vector, Euler

# Load color config
with open("C:/Users/0501JP/mmx/mmx_colors.json", "r") as f:
    config = json.load(f)

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

# Import each STL with its material - KEEP OBJECTS SEPARATE
objects = []
for filename, clean_name in stl_files:
    filepath = os.path.join("C:/Users/0501JP/mmx/STL_data", filename)
    if not os.path.exists(filepath): continue
    
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
    objects.append(obj)
    
    # Apply material from config
    part_config = next((p for p in config['parts'] if p['name'] == clean_name), None)
    if part_config:
        mat_name = f"Mat_{clean_name}"
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        for n in list(nodes): nodes.remove(n)
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (*part_config['color'], 1.0)
        bsdf.inputs['Metallic'].default_value = part_config['metallic']
        bsdf.inputs['Roughness'].default_value = part_config['roughness']
        if part_config['emissive_strength'] > 0:
            bsdf.inputs['Emission Color'].default_value = (*part_config['emissive'], 1.0)
            bsdf.inputs['Emission Strength'].default_value = part_config['emissive_strength']
        output = nodes.new('ShaderNodeOutputMaterial')
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

# Save assembly with separate objects
assembly_blend = "C:/Users/0501JP/mmx/models/mmx_colored_assembly.blend"
bpy.ops.wm.save_as_mainfile(filepath=assembly_blend)
print(f"Saved colored assembly: {assembly_blend}")

# NOW join and decimate for low-poly
for obj in objects:
    obj.select_set(True)

bpy.context.view_layer.objects.active = objects[0]
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

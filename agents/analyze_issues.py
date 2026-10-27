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

# Load and analyze each STL
issues_report = []

for filename, clean_name in stl_files:
    filepath = os.path.join("C:/Users/0501JP/mmx/STL_data", filename)
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'rb') as f:
        data = f.read()
    is_ascii = data[:5] == b'solid'
    facets = parse_ascii_stl(filepath) if is_ascii else parse_binary_stl(filepath)
    
    # Build mesh for analysis
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
    
    # Analyze issues
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    # Non-manifold edges
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()
    bm_edit = bmesh.from_edit_mesh(mesh)
    non_manifold_edges = [e for e in bm_edit.edges if e.select]
    
    # Duplicate vertices
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bm_edit2 = bmesh.from_edit_mesh(mesh)
    duplicate_verts = len(bm_edit2.verts) - len(vert_map)
    
    # Zero-area faces
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')  # triangles only
    # Check for degenerate faces
    bm_edit3 = bmesh.from_edit_mesh(mesh)
    degenerate_faces = [f for f in bm_edit3.faces if f.calc_area() < 1e-6]
    
    # Connected components
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Count loose parts
    loose_parts = len([o for o in bpy.context.selected_objects if o.type == 'MESH'])
    
    issues_report.append({
        'name': clean_name,
        'facets': len(facets),
        'vertices': len(mesh.vertices),
        'non_manifold_edges': len(non_manifold_edges),
        'duplicate_verts_removed': duplicate_verts,
        'degenerate_faces': len(degenerate_faces),
        'loose_parts': loose_parts
    })
    
    print(f"\n{clean_name}:")
    print(f"  Facets: {len(facets)}")
    print(f"  Vertices: {len(mesh.vertices)}")
    print(f"  Non-manifold edges: {len(non_manifold_edges)}")
    print(f"  Duplicate vertices (removed): {duplicate_verts}")
    print(f"  Degenerate faces: {len(degenerate_faces)}")
    print(f"  Loose parts: {loose_parts}")

# Summary
print("\n" + "="*60)
print("MMX SPACECRAFT STL ISSUE REPORT")
print("="*60)
total_facets = sum(r['facets'] for r in issues_report)
total_verts = sum(r['vertices'] for r in issues_report)
total_nm = sum(r['non_manifold_edges'] for r in issues_report)
total_dup = sum(r['duplicate_verts_removed'] for r in issues_report)
total_deg = sum(r['degenerate_faces'] for r in issues_report)

print(f"\nTotal parts: {len(issues_report)}")
print(f"Total facets: {total_facets:,}")
print(f"Total vertices: {total_verts:,}")
print(f"Total non-manifold edges: {total_nm:,}")
print(f"Total duplicate vertices: {total_dup:,}")
print(f"Total degenerate faces: {total_deg:,}")

# Individual issues
print("\n--- PARTS WITH ISSUES ---")
for r in issues_report:
    issues = []
    if r['non_manifold_edges'] > 0: issues.append(f"non-manifold edges: {r['non_manifold_edges']}")
    if r['duplicate_verts_removed'] > 0: issues.append(f"duplicate verts: {r['duplicate_verts_removed']}")
    if r['degenerate_faces'] > 0: issues.append(f"degenerate faces: {r['degenerate_faces']}")
    if r['loose_parts'] > 1: issues.append(f"loose parts: {r['loose_parts']}")
    if issues:
        print(f"  {r['name']}: {', '.join(issues)}")
    else:
        print(f"  {r['name']}: OK")


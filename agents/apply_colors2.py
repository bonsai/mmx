import bpy, os, json, math
from mathutils import Vector, Euler

# Load color config from JSON
with open("C:/Users/0501JP/mmx/mmx_colors.json", "r") as f:
    config = json.load(f)

# Load low-poly scene
blend_file = "C:/Users/0501JP/mmx/models/mmx_lowpoly.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

# Create material for each part based on config
for part_config in config['parts']:
    name = part_config['name']
    obj = bpy.data.objects.get(name)
    if not obj:
        print(f"Object not found: {name}")
        continue
    
    mat_name = f"Mat_{name}"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(mat_name)
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    for n in list(nodes):
        nodes.remove(n)
    
    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (*part_config['color'], 1.0)
    bsdf.inputs['Metallic'].default_value = part_config['metallic']
    bsdf.inputs['Roughness'].default_value = part_config['roughness']
    
    # Emission if specified
    if part_config['emissive_strength'] > 0:
        bsdf.inputs['Emission Color'].default_value = (*part_config['emissive'], 1.0)
        bsdf.inputs['Emission Strength'].default_value = part_config['emissive_strength']
    
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Assign to object
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    print(f"Applied material to {name}: {part_config['color']}")

# Update world with global settings
world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("SpaceWorld")
    bpy.context.scene.world = world

world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
for n in list(nodes):
    nodes.remove(n)

bg = nodes.new('ShaderNodeBackground')
bg.location = (0, 0)
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-600, 0)
noise = nodes.new('ShaderNodeTexNoise')
noise.location = (-400, 0)
noise.inputs['Scale'].default_value = 200
noise.inputs['Detail'].default_value = 8
noise.inputs['Roughness'].default_value = 0.7
color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.location = (-200, 0)
color_ramp.color_ramp.elements[0].position = 0.95
color_ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
color_ramp.color_ramp.elements[1].position = 0.98
color_ramp.color_ramp.elements[1].color = (1, 1, 0.9, 1)
mix = nodes.new('ShaderNodeMixRGB')
mix.location = (0, -200)
mix.blend_type = 'MIX'
mix.inputs['Fac'].default_value = 1.0
mix.inputs[1].default_value = (0.01, 0.01, 0.02, 1.0)
mix.inputs[2].default_value = (1, 1, 0.9, 1)
output = nodes.new('ShaderNodeOutputWorld')
output.location = (200, 0)
links.new(tex_coord.outputs['Generated'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], mix.inputs['Color2'])
links.new(mix.outputs['Color'], bg.inputs['Color'])
links.new(bg.outputs['Background'], output.inputs['Surface'])
bg.inputs['Strength'].default_value = 0.15

# Sun light
g = config['global']
sun_data = bpy.data.lights.new('Sun', 'SUN')
sun_obj = bpy.data.objects.new('Sun', sun_data)
bpy.context.scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = Euler((math.radians(45), math.radians(30), 0), 'XYZ')
sun_data.energy = g['sun_energy']
sun_data.color = g['sun_color']
sun_data.angle = 0.53

# Fill light
fill_data = bpy.data.lights.new('Fill', 'SUN')
fill_obj = bpy.data.objects.new('Fill', fill_data)
bpy.context.scene.collection.objects.link(fill_obj)
fill_obj.rotation_euler = Euler((math.radians(-45), math.radians(-30), 0), 'XYZ')
fill_data.energy = g['sun_energy'] * 0.15
fill_data.color = g['ambient_color']

# Save colored scene
colored_blend = "C:/Users/0501JP/mmx/models/mmx_colored.blend"
bpy.ops.wm.save_as_mainfile(filepath=colored_blend)
print(f"Saved colored scene: {colored_blend}")

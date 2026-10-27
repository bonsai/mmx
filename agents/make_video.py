import bpy
import os

# Create video from PNG sequence
scene = bpy.context.scene
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 450
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.filepath = "C:/Users/0501JP/mmx/MMX_space_flight_15sec.mp4"

# Add sequence editor strip
seq = scene.sequence_editor_create()
strip = seq.sequences.new_movie(
    name="Frames",
    filepath="C:/Users/0501JP/mmx/renders/frame_0001.png",
    channel=1,
    frame_start=1
)
strip.frame_final_end = 450

bpy.ops.render.render(animation=True)
print("Video created!")

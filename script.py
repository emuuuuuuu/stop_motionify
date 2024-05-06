import bpy

# Overall strength of the effect
STRENGTH = 1.5

# Treshold for the effect to take place for the whole body
THRESHOLD = 0.01

# Seperate treshold for hands and arms to avoid extreme jittering of the hands
HAND_ARM_THRESHOLD = 0.005

def clean_selected_bones_animation(bone_name, threshold):
    armature = bpy.context.active_object
    if not armature or armature.type != 'ARMATURE' or not armature.animation_data or not armature.animation_data.action:
        return
    action = armature.animation_data.action
    bone = armature.pose.bones.get(bone_name)
    if not bone:
        return
    for fcurve in action.fcurves:
        if fcurve.data_path.split('["')[1].split('"]')[0] == bone_name:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'LINEAR'
            prev_value = fcurve.keyframe_points[0].co[1]
            for keyframe in fcurve.keyframe_points[1:]:
                current_value = keyframe.co[1]
                if abs(current_value - prev_value) < threshold:
                    keyframe.co[1] = prev_value
                else:
                    prev_value = current_value

# Get the selected armature
selected_armature = bpy.context.active_object

# Define bone patterns
bone_patterns = ['Hips', 'Leg', 'Foot', 'Toe']

# Ensure the selected object is an armature
if selected_armature and selected_armature.type == 'ARMATURE':
    for action in bpy.data.actions:
        fcurves = [fc for fc in action.fcurves if fc.data_path.startswith("pose.bones")]
        for fcurve in fcurves:
            bone_name = fcurve.data_path.split('"')[1]
            if any(pattern in bone_name for pattern in bone_patterns):
                keyframe_points = fcurve.keyframe_points[:]
                for i in range(len(keyframe_points) - 1, -1, -1):
                    if i % 2 == 0:
                        fcurve.keyframe_points.remove(keyframe_points[i])
                for kf in fcurve.keyframe_points:
                    kf.interpolation = 'QUAD'
            elif 'Hand' or 'Arm' in bone_name:
                clean_selected_bones_animation(bone_name, HAND_ARM_THRESHOLD * STRENGTH)
            else:
                clean_selected_bones_animation(bone_name, THRESHOLD * STRENGTH)

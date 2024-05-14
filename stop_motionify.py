bl_info = {
    "name": "Stop Motionify",
    "blender": (2, 80, 0),
    "category": "Animation",
}

import bpy

class StopMotionifyProperties(bpy.types.PropertyGroup):
    strength: bpy.props.FloatProperty(
        name="Strength",
        description="Overall strength of the effect",
        default=1.5,
        min=0,
        max=10.0
    )

class OBJECT_OT_clean_armature_animation(bpy.types.Operator):
    """Clean Armature Animation"""
    bl_idname = "object.clean_armature_animation"
    bl_label = "Apply"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and not obj.get('stop_motionify_applied', False)

    def execute(self, context):
        armature = context.active_object
        if armature and armature.type == 'ARMATURE':
            self.clean_animation(context, armature)
            armature['stop_motionify_applied'] = True  # Use a custom property to track application
            return {'FINISHED'}
        return {'CANCELLED'}

    def clean_animation(self, context, armature):
        THRESHOLD = 0.01
        HAND_ARM_THRESHOLD = 0.005
        strength = context.scene.stop_motionify_settings.strength

        # Get the currently selected armature object
        selected_armature = context.view_layer.objects.active
        if selected_armature is None or selected_armature.type != 'ARMATURE':
            print("No armature selected")
            return

        # Iterate over actions linked to the selected armature
        for action in bpy.data.actions:
            # Check if the action is used by the selected armature
            if selected_armature.animation_data is not None and selected_armature.animation_data.action == action:
                fcurves = [fc for fc in action.fcurves if fc.data_path.startswith("pose.bones")]
                for fcurve in fcurves:
                    bone_name = fcurve.data_path.split('"')[1]
                    bone_patterns = ['Hips', 'Leg', 'Foot', 'Toe']
                    if any(pattern in bone_name for pattern in bone_patterns):
                        keyframe_points = fcurve.keyframe_points[:]
                        for i in range(len(keyframe_points) - 1, -1, -1):
                            if i % 2 == 0:
                                fcurve.keyframe_points.remove(keyframe_points[i])
                        for kf in fcurve.keyframe_points:
                            kf.interpolation = 'QUAD'
                    elif 'Hand' in bone_name or 'Arm' in bone_name:
                        self.clean_selected_bones_animation(armature, bone_name, HAND_ARM_THRESHOLD * strength)
                    else:
                        self.clean_selected_bones_animation(armature, bone_name, THRESHOLD * strength)


    def clean_selected_bones_animation(self, armature, bone_name, threshold):
        action = armature.animation_data.action
        bone = armature.pose.bones.get(bone_name)
        if not bone:
            return
        for fcurve in action.fcurves:
            if fcurve.data_path.endswith(bone_name):
                prev_value = fcurve.keyframe_points[0].co[1]
                for keyframe in fcurve.keyframe_points[1:]:
                    current_value = keyframe.co[1]
                    if abs(current_value - prev_value) < threshold:
                        keyframe.co[1] = prev_value
                    else:
                        prev_value = current_value

class STOP_MOTIONIFY_PT_armature_panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Stop Motionify"
    bl_idname = "OBJECT_PT_stop_motionify_armature"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Stop Motionify'

    def draw(self, context):
        layout = self.layout
        sm_props = context.scene.stop_motionify_settings
        
        layout.prop(sm_props, "strength", slider=True)
        layout.operator("object.clean_armature_animation")

def register():
    bpy.utils.register_class(StopMotionifyProperties)
    bpy.types.Scene.stop_motionify_settings = bpy.props.PointerProperty(type=StopMotionifyProperties)
    bpy.utils.register_class(OBJECT_OT_clean_armature_animation)
    bpy.utils.register_class(STOP_MOTIONIFY_PT_armature_panel)

def unregister():
    del bpy.types.Scene.stop_motionify_settings
    bpy.utils.unregister_class(StopMotionifyProperties)
    bpy.utils.unregister_class(OBJECT_OT_clean_armature_animation)
    bpy.utils.unregister_class(STOP_MOTIONIFY_PT_armature_panel)

if __name__ == "__main__":
    register()

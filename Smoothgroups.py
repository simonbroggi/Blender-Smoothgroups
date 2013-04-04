# Smoothgroups.py

import bpy
from bpy.types import Menu, Panel, UIList
import bmesh

class DATA_PT_smooth_groups(Panel):    
    bl_label = "Smooth Groups"
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME', 'CYCLES'}
    
    #from MeshButtonsPanel
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        engine = context.scene.render.engine
        obj = context.object
        return (obj and obj.type in {'MESH'} and (engine in cls.COMPAT_ENGINES))

    def draw(self, context):
        layout = self.layout

        ob = context.object
        me = ob.data
        group = False
        if len(me.smoothgroup_slots) > me.active_smoothgroup_index:
            group = me.smoothgroup_slots[me.active_smoothgroup_index] # should be a reference to a smoothgroup, not an index. possible?

        rows = 2
        if group:
            rows = 5

        row = layout.row()
        row.template_list("SMOOTHGROUP_UIList", "", me, "smoothgroup_slots", me, "active_smoothgroup_index", rows=rows)
        #row.template_list("MESH_UL_vgroups", "", ob, "vertex_groups", ob.vertex_groups, "active_index", rows=rows)

        col = row.column(align=True)
        col.operator("object.add_smoothgroup", icon='ZOOMIN', text="")
        col.operator("object.remove_smoothgroup", icon='ZOOMOUT', text="")

        if group:
            row = layout.row()
            row.prop(group, "name") #would work nicely if group were a refference
            #row.prop("todo", text="todo")

        if me.smoothgroup_slots and (ob.mode == 'EDIT'):
            row = layout.row()

            sub = row.row(align=True)
            sub.operator("object.set_selection_to_smoothgroup", text="Assign")
            sub.operator("object.remove_selection_from_smoothgroup", text="Remove")

            sub = row.row(align=True)
            sub.operator("object.select_smoothgroup", text="Select")
            sub.operator("object.deselect_smoothgroup", text="Deselect")
            layout.operator("object.smooth_according_to_acctive_smoothgroup", text="Smooth")
            #layout.prop(context.tool_settings, "vertex_group_weight", text="Weight")
            
class SMOOTHGROUP_UIList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        ob = data
        slot = item
        sg_name = slot.name + " : " + slot.face_selection_name
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=sg_name, translate=False, icon_value=icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
            
#hmm perhaps I need a Smoothgroups class containing several SmoothgroupSlots and the active_smoothgroup_index
class SmoothgroupSlot(bpy.types.PropertyGroup):
    face_selection_name = bpy.props.StringProperty(name="Face Selection Name", default="face_selection_1")
    prio = bpy.props.IntProperty(name="Priority", default=0)
    
class AddSmoothgroup(bpy.types.Operator):
    """Add a smoothgroup to the active mesh"""
    bl_idname = "object.add_smoothgroup"
    bl_label = "Add smoothgroup"
    
    @classmethod
    def pol(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')
    
    def execute(self, context):
        me = context.active_object.data
        sg = me.smoothgroup_slots.add()
        face_selection_number = 1
        face_selection_name = "face_selection_" + str(face_selection_number)
        while face_selection_name in me:
            face_selection_number = face_selection_number + 1
            face_selection_name = "face_selection_" + str(face_selection_number)
        me[face_selection_name] = []
        sg.face_selection_name = face_selection_name
        sg.name = "smoothgroup_"+str(face_selection_number)
        return {'FINISHED'}
            
class RemoveSmoothgroup(bpy.types.Operator):
    """Removes a smoothgroup and its face_selection property from the active mesh"""
    bl_idname = "object.remove_smoothgroup"
    bl_label = "Remove smoothgroup"
    
    @classmethod
    def pol(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')
    
    def execute(self, context):
        me = context.active_object.data
        sg = me.smoothgroup_slots[me.active_smoothgroup_index]
        if sg.face_selection_name in me:
            del me[sg.face_selection_name]
        me.smoothgroup_slots.remove(me.active_smoothgroup_index)
        #del me.smoothgroup_slots.items [me.active_smoothgroup_index]
        return {'FINISHED'}
    
class SelectSmoothgroup(bpy.types.Operator):
    """Select all the faces in the active smoothgroup"""
    bl_idname = "object.select_smoothgroup"
    bl_label = "Select faces of smoothgroup"
    
    @classmethod
    def pol(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')
    
    def execute(self, context):
        me = context.active_object.data
        group = me.smoothgroup_slots[me.active_smoothgroup_index]
        face_indices = me[group.face_selection_name]
        face_selection_bm = bmesh.from_edit_mesh(me)
        face_seq = face_selection_bm.faces
        for face in face_seq:
            if face.index in face_indices:
                face.select = True
        bmesh.update_edit_mesh(me)
        return {'FINISHED'}
    
class DeselectSmoothgroup(bpy.types.Operator):
    """Deselect all the faces in the active smoothgroup"""
    bl_idname = "object.deselect_smoothgroup"
    bl_label = "Deselect faces of smoothgroup"
    
    @classmethod
    def pol(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')
    
    def execute(self, context):
        me = context.active_object.data
        group = me.smoothgroup_slots[me.active_smoothgroup_index]
        face_indices = me[group.face_selection_name]
        face_selection_bm = bmesh.from_edit_mesh(me)
        face_seq = face_selection_bm.faces
        for face in face_seq:
            if face.index in face_indices:
                face.select = False
        bmesh.update_edit_mesh(me)
        return {'FINISHED'}
    
class RemoveSelectionFromSmoothgroup(bpy.types.Operator):
    """Removes the selected faces from the active smoothgroup"""
    bl_idname = "object.remove_selection_from_smoothgroup"
    bl_label = "Remove faces from smoothgroup"
    
    @classmethod
    def pol(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')
    
    def execute(self, context):
        me = context.active_object.data
        group = me.smoothgroup_slots[me.active_smoothgroup_index]
        face_indices = me[group.face_selection_name].to_list()
        face_selection_bm = bmesh.from_edit_mesh(me)
        face_seq = face_selection_bm.faces
        print(face_indices)
        for face in face_seq:
            if face.select and face.index in face_indices:
                face_indices.remove(face.index)
        me[group.face_selection_name] = face_indices
        return {'FINISHED'}
    
class SetSelectionToSmoothgroup(bpy.types.Operator):
    """Set selected faces to the active smoothgroup"""
    bl_idname = "object.set_selection_to_smoothgroup"
    bl_label = "Set to Smoothgroup"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')
    
    def execute(self, context):
        me = context.active_object.data
        group = me.smoothgroup_slots[me.active_smoothgroup_index]
        face_selection_bm = bmesh.from_edit_mesh(me)
        face_seq = face_selection_bm.faces
        selected_face_indices = []
        for face in face_seq:
            if face.select:
                selected_face_indices.append(face.index)
        print("selected faces: ")
        print(selected_face_indices)
        me[group.face_selection_name] = selected_face_indices
        return {'FINISHED'}

#the main thing, finally!
class SmoothAccordingToSmoothgroup(bpy.types.Operator):
    """Smooth vertex normals according to the active smoothgroup of the mesh"""
    bl_idname = "object.smooth_according_to_acctive_smoothgroup"
    bl_label = "Smooth according to active smoothgroup"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj and obj.type == 'MESH')
    
    def execute(self, context):
        me = context.active_object.data
        smooth_group_bm = bmesh.new() # create an empty BMesh
        #for sg in me.smoothgroup_slots:
        #print("smoothing " + sg.face_selection_name)
        sg = me.smoothgroup_slots[me.active_smoothgroup_index]
        smooth_group_bm.from_mesh(me) # fill it in from the mesh
        face_seq = smooth_group_bm.faces
        for face in face_seq:
            if not face.index in me[sg.face_selection_name]:
                face_seq.remove(face)
        smooth_group_bm.normal_update() # smooth normals of the mesh with only the faces in the group
        vert_seq = smooth_group_bm.verts
        bm = bmesh.from_edit_mesh(me)    
        for vert in vert_seq: #write the normals to the mesh
            if len(vert.link_faces) > 0:
                bm.verts[vert.index].normal = vert.normal #todo: write normals of verts connected to faces only
        bmesh.update_edit_mesh(me)
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(SmoothgroupSlot)
    
    # Create static properties here. ok?
    bpy.types.Mesh.smoothgroup_slots = bpy.props.CollectionProperty(type=SmoothgroupSlot) # http://www.blender.org/documentation/blender_python_api_2_57_release/bpy.props.html
    bpy.types.Mesh.active_smoothgroup_index = bpy.props.IntProperty()
    
    bpy.utils.register_class(SmoothAccordingToSmoothgroup)
    bpy.utils.register_class(AddSmoothgroup)
    bpy.utils.register_class(RemoveSmoothgroup)
    bpy.utils.register_class(SetSelectionToSmoothgroup)
    bpy.utils.register_class(SelectSmoothgroup)
    bpy.utils.register_class(DeselectSmoothgroup)
    bpy.utils.register_class(RemoveSelectionFromSmoothgroup)
    
    bpy.utils.register_class(SMOOTHGROUP_UIList)
    bpy.utils.register_class(DATA_PT_smooth_groups)
    
    
def unregister():
    bpy.utils.register_class(DATA_PT_smooth_groups)
    bpy.utils.unregister_class(SMOOTHGROUP_UIList)
    
    bpy.utils.unregister_class(SmoothAccordingToSmoothgroup)
    bpy.utils.unregister_class(AddSmoothgroup)
    bpy.utils.unregister_class(RemoveSmoothgroup)
    bpy.utils.unregister_class(SelectSmoothgroup)
    bpy.utils.unregister_class(DeselectSmoothgroup)
    bpy.utils.unregister_class(RemoveSelectionFromSmoothgroup)
    bpy.utils.unregister_class(SetSelectionToSmoothgroup)
    
    # do I ned to unregister the static properties?
    
    bpy.utils.unregister_class(SmoothgroupSlot)
    

if __name__ == "__main__":
    register()
    

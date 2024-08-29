bl_info = {
    "name": "Material Variants",
    "author": "Sammy Fennec",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "N-panel in the 3D Viewport",
    "description": "This addon let you make material variants. You select an option on the dropdown and all the materials will change to the asigned on that option",
    "category": "Material",
}

import bpy

class MaterialOption(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name", update=lambda self, context: update_enum_items(context))
    material: bpy.props.PointerProperty(type=bpy.types.Material, name="Material")

class OBJECT_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Material Variants"
    bl_idname = "material_variants_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Material Variants'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object

        row = layout.row()
        row.template_list("UI_UL_list", "material_options", scene, "material_options", scene, "material_options_index")

        col = row.column(align=True)
        col.operator("material_list.new_item", icon='ADD', text="")
        col.operator("material_list.delete_item", icon='REMOVE', text="")
        col.operator("material_list.move_item", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("material_list.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if scene.material_options:
            option = scene.material_options[scene.material_options_index]
            layout.prop(option, "name", text="Name")
            layout.prop(obj.material_options[scene.material_options_index], "material", text="Material")

        layout.separator()
        layout.label(text="Select Option:")
        row = layout.row(align=True)
        row.prop(scene, "selected_option", text="")
        row.operator("material_list.reload_dropdown", icon='FILE_REFRESH', text="")

class MATERIAL_OT_NewItem(bpy.types.Operator):
    bl_idname = "material_list.new_item"
    bl_label = "Add New Item"

    def execute(self, context):
        scene = context.scene
        new_item = scene.material_options.add()
        new_item.name = "Option " + str(len(scene.material_options))

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.material_options.add()

        update_enum_items(context)
        return {'FINISHED'}

class MATERIAL_OT_DeleteItem(bpy.types.Operator):
    bl_idname = "material_list.delete_item"
    bl_label = "Delete Item"

    def execute(self, context):
        scene = context.scene
        index = scene.material_options_index
        scene.material_options.remove(index)

        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.material_options.remove(index)

        scene.material_options_index = min(max(0, index - 1), len(scene.material_options) - 1)
        update_enum_items(context)
        return {'FINISHED'}

class MATERIAL_OT_MoveItem(bpy.types.Operator):
    bl_idname = "material_list.move_item"
    bl_label = "Move Item"
    direction: bpy.props.EnumProperty(items=(('UP', 'Up', ""), ('DOWN', 'Down', "")))

    def execute(self, context):
        scene = context.scene
        index = scene.material_options_index

        if self.direction == 'UP' and index > 0:
            scene.material_options.move(index, index - 1)
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    obj.material_options.move(index, index - 1)
            scene.material_options_index -= 1
        elif self.direction == 'DOWN' and index < len(scene.material_options) - 1:
            scene.material_options.move(index, index + 1)
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    obj.material_options.move(index, index + 1)
            scene.material_options_index += 1

        update_enum_items(context)
        return {'FINISHED'}

class MATERIAL_OT_ReloadDropdown(bpy.types.Operator):
    bl_idname = "material_list.reload_dropdown"
    bl_label = "Reload Dropdown"

    def execute(self, context):
        update_enum_items(context)
        return {'FINISHED'}

def update_enum_items(context):
    scene = context.scene
    items = [(str(i), option.name, "") for i, option in enumerate(scene.material_options)]
    bpy.types.Scene.selected_option = bpy.props.EnumProperty(
        items=items,
        name="Select Variant",
        update=update_materials
    )

def update_materials(self, context):
    scene = context.scene
    selected_option = int(scene.selected_option)

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            material_option = obj.material_options[selected_option]
            obj.active_material = material_option.material

def register():
    bpy.utils.register_class(MaterialOption)
    bpy.utils.register_class(OBJECT_PT_CustomPanel)
    bpy.utils.register_class(MATERIAL_OT_NewItem)
    bpy.utils.register_class(MATERIAL_OT_DeleteItem)
    bpy.utils.register_class(MATERIAL_OT_MoveItem)
    bpy.utils.register_class(MATERIAL_OT_ReloadDropdown)
    bpy.types.Scene.material_options = bpy.props.CollectionProperty(type=MaterialOption)
    bpy.types.Scene.material_options_index = bpy.props.IntProperty()
    bpy.types.Object.material_options = bpy.props.CollectionProperty(type=MaterialOption)

def unregister():
    bpy.utils.unregister_class(MaterialOption)
    bpy.utils.unregister_class(OBJECT_PT_CustomPanel)
    bpy.utils.unregister_class(MATERIAL_OT_NewItem)
    bpy.utils.unregister_class(MATERIAL_OT_DeleteItem)
    bpy.utils.unregister_class(MATERIAL_OT_MoveItem)
    bpy.utils.unregister_class(MATERIAL_OT_ReloadDropdown)
    del bpy.types.Scene.material_options
    del bpy.types.Scene.material_options_index
    del bpy.types.Object.material_options
    del bpy.types.Scene.selected_option

if __name__ == "__main__":
    register()

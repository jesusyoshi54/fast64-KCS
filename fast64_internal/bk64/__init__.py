import bpy

from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty,
    IntVectorProperty,
    BoolVectorProperty,
)
from bpy.utils import register_class, unregister_class

from .bk64_level_importer import (
    bk64_import_panel_register,
    bk64_import_panel_unregister,
    bk64_import_register,
    bk64_import_unregister,
    BK64_ImportProperties,
)


class BK64_Properties(PropertyGroup):
    """Global BK64 Scene Properties found under scene.fast64.bk64"""

    # Import Course DL
    importer: bpy.props.PointerProperty(type=BK64_ImportProperties)

    @staticmethod
    def upgrade_changed_props():
        pass


def bk64_panel_register():
    register_class(BK64_Properties)
    bk64_import_panel_register()


def bk64_panel_unregister():
    unregister_class(BK64_Properties)
    bk64_import_panel_unregister()


def bk64_register(register_panels: bool):
    bk64_import_register()
    if register_panels:
        bk64_panel_register()


def bk64_unregister(unregister_panels: bool):
    bk64_import_unregister()
    if unregister_panels:
        bk64_panel_unregister()

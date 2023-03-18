from __future__ import annotations

import bpy, math, os

# a WIP suite for adding/removing drivers for various properties within fast64, currently built with support for sm64 tile animations
# and called from f3d_material during custom property callbacks


# adds a driver to the data path on object data "data_object" at path "data_path" and uses an index if data is an array.
# if the path already has a driver, then it will instead return the existing driver
def get_or_add_driver(block_object, data_object, prop_path, index: int = -1):
    if block_object.animation_data:
        # create the path for the property we will attach the driver to
        abs_prop_path = data_object.path_from_id(prop_path)
        # get driver from bpy data path
        driver = block_object.animation_data.drivers.find(abs_prop_path)
        if driver:
            return driver
    return data_object.driver_add(prop_path, index)

def remove_driver(block_object, data_object, prop_path, index: int = -1):
    if block_object.animation_data:
        # create the path for the property we will attach the driver to
        abs_prop_path = data_object.path_from_id(prop_path)
        # get driver from bpy data path
        driver = block_object.animation_data.drivers.find(abs_prop_path)
        if driver:
            data_object.driver_remove(prop_path, index)

# here are some generics for getting commonly used drivers and values
def get_tex_field_driver(material: bpy.types.Material, desired_group: str, tile_path: str):
    return get_or_add_driver(
        material.node_tree,
        material.node_tree.nodes[desired_group].inputs[tile_path],
        "default_value"
    )

def get_tile_scroll_values(tex: TextureProperty, s: bool = False, t: bool = False):
    if not tex.tex or (not s and not t):
        return
    if s:
        return (tex.tile_scroll.s, tex.tile_scroll.interval, tex.S.low)
    else:
        return (tex.tile_scroll.t, tex.tile_scroll.interval, tex.T.low)

# and here are some generic functions for setting drivers to an easy value

# update with speed on an interval, sm64 tile scrolling
def update_driver_on_interval(driver: bpy.types.Driver, speed: int, interval: int, base_value: float):
    driver.expression = f"int(frame / {interval})*{speed} + {base_value}"

# update linearly, vertex scrolling
def update_driver_linear(driver: bpy.types.Driver, speed: float, base_value: float):
    driver.expression = f"frame*{speed} + {base_value}"

# update with sin, vertex scrolling
def update_driver_sinusoidal(driver: bpy.types.Driver, amplitude: float, frequency: float, offset: float, base_value: float):
    driver.expression = f"sin(frame*{frequency} + {offset})*{amplitude} + {base_value}"

# update with noise, vertex scrolling
# uses modifier, needs to be cleaned up later
def update_driver_noise(driver: bpy.types.Driver, amplitude: float, base_value: float):
    mod = driver.modifiers.new("NOISE")
    mod.Strength = amplitude

def remove_driver_modifiers(driver: bpy.types.Driver):
    (driver.modifiers.remove(mod) for mod in driver.modifiers)


import bpy,sys
from pathlib import Path
from sverchok.ui.sv_examples_menu import add_extra_examples, make_submenu_classes
import sverchok_bmesh
EXAMPLES_PATH = Path(sverchok_bmesh.__file__).parent / 'examples'

def example_categories_names():
    names = []
    for category_path in EXAMPLES_PATH.iterdir():
        if category_path.is_dir():
            names.append((EXAMPLES_PATH, category_path.name))
    for name in names:
        yield name

def register():
    submenu_classes = (make_submenu_classes(path, category_name) for path, category_name in example_categories_names())
    for examples_menu in submenu_classes:
        bpy.utils.register_class(examples_menu)
    add_extra_examples('bmesh', EXAMPLES_PATH)

def unregister():
    pass
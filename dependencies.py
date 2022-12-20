
from sverchok.dependencies import SvDependency

ex_dependencies = dict()

try:
    import sverchok
    from sverchok.utils.logging import info, error, debug

    from sverchok.dependencies import (
            SvDependency,
            ensurepip,pip
        )

    sverchok_d = ex_dependencies["sverchok"] = SvDependency('sverchok', "https://github.com/nortikin/sverchok")
    sverchok_d.module = sverchok
except ImportError:
    message =  "Sverchok addon is not available. Sverchok-Bmesh will not work."
    print(message)
    sverchok = None
"""
sdf_d = ex_dependencies["sdf"] = SvDependency("sdf", "https://github.com/fogleman/sdf")
try:
    import sdf
    sdf_d.module = sdf
except ImportError:
    sdf = None

pyexcel_d = ex_dependencies["pyexcel"] = SvDependency("pyexcel", "https://github.com/pyexcel/pyexcel")
pyexcel_d.pip_installable = True
try:
    import pyexcel
    pyexcel_d.module = pyexcel
except ImportError:
    pyexcel = None
"""
from __future__ import annotations

import traceback
import io
import sys
from typing import Any


preamble = '''
import cadquery as cq
import cadquery
import math
import numpy as np
'''

code_example = '''pitch = 5
height = 20
turns = 4
radius = 5

# Define the helix path using a proper callable function
def helix(t):
    return (
        radius * math.cos(t),
        radius * math.sin(t),
        pitch * t / (2 * math.pi)
    )

# Create a helix path
path = (cq.Workplane("XY")
        .parametricCurve(lambda t: helix(2 * math.pi * turns * t), N=100))

# Define profile to be swept along the path
profile = cq.Workplane("XZ").circle(0.5)

# Perform the sweep
shape = profile.sweep(path, isFrenet=True)

# Export to STL
shape.val().exportStl('spiral_sweep.stl')
result = spiral_sweep.stl
'''


class CadqueryExecutor:
    def execute(self, script: str) -> (str, Any, bool):
        output = io.StringIO()
        sys.stdout = output
        sys.stderr = output
        result = None
        print('script:', script)
        try:
            exec(preamble + script)
            return output.getvalue(), result, True
        except Exception as e:
            return output.getvalue() + traceback.format_exc(), result, False
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            output.close()

from __future__ import annotations

import subprocess
import tempfile
from typing import Any
from dataclasses import dataclass, field
import random
import os


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


def random_dir():
    d = 'scripts/models/' + str(random.randint(0, 1000000)) + '/'
    os.mkdir(d)
    return d


@dataclass
class CadqueryExecutor:
    base_dir: str = field(default_factory=random_dir)
    
    def execute(self, script: str) -> (str, Any, bool):
        with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
            postfix = '\nprint("<RESULT>" + str(result) + "</RESULT>")\n'
            f.write(preamble + script + postfix)
            script_path = f.name
        try:
            output = subprocess.check_output(['python', script_path], stderr=subprocess.STDOUT, cwd=self.base_dir)
            result = output.decode().split('<RESULT>')[1].split('</RESULT>')[0] if '<RESULT>' in output.decode() else None
            return output.decode(), result, True
        except subprocess.CalledProcessError as e:
            return e.output.decode(), None, False

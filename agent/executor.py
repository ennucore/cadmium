from __future__ import annotations

import subprocess
import tempfile
from typing import Any
from dataclasses import dataclass, field
import random
import os
import json


preamble = """
import cadquery as cq
import cadquery
import math
import numpy as np
"""

code_example = """pitch = 5
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
"""


def random_dir():
    d = "cadmium/scripts/models/" + str(random.randint(0, 1000000)) + "/"
    os.mkdir(d)
    return d


def get_params(script_path):

    parameters = {}

    with open(script_path, "r") as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if lines[i].startswith("# Parameters"):
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() == "":
                        return parameters

                    line = lines[j].strip().split("=")
                    if len(line) == 2:
                        var_name = line[0].strip()

                        rest_line = line[1].strip().split("#")

                        var_value = rest_line[0].strip()

                        if len(rest_line) > 1:
                            var_unit = rest_line[1].strip()
                        else:
                            var_unit = None

                        parameters[var_name] = {"value": var_value, "unit": var_unit}
    return parameters


@dataclass
class CadqueryExecutor:
    base_dir: str = field(default_factory=random_dir)

    def execute(self, script: str) -> tuple[str, Any, bool]:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            postfix = '\nprint("<RESULT>" + str(result) + "</RESULT>")\n'
            f.write(preamble + script + postfix)
            script_path = f.name
        try:
            process = subprocess.Popen(
                ["python", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=self.base_dir,
                universal_newlines=True,
            )
            output, _ = process.communicate()

            if "<RESULT>" in output:
                result = output.split("<RESULT>")[1].split("</RESULT>")[0]

                params = get_params(script_path=script_path)
                params_file_path = os.path.join(self.base_dir, "params.json")
                with open(params_file_path, "w") as params_file:
                    json.dump(params, params_file, indent=4)

                return output, result, True
            else:
                os.rmdir(self.base_dir)
                return output, None, False
        except Exception as e:
            print("===================================================")
            print(e)
            return str(e), None, False

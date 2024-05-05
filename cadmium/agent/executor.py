from __future__ import annotations

import subprocess
import tempfile
from typing import Any
from dataclasses import dataclass, field
import traceback
import random
import os
import json

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from .prompts import example_params_prompt
from .utils import call_small_model

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
    os.makedirs(d)
    print('created', d)
    return d


def get_params(script_path) -> dict:
    with open(script_path, "r") as file:
        code = file.read()

    system_prompt = (
        "You are a CAD agent. Your goal is to extract the parameters in the given Cadquery python code "
        "and return them as json.\n"
        "The parameters can be generally found under a comment # Parameters or something similar. \n"
        "Your response should contain your thoughts and a specific description of what you're extracting "
        "and then the json inside the code braces, like this:\n"
        f"```{example_params_prompt}```"
        "Do not include any programming language reference to the code string"
    )
    user_prompt = ("Extract parameters from the following \n"
                   "Code :\n"
                   f"{code}"
                   )
    message = call_small_model(system_prompt + '\n\n' + user_prompt)

    params = message.split("\n```", 1)[1].split("\n", 1)[1].strip().split("```")[0] if "\n```" in message else ""
    try:
        params_json = json.loads(params)
    except json.JSONDecodeError:
        return {}

    print("PARAMS", params)
    print("PARAMS JSON", params_json)

    return params_json


def ensure_dir_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


@dataclass
class CadqueryExecutor:
    base_dir: str = field(default_factory=random_dir)

    def execute(self, script: str) -> tuple[str, Any, bool]:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            postfix = '\nprint("<RESULT>" + str(result) + "</RESULT>")\n'
            f.write(preamble + script + postfix)
            script_path = f.name
        ensure_dir_exists(self.base_dir)
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
                return output, None, False
        except Exception as e:
            print("===================================================")
            print(e)
            print(traceback.format_exc())
            return str(e), None, False

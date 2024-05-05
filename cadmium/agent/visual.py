from __future__ import annotations
import os
import openai
from cadmium.stl_to_pics.render import render
from dotenv import load_dotenv
from multiprocessing.pool import ThreadPool
from itertools import chain
import json
import glob
import base64


load_dotenv()
client = openai.OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        timeout=100,
    )


def stl_to_paths(stl_path: str) -> list[str]:
    # get the directory of the stl file
    stl_dir = os.path.dirname(stl_path) or '.'
    stl_name = os.path.basename(stl_path).split('.')[0]
    render(
        [stl_path],
        [(0, 0, 0)],
        [(0.5, 0.5, 1.0)],
        stl_dir,
        prefix=stl_name,
        short_positions=True,
    )
    paths = glob.glob(os.path.join(stl_dir, f"{stl_name}_*.jpg"))
    return paths


def path_to_openai_image(path: str) -> dict:
    """
    Convert a path to an image to an OpenAI image object that looks like this:
    {
        "type": "image_url",
        "image_url": {
        "url": f"data:image/jpeg;base64,{base64_image}"
        }
    }
    """
    with open(path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{base64_image}"
        }
    }


def visual_feedback(stl_path: str, prompt: str) -> (str, bool):
    paths = stl_to_paths(stl_path)
    messages = [
        {"role": "system", "content": "Your goal is to evaluate 3d models against a prompt."},
        {"role": "user", "content": [
            {"type": "text", "text": f"The prompt for the model is as follows: \n```\n{prompt}\n```\nPlease, look at the images and provide feedback on the model: whether it fits the requirements and whether the user will be satisfied. "
             "The images below are views of the 3d model from different sides: top, bottom, front, left."},
            *map(path_to_openai_image, paths)
            ]},
    ]
    return client.chat.completions.create(
        model="gpt-4-turbo-2024-04-09",
        messages=messages,
    ).choices[0].message.content, True


def pick_visually(stl_paths: list[str], prompt: str, n_to_pick: int = 2) -> list[str]:
    # get images in threads
    paths = list(map(stl_to_paths, stl_paths))
    messages = [
        {"role": "system", "content": f"Your goal is to select **{n_to_pick}** best 3d models based on a prompt."},
        {"role": "user", "content": [
            {"type": "text", "text": f"The prompt for the model is as follows: \n```\n{prompt}\n```\nPlease, look at the images and select {n_to_pick} best 3d models using the result function. "
             "The images below are views of the 3d models from different sides: top, bottom, front, left."},
            *chain(*map(lambda inp: [{"type": "text", "text": f"Model #{inp[0] + 1}.\nHere it is from top, bottom, front, left:"}, *map(path_to_openai_image, inp[1])], enumerate(paths)))
            ]},
    ]
    
    response = client.chat.completions.create(
        model="openai/gpt-4-turbo-2024-04-09",
        messages=messages,
        tools=[{"type": "function", "function": {
            "name": "result", "description": "Report the selected 3d models",
            "parameters": {
                "type": "object",
                "properties": {
                    "selected_models": {
                        "type": "array", "description": "The selected models, in decreasing order of preference",
                        "items": {"type": "object", "properties": {"model_index": {"type": "number", "example": 1},
                                                                   }}, "minItems": n_to_pick, "maxItems": n_to_pick},
                }
            }
        }}],
        tool_choice={"type": "function", "function": {"name": "result"}},
        temperature=0.25
    )

    message = response.choices[0].message
    data = json.loads(message.tool_calls[0].function.arguments if message.tool_calls else message.content)
    data = data.get('result', data)
    data = data.get('parameters', data)
    selected_models = data.get('selected_models', [])
    selected_models = [stl_paths[res['model_index'] - 1] for res in selected_models]
    return selected_models

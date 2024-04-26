from __future__ import annotations
import os
import openai
from cadmium.stl_to_pics.render import render
from dotenv import load_dotenv
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
    stl_dir = os.path.dirname(stl_path)
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
            {"type": "text", "text": f"The prompt for the model is as follows: \n```\n{prompt}\n```\nPlease, look at the images and provide feedback on the model."},
            *map(path_to_openai_image, paths)
            ]},
    ]
    return client.chat.completions.create(
        model="gpt-4-turbo-2024-04-09",
        messages=messages,
    ).choices[0].message.content, True

import yaml
import json

with open('cadmium/examples.yaml') as f:
    examples = yaml.load(f, Loader=yaml.FullLoader)

with open('cadmium/example_params.json') as f:
    example_params = json.load(f)

selected_examples = [2, 4, 7, 8, 9, 15, 20, 21, 22, 23, 24, 19, 28, 32, 33, 34]

examples_prompt = 'Here are some examples of how to use the functions:\n' + '\n'.join([
    f'Name: {examples[i - 1]["Name of Part"]}\n{examples[i-1]["label"]}\n\n```\n{examples[i-1]["Code"]}\n```\n\n' for i in selected_examples])

advice = '''Some advice:
Usually, when using .shell() to make something hollow, you have to choose a face before that and the thickness should be POSITIVE. Example: `.faces("+Z").shell(10)`.
You can also use shell without that to make a fillet. 
'''

fixing_advice = '''Some advice:
If you have a "No pending wires present" error, you need to make sure that the profile is a 2D shape.
'''

example_params_prompt = 'Here is an example of need to be formatted:\n' + json.dumps(example_params, indent=4)

# box extrude thing

import yaml

with open('examples.yaml') as f:
    examples = yaml.load(f, Loader=yaml.FullLoader)

selected_examples = [2, 3, 4, 7, 8, 9, 15]

examples_prompt = 'Here are some examples:\n' + '\n'.join([
    f'Name: {examples[i - 1]["Name of Part"]}\n{examples[i-1]["label"]}\n\n```\n{examples[i-1]["Code"]}\n```\n\n' for i in selected_examples])

fixing_advice = '''Some advice:
If you have a "No pending wires present" error, you need to make sure that the profile is a 2D shape.
'''
# box extrude thing

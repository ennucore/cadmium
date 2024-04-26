import sys
from cadmium.agent.visual import visual_feedback, pick_visually


if __name__ == '__main__':
    stl_paths = sys.argv[2:]
    prompt = sys.argv[1]
    if len(stl_paths) == 1:
        print(visual_feedback(stl_paths[0], prompt)[0])
        sys.exit(0)
    else:
        print(pick_visually(stl_paths, prompt))

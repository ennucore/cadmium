import sys
from cadmium.agent.visual import visual_feedback


if __name__ == '__main__':
    stl_path = sys.argv[1]
    prompt = sys.argv[2]
    print(visual_feedback(stl_path, prompt))

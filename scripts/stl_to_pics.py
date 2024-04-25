import os
import sys
from cadmium.stl_to_pics.render import render


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <stl_path (single stl file or directory of stl files)> <output_path (directory)> [prefix]")
        sys.exit(1)

    stl_path = sys.argv[1]
    output_path = sys.argv[2]

    if os.path.isdir(stl_path):
        # Render all STL files in the input directory
        stl_files = [os.path.join(stl_path, f) for f in os.listdir(stl_path) if f.endswith(".stl")]
        for stl_model_path in stl_files:
            stl_out_dirname = os.path.join(output_path, os.path.splitext(os.path.basename(stl_model_path))[0])
            if not os.path.exists(stl_out_dirname):
                os.makedirs(stl_out_dirname)
            render(
                [stl_model_path],
                [(0, 0, 0)],
                [(0.5, 0.5, 1.0)],
                stl_out_dirname,
                prefix=""
            )
    else:
        # Render a single STL file to the output directory
        stl_out_dirname = os.path.join(output_path, os.path.splitext(os.path.basename(stl_path))[0])
        if not os.path.exists(stl_out_dirname):
            os.makedirs(stl_out_dirname)
        render(
            [stl_path],
            [(0, 0, 0)],
            [(0.5, 0.5, 1.0)],
            stl_out_dirname,
            prefix=""
        )

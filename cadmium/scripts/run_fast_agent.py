import os
import typer

from cadmium.agent.faster_agent import run_agents
from cadmium.utils.logging import setup_simple_logger


if __name__ == "__main__":
    setup_simple_logger("trace", log_file=".logs/" + os.path.basename(__file__) + ".{time:YYYY-MM-DD_HH-mm-ss!UTC}.log")

    prompt = typer.prompt("Enter a prompt for the agent")

    results = run_agents(prompt, 10)

    for r in results[1]:
        print(r.result)


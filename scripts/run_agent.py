import typer

from cadmium.agent.agent import Agent


if __name__ == "__main__":
    prompt = typer.prompt("Enter a prompt for the agent")
    agent = Agent.initialize(prompt)
    agent.run_agent()

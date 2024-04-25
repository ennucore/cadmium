import typer

from cadmium.agent.agent import Agent, UserMessage


if __name__ == "__main__":
    prompt = typer.prompt("Enter a prompt for the agent")
    agent = Agent.initialize(prompt)
    while True:
        agent.run_agent()
        agent.history.append(UserMessage(message=typer.prompt("Enter a message for the agent")))

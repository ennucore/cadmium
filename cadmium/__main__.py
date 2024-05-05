import typer
import rich

from agent.agent import Agent, UserMessage


if __name__ == "__main__":
    prompt = typer.prompt("Enter a prompt for the agent")
    agent = Agent.initialize(prompt)
    while True:
        agent.run_agent(streaming_callback=lambda upd: rich.print(f'[yellow][bold]Update:[/bold] {upd}[/yellow]'))
        agent.history.append(UserMessage(message=typer.prompt("Enter a message for the agent")))

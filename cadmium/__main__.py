import typer
import rich

from agent.agent import Agent, UserMessage
from agent.utils import open_file_with_default


if __name__ == "__main__":
    prompt = typer.prompt("Enter a prompt for the agent")
    agent = Agent.initialize(prompt)
    while True:
        agent.run_agent(streaming_callback=lambda upd: rich.print(f'[yellow][bold]Update:[/bold] {upd}[/yellow]'))
        msg = typer.prompt("Enter a message for the agent")
        if msg.strip() == 'i':
            agent.run_image_reflection(streaming_callback=
                                       lambda upd: rich.print(f'[yellow][bold]Update:[/bold] {upd}[/yellow]'))
        elif msg.strip() == 'exit':
            break
        elif msg.strip() == 'o':
            open_file_with_default(agent.get_last_result())
        else:
            agent.history.append(UserMessage(message=msg))

import typer
import rich

from agent.agent import Agent, UserMessage
from agent.utils import open_file_with_default

app = typer.Typer(help="Text-to-CAD agent for generating 3D models from text prompts.")


@app.command()
def main(prompt: str = ''):
    prompt = prompt or typer.prompt("Enter a prompt for the agent")
    agent = Agent.initialize(prompt)
    while True:
        agent.run_agent(streaming_callback=lambda upd: rich.print(f'[yellow][bold]Update:[/bold] {upd}[/yellow]'))
        msg = typer.prompt("Enter a message for the agent")
        if msg.strip() == 'i' or not msg.strip():
            agent.run_image_reflection(streaming_callback=
                                       lambda upd: rich.print(f'[yellow][bold]Update:[/bold] {upd}[/yellow]'))
        elif msg.strip() == 'exit':
            break
        elif msg.strip().lower() in ['o', 'open']:
            open_file_with_default(agent.get_last_result())
        else:
            agent.add_images_message(agent.get_last_result())
            agent.history.append(UserMessage(message=msg))


if __name__ == "__main__":
    app()

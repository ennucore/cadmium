import typer

from cadmium.agent.agent import Agent, AgentMessage, UserMessage


if __name__ == "__main__":
    prompt = typer.prompt("Enter a prompt for the agent")
    agent = Agent.initialize(prompt)
    agent.run_agent(streaming_callback=lambda x: None)

    # agent.change_params({'table_length': 699})

    # while True:
    #     agent.run_agent()
    #     agent.history.append(UserMessage(message=typer.prompt("Enter a message for the agent")))
    #     print('HISTORY', agent.history)


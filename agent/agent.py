from __future__ import annotations

from cadmium.agent.executor import code_example, CadqueryExecutor
from cadmium.agent.recap_streamer import RecapStreamer
from cadmium.agent.prompts import examples_prompt, fixing_advice, advice

from dataclasses import dataclass, field
import rich
import os
import json
import openai
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from groq import Groq
from abc import ABC
from dotenv import load_dotenv
from multiprocessing.pool import ThreadPool
from copy import deepcopy

load_dotenv()


@dataclass
class AgentFactory:
    model: str = "openai/gpt-4-turbo-2024-04-09"


class Message(ABC):
    def to_dict(self) -> dict:
        return {"content": repr(self), "role": self.role}

    def to_rich_dict(self) -> dict:
        return {"type": self.__class__.__name__, **self.__dict__}

    @classmethod
    def from_rich_dict(cls, d: dict):
        if d["type"] == "AgentMessage":
            return AgentMessage(
                content=d["content"], code=d["code"], thoughts=d["thoughts"]
            )
        elif d["type"] == "CodeExecutionFeedback":
            return CodeExecutionFeedback(
                output=d["output"],
                finished_successfully=d["finished_successfully"],
                result=d["result"],
            )
        elif d["type"] == "UserMessage":
            return UserMessage(message=d["message"])
        else:
            return cls(content=d["content"], role=d["role"])


@dataclass
class AgentMessage(Message):
    content: str
    code: str = ""
    thoughts: str = ""
    role = "assistant"

    def __repr__(self) -> str:
        return self.content  # f'{self.thoughts}\n```\n{self.code}\n```'

    @classmethod
    def from_message(cls, message: str) -> AgentMessage:
        return cls(
            content=message,
            thoughts=message.split("\n```")[0],
            code=message.split("\n```", 1)[1].split("\n", 1)[1].strip().split("```")[0] if "\n```" in message else "",
        )

    def run_code(self, executor: CadqueryExecutor) -> CodeExecutionFeedback | None:
        output, result, finished_successfully = executor.execute(self.code)
        if result:
            rich.print(f"[red]{executor.base_dir + str(result)}[/red]")
        return CodeExecutionFeedback(
            output=output,
            result=(executor.base_dir + result) if result else None,
            finished_successfully=finished_successfully,
        )


@dataclass
class CodeExecutionFeedback(Message):
    output: str
    finished_successfully: bool
    result: str = ""
    role = "system"

    def __repr__(self) -> str:
        err_msg = ""
        if not self.finished_successfully:
            err_msg = (
                "The code execution failed. Please, take a deep breath, write the reasons while it failed, and write the code again with more attention to detail.\n"
                + fixing_advice
            )
        return f"{self.output}\n{err_msg}\n"


@dataclass
class UserMessage(Message):
    message: str
    role: str = "user"

    def __repr__(self) -> str:
        return f"{self.message}"


@dataclass
class Agent:
    # model: str = 'llama3-70b-8192'    # 'openai/gpt-4-turbo-2024-04-09'
    # model: str = 'meta-llama/llama-3-70b-instruct:nitro'
    model: str = "openai/gpt-4-turbo-2024-04-09"
    history: list[UserMessage | AgentMessage | CodeExecutionFeedback] = field(
        default_factory=list
    )
    executor: CadqueryExecutor = field(default_factory=CadqueryExecutor)

    def get_first_messages(self, prompt: str) -> list[UserMessage]:
        return [
            UserMessage(message=examples_prompt, role="system"),
            UserMessage(message="You are a CAD agent called Cadmium. Your goal is to create a CAD model based on the user's description by writing Python code based on Cadquery.\n"
                        "When writing the python code, output the STL to a file in the current directory, then store the filename in the `result` variable.\n"
                        "Before writing the code, first write a numbered list of all the small parts you will have in your model, their position relative to all the other elements, shapes, sizes, and direction. Write how you're going to contruct them.\n"
                        "Your response should contain your thoughts and a specific description of what you're going to do and what the model will be on a geometric level, then the code inside the code braces, like this:\n"
                        f"```\n{code_example}\n```\n\nNote that you should always have the code and you cannot ask follow-ups", role="user"), 
            UserMessage(message=advice, role="system"),
            UserMessage(message=f"Create the following model:\n{prompt}")]
    
    @classmethod
    def initialize(cls, prompt: str, factory: AgentFactory | None = None) -> Agent:
        self = cls()
        if factory is not None:
            self.model = factory.model
        self.history = self.get_first_messages(prompt)
        return self

    def get_next_message(self, callback_function=None) -> AgentMessage:
        message_history = [msg.to_dict() for msg in self.history]
        # response = ask_llm(provider=LLMProvider.GROQ, model=LLMModel.GROQ_LLAMA3_70, query=message_history)
        if "/" not in self.model:
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        else:
            client = openai.OpenAI(
                # api_key=os.getenv("OPENAI_API_KEY"),
                api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1", 
                timeout=100
            )

        response = client.chat.completions.create(
            model=self.model,
            # model="gpt-4-turbo-2024-04-09",
            messages=message_history,
            temperature=0.4,
        ).choices[0].message.content
        print(response)
        return AgentMessage.from_message(response)

    def add_user_message(self, message: str) -> None:
        self.history.append(UserMessage(message=message))
    
    def get_latest_chatbot_message(self) -> str:
        try:
            latest_message = [msg for msg in self.history if msg.role == "assistant"][-1]
            return latest_message.content
        except IndexError:
            return ""
        

    def run_step(self, streaming_callback=False) -> list[CodeExecutionFeedback | AgentMessage]:
        next_message = self.get_next_message(streaming_callback)
        self.history.append(next_message)
        code_feedback = next_message.run_code(self.executor)

        return [next_message] + ([code_feedback] if code_feedback else [])

    def run_agent(self, max_iters: int = 7, streaming_callback=None) -> None | str:
        if streaming_callback:
            streamer = RecapStreamer(callback_function=streaming_callback).stream_non_blocking
        while not getattr(self.history[-1], "finished_successfully", False) and max_iters > 0:
            self.history.extend(self.run_step(streamer))
            rich.print(self.history[-1])
            rich.print(self.history[-1])
            max_iters -= 1
        return getattr(self.history[-1], "result", None)

    def clone(self) -> Agent:
        c = deepcopy(self)
        c.executor = CadqueryExecutor()
        return c

    def run_multiply(self, times: int, streaming_function=None):
        # create copies of self and run them in parallel
        copies = [self.clone() for _ in range(times)]
        with ThreadPool(times) as pool:
            results = pool.map(lambda agent: (agent[1].run_agent(streaming_callback=lambda x: streaming_function(x, agent[0])), agent[1]), list(enumerate(copies)))
        agents = [result[1] for result in results]
        return agents, [result[0] for result in results]

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "history": [msg.to_rich_dict() for msg in self.history],
        }

    @classmethod
    def from_dict(cls, d: dict) -> Agent:
        self = cls()
        self.model = d["model"]
        self.history = [Message.from_rich_dict(msg) for msg in d["history"]]
        return self

    def change_params(self, new_params: dict) -> str:
        found_code_feedback = False

        for history_item in reversed(self.history):
            if found_code_feedback:
                if isinstance(history_item, AgentMessage):
                    agent_message = history_item
                    code = agent_message.code
                    print('CODE', code)
                    break

            else:
                if isinstance(history_item, CodeExecutionFeedback):
                    output = history_item.output
                    result = history_item.result

                    print("OUTPUT", output)
                    print("Result", result)
                    found_code_feedback = True
        if code:
            client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
            
            system_prompt = ChatMessage(content= "You are a CAD agent. Your goal is to update the parameters in the given Cadquery python code based on the user's description.\n"
                                        "Only update the variable values that exist in the code. \n"
                                        "Your response should contain your thoughts and a specific description of what you're modifying then the code inside the code braces, like this:\n"
                                        f"```\n code ...\n ```"
                                        "Do not include any programming language reference to the code string",
                                        role="system"
                                      )
            user_prompt = ChatMessage(content= "In the following code update the parameters that are under comment # Parameters. \n"
                                        "Parameters to update :\n"
                                        f"{json.dumps(new_params)} \n"

                                        "Code: \n"
                                        f"{code}",
                                        role="user"
                                      )

            chat_response = client.chat(
                    model="mistral-large-latest",
                    messages=[system_prompt, user_prompt]
                )
            
            message = chat_response.choices[0].message.content
            agent_message = AgentMessage(message).from_message(message=message)
            agent_message.run_code(self.executor)


        












            
        

        



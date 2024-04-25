from __future__ import annotations
from cadmium.llms.ask import LLMModel, LLMProvider, ask_llm

from cadmium.agent.executor import code_example, CadqueryExecutor
from cadmium.agent.prompts import examples_prompt, fixing_advice

from dataclasses import dataclass, field
import rich
import os
import openai
from groq import Groq
from abc import ABC
from dotenv import load_dotenv
from multiprocessing.pool import ThreadPool
from copy import deepcopy

load_dotenv()

@dataclass
class AgentFactory:
    model: str = 'openai/gpt-4-turbo-2024-04-09'
    

class Message(ABC):
    def to_dict(self) -> dict:
        return {"content": repr(self), "role": self.role}
    

@dataclass
class AgentMessage(Message):
    content: str
    code: str = ''
    thoughts: str = ''
    role = "assistant"
    
    def __repr__(self) -> str:
        return self.content   # f'{self.thoughts}\n```\n{self.code}\n```'
    
    @classmethod
    def from_message(cls, message: str) -> AgentMessage:
        return cls(content=message,
                   thoughts=message.split('\n```')[0],
                   code=message.split('\n```', 1)[1].split('\n', 1)[1].strip().split('```')[0])

    
    
    def run_code(self, executor: CadqueryExecutor) -> CodeExecutionFeedback:
        output, result, finished_successfully = executor.execute(self.code)
        return CodeExecutionFeedback(output=output, result=result, finished_successfully=finished_successfully)


@dataclass
class CodeExecutionFeedback(Message):
    output: str
    finished_successfully: bool
    result: str = ''
    role = "system"
    
    def __repr__(self) -> str:
        err_msg = ''
        if not self.finished_successfully:
            err_msg = 'The code execution failed. Please, take a deep breath, write the reasons while it failed, and write the code again with more attention to detail.\n' + fixing_advice
        return f'{self.output}\n{err_msg}\n'


@dataclass
class UserMessage(Message):
    message: str
    role: str = "user"
    
    def __repr__(self) -> str:
        return f'{self.message}'


@dataclass
class Agent:
    # model: str = 'llama3-70b-8192'    # 'openai/gpt-4-turbo-2024-04-09'
    model: str = 'meta-llama/llama-3-70b-instruct:nitro'
    # model: str = 'openai/gpt-4-turbo-2024-04-09'
    history: list[UserMessage | AgentMessage | CodeExecutionFeedback] = field(default_factory=list)
    executor: CadqueryExecutor = field(default_factory=CadqueryExecutor)
    
    def get_first_messages(self, prompt: str) -> list[UserMessage]:
        return [
            UserMessage(message=examples_prompt, role="system"),
            UserMessage(message="You are a CAD agent called Cadmium. Your goal is to create a CAD model based on the user's description by writing Python code based on Cadquery.\n"
                        "When writing the python code, output the STL to a file in the current directory, then store the filename in the `result` variable.\n"
                        "Your response should contain your thoughts and a specific description of what you're going to do and what the model will be on a geometric level, then the code inside the code braces, like this:\n"
                        f"```\n{code_example}\n```", role="system"), 
            UserMessage(message=f"Create the following model:\n{prompt}")]
    
    @classmethod
    def initialize(cls, prompt: str, factory: AgentFactory | None = None) -> Agent:
        self = cls()
        if factory is not None:
            self.model = factory.model
        self.history = self.get_first_messages(prompt)
        return self
    
    def get_next_message(self) -> AgentMessage:
        message_history = [msg.to_dict() for msg in self.history]
        #response = ask_llm(provider=LLMProvider.GROQ, model=LLMModel.GROQ_LLAMA3_70, query=message_history)
        if self.model == 'llama3-70b-8192':
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        else:
            client = openai.OpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1", 
                timeout=100
                )
        response = client.chat.completions.create(
            model=self.model,
            messages=message_history,
            temperature=0.4,
        ).choices[0].message.content
        print(response)
        return AgentMessage.from_message(response)

    def run_step(self) -> list[CodeExecutionFeedback | AgentMessage]:
        next_message = self.get_next_message()
        self.history.append(next_message)

        return [next_message, next_message.run_code(self.executor)]

    def run_agent(self) -> None | str:
        while not getattr(self.history[-1], 'finished_successfully', False):
            self.history.extend(self.run_step())
            rich.print(self.history[-1])
            rich.print(self.history[-1])
        return getattr(self.history[-1], 'result', None)

    def run_multiply(self, times: int):
        # create copies of self and run them in parallel
        copies = [deepcopy(self) for _ in range(times)]
        with ThreadPool(times) as pool:
            results = pool.map(lambda agent: (agent.run_agent(), agent), copies)
        agents = [result[1] for result in results]
        return agents, [result[0] for result in results]

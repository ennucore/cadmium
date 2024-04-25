from typing import Optional

from cadmium.core.system_states.util_states import new_goodbye_state
from cadmium.chat.payload import Payload
from cadmium.chat.payloads import (
    PayloadChat,
)
from cadmium.core.system_state import SystemState, SystemStateExecInputs
from cadmium.core.system_states.registry import register_state
from cadmium.sessions.messages import Message
from cadmium.llms.ask import ask_llm, LLMModel, LLMProvider


# see cadmium.core.system_states.start_state
# see cadmium.core.system_states.util_states
# see cadmium.chat.payloads


def new_expand_state():
    return SystemState(inner={"type": "expand"}, f=execute_expand_state)


def execute_expand_state(
    inputs: SystemStateExecInputs,
) -> tuple["SystemState", list[Payload]]:
    """
    This state expects the previous state to have asked for a user input with PayloadOpenChat()
    It takes the last user input and asks an LLM to expand on it
    It sends back the answer as final payload which is persisted in the history
    In between it sends statuses payloads such as PayloadChat with "Thinking..." which is not persisted because not final.
    It transitions to a search state
    """

    prompt = find_prompt(inputs.history)

    inputs.send_payload(PayloadChat("Thinking how to expand your query..."))

    result = ask_llm(
        query=f"""
```
{prompt}
```

Add precision and context to the above internet search query

Answer with only the modified query without text before or after:
""",
        system_prompt="You are a cool LLM. Cool LLMs do what they're asked for.",
        provider=LLMProvider.MISTRAL,
        model=LLMModel.MISTRAL_SMALL,
        temperature=0.0,
    )

    return new_search_state(result), [
        PayloadChat(result),
    ]


register_state("expand", execute_expand_state)


def new_search_state(query: str):
    return SystemState(inner={"type": "search", "query": query}, f=execute_search_state)


def execute_search_state(inputs: SystemStateExecInputs):
    """
    This state expects the previous state to have given it a query
    It asks an online LLM to search for it
    It sends back the answer as a final payload which is persisted in the history
    It transitions to a goodbye state
    """
    query = inputs.inner["query"]

    inputs.send_payload(PayloadChat("Searching..."))

    results = ask_llm(
        query=f"What is {query}?",
        provider=LLMProvider.PPLX,
        model=LLMModel.PPLX_SONAR_MD_ONLINE
    )
    return new_goodbye_state(), [PayloadChat(results)]


register_state("search", execute_search_state)


def find_prompt(history: list[Message]) -> Optional[str]:
    for message in reversed(history):
        if message.is_system:
            continue
        payload = PayloadChat.try_from_dict(message.payload)
        if payload is not None:
            return payload.message
    return None

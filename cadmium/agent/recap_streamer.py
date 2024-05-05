from mistralai.client import MistralClient
import os
from threading import Thread
from dotenv import load_dotenv
from .utils import call_small_model

load_dotenv()
mistral_client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))


def get_new_summary(existing_summaries: list[str], current_streamed_chunk: str):
    prompt = (f'You need to generate status updates to the user based on the work of Cadmium, a 3D agent. '
              f"Example updates that you could generate:\n"
              f"  - STATUS UPDATE: 🔍 Cadmium is analyzing your requirements\n"
              f"  - STATUS UPDATE: ⚙️ Cadmium is creating a gear\n"
              f"  - STATUS UPDATE: 🦿 Cadmium creates a leg of the table\n"
              f"  - STATUS UPDATE: 🤭 Cadmium is fixing a mistake in the code\n"
              f"  - STATUS UPDATE: 📝 Cadmium finalizes the generation of your 3D model\n"
              f"The current work progress of Cadmium is as follows:\n```\n{current_streamed_chunk}\n```\n"
              f"The status updates that were already generated are these:\n```\n{existing_summaries}\n```\n\n\n"
              f"Respond with the next status update for the user, in the format "
              f"'STATUS UPDATE: <update>' (you don't need to have anything else)")
    response = call_small_model(prompt).split('STATUS UPDATE:')[-1].strip().split('\n')[0]
    return response


class RecapStreamer:
    def __init__(self, callback_function=None):
        self.summaries = []
        self.prev_summarize_delta = ''
        self.callback_function = callback_function
        self.last_length = 0

    def stream(self, current_streamed_chunk: str):
        threshold = 450
        if len(current_streamed_chunk.replace(self.prev_summarize_delta, '')) > threshold and (
                len(current_streamed_chunk) - self.last_length > threshold or len(
            current_streamed_chunk) < self.last_length):
            self.prev_summarize_delta = current_streamed_chunk
            self.last_length = len(current_streamed_chunk)
            new_summary = get_new_summary(self.summaries, current_streamed_chunk)
            self.summaries.append(new_summary)
            if self.callback_function:
                self.callback_function(new_summary)
            return new_summary

    def stream_non_blocking(self, current_streamed_chunk: str):
        Thread(target=self.stream, args=(current_streamed_chunk,)).start()

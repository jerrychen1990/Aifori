#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/07/19 15:13:29
@Author  :   ChenHao
@Description  :   
@Contact :   jerrychen1990@gmail.com
'''


from openai import OpenAI
from mem0 import Memory
from snippets import set_logger
logger = set_logger("DEV", __name__)


# Set the OpenAI API key
# os.environ['OPENAI_API_KEY'] = 'sk-xxx'


class PersonalTravelAssistant:
    def __init__(self):
        self.client = OpenAI()
        self.memory = Memory()
        # self.memory.reset()
        self.messages = [{"role": "system", "content": "You are a personal AI Assistant."}]

    def ask_question(self, question, user_id):
        # Fetch previous related memories
        previous_memories = self.search_memories(question, user_id=user_id)
        prompt = question
        if previous_memories:
            prompt = f"User input: {question}\n Previous memories: {previous_memories}"
        self.messages.append({"role": "user", "content": prompt})

        # Generate response using GPT-4o
        logger.info(f"{self.messages=}")
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.messages
        )
        answer = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": answer})

        # Store the question in memory
        self.memory.add(question, user_id=user_id)
        return answer

    def get_memories(self, user_id):
        memories = self.memory.get_all(user_id=user_id)
        return [m['text'] for m in memories]

    def search_memories(self, query, user_id):
        memories = self.memory.search(query, user_id=user_id)
        return [m['text'] for m in memories]


# Usage example
user_id = "traveler_1"
ai_assistant = PersonalTravelAssistant()


def main():
    while True:
        question = input("Question: ")
        if question.lower() in ['q', 'exit']:
            print("Exiting...")
            break

        answer = ai_assistant.ask_question(question, user_id=user_id)
        print(f"Answer: {answer}")
        memories = ai_assistant.get_memories(user_id=user_id)
        print("Memories:")
        for memory in memories:
            print(f"- {memory}")
        print("-----")


if __name__ == "__main__":
    main()

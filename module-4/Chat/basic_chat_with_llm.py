from typing import TypedDict
import uuid

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command, Interrupt
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage, AnyMessage, SystemMessage

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv("../.env")
age = 0

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)

# Define graph state
class State(TypedDict):
    age: int

# Node that asks for human input and validates it
def get_user_input(state: State) -> State:
    prompt = "Please enter your age:"

    while True:
        user_input = input(prompt)

        llm_response = llm.invoke([HumanMessage(content=f'extract the age from the following text: {user_input}')]).content
        # Validate the input
        try:
            age = int(llm_response)
            if age < 0:
                raise ValueError("Age must be non-negative.")
            break  # Valid input received
        except (ValueError, TypeError):
            prompt = f"AI: '{user_input}' is not valid. Please enter a non-negative integer for age.\n >"

    return {"age": age}

def run_interactive_graph():
    # Build the graph
    builder = StateGraph(State)
    builder.add_node("get_user_input", get_user_input)
    builder.set_entry_point("get_user_input")
    builder.add_edge("get_user_input", END)

    graph = builder.compile()

    result = graph.invoke({})
    
    # Print the final result
    print("\nFinal result:", result)

if __name__ == "__main__":
    run_interactive_graph()
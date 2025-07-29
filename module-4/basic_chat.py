from typing import TypedDict
import uuid

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command, Interrupt
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")
age = 0

# Define graph state
class State(TypedDict):
    age: int

# Node that asks for human input and validates it
def get_user_input(state: State) -> State:
    prompt = "Please enter your age:"

    while True:
        user_input = input(prompt)

        if user_input == "quit":
            break

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
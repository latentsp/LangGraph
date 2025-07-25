from typing import TypedDict
import uuid

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command, Interrupt
from langgraph.checkpoint.memory import InMemorySaver

# Define graph state
class State(TypedDict):
    age: int

# Node that asks for human input and validates it
def get_valid_age(state: State) -> State:
    prompt = "Please enter your age:"

    while True:
        user_input = interrupt(prompt)

        # Validate the input
        try:
            age = int(user_input)
            if age < 0:
                raise ValueError("Age must be non-negative.")
            break  # Valid input received
        except (ValueError, TypeError):
            prompt = f"'{user_input}' is not valid. Please enter a non-negative integer for age."

    return {"age": age}

# Node that uses the valid input
def report_age(state: State) -> State:
    print(f"Human is {state['age']} years old.")
    return state

def run_interactive_graph():
    # Build the graph
    builder = StateGraph(State)
    builder.add_node("get_valid_age", get_valid_age)
    builder.add_node("report_age", report_age)

    builder.set_entry_point("get_valid_age")
    builder.add_edge("get_valid_age", "report_age")
    builder.add_edge("report_age", END)

    # Create the graph with a memory checkpointer
    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    # Set up configuration
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    
    # Start the graph
    result = graph.invoke({}, config=config)
    
    # Continue running until we get a valid result (no interrupt)
    while "__interrupt__" in result:
        # Get the interrupt message
        interrupt_obj = result["__interrupt__"]
        if isinstance(interrupt_obj, list):
            interrupt_obj = interrupt_obj[0]
        
        # Print only the value from the interrupt object
        print("\n" + interrupt_obj.value)
        
        # Get user input from command line
        user_input = input("> ")
        
        # Resume the graph with the user's input
        result = graph.invoke(Command(resume=user_input), config=config)
    
    # Print the final result
    print("\nFinal result:", result)

if __name__ == "__main__":
    run_interactive_graph()
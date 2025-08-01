from typing import TypedDict, List, Dict
import uuid

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command, Interrupt
from langgraph.checkpoint.memory import InMemorySaver

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# Define graph state
class State(TypedDict):
    age: int
    messages: List[Dict[str, str]]  # List of message dictionaries with 'role' and 'content'

# Node that asks for human input and validates it
def get_valid_age(state: State) -> State:
    if "messages" not in state:
        state["messages"] = []
    
    prompt = "Please enter your age:"

    while True:
        user_input = interrupt(prompt)
        
        # Add user message to state
        state["messages"].append({"role": "user", "content": user_input})

        # Validate the input
        try:
            age = int(user_input)
            if age < 0:
                raise ValueError("Age must be non-negative.")
            break  # Valid input received
        except (ValueError, TypeError):
            # Use an LLM to explain why the input is invalid and prompt again
            def do_llm_explain_invalid_age(user_input, messages):
                system_prompt = (
                    "You are a helpful assistant. The user was asked to enter their age as a non-negative integer, "
                    "but they entered an invalid value. Kindly explain to the user why their input is not valid."
                )
                user_message = f"The user entered: '{user_input}'."
                response = llm.invoke([
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ])
                
                # Add assistant's response to messages
                messages.append({"role": "assistant", "content": response.content})
                return response.content

            prompt = do_llm_explain_invalid_age(user_input, state["messages"])

    return {"age": age, "messages": state["messages"]}

# Node that uses the valid input
def report_age(state: State) -> State:
    print(f"Human is {state['age']} years old.")
    return state

def run_interactive_graph():
    # Build the graph
    builder = StateGraph(State)
    
    # Initialize the state with empty messages list
    initial_state = {"messages": []}
    
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
    
    # Start the graph with initial state
    result = graph.invoke(initial_state, config=config)
    
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
    load_dotenv("../.env")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)
    print("key: ", openai_api_key)
    run_interactive_graph()
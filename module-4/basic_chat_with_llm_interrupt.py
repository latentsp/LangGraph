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

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)

# Define graph state
class State(TypedDict):
    age: int
    prompt: str
    user_input: str
    validation_error: str

def ask_for_input(state: State) -> State:
    """Ask for user input with current prompt"""
    prompt = state.get("prompt", "Please enter your age:")
    user_input = interrupt(prompt)
    return {"user_input": user_input}

def validate_input(state: State) -> State:
    """Validate the user input using LLM"""
    user_input = state["user_input"]
    
    llm_response = llm.invoke([HumanMessage(content=f'extract the age from the following text: {user_input}')]).content
    print(f"LLM extracted: {llm_response}")
    
    try:
        age = int(llm_response)
        if age < 0:
            raise ValueError("Age must be non-negative.")
        return {"age": age, "validation_error": ""}
    except (ValueError, TypeError):
        error_msg = f"AI: '{user_input}' is not valid. Please enter a non-negative integer for age. LLM extracted: {llm_response}"
        return {"validation_error": error_msg, "prompt": error_msg}

def should_continue(state: State) -> str:
    """Decide whether to continue asking for input or end"""
    if state.get("validation_error"):
        return "ask_for_input"
    return END

def run_interactive_graph():
    # Build the graph
    builder = StateGraph(State)
    builder.add_node("ask_for_input", ask_for_input)
    builder.add_node("validate_input", validate_input)
    
    builder.set_entry_point("ask_for_input")
    builder.add_edge("ask_for_input", "validate_input")
    builder.add_conditional_edges("validate_input", should_continue)

    # Create the graph with a memory checkpointer
    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

   # You can also get ASCII representation
  # You'll need to install: pip install pygraphviz
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        with open("graph.png", "wb") as f:
            f.write(png_data)
        print("Graph saved as graph.png")
    except Exception as e:
        print(f"Could not save PNG: {e}")

    # Set up configuration
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    print("invoking graph for the first time")
    
    # Start the graph
    result = graph.invoke({"prompt": "Please enter your age:"}, config=config)
    
    # Continue running until we get a valid result (no interrupt)
    while "__interrupt__" in result:        
        print("interrupt detected")
        print(result["__interrupt__"])
        
        # Get user input from command line
        user_input = input("> ")
        
        # Resume the graph with the user's input
        result = graph.invoke(Command(resume=user_input), config=config)
    
    # Print the final result
    print("\nFinal result:", result)

if __name__ == "__main__":
    run_interactive_graph()
import uuid

from langgraph.constants import START, END
from langgraph.graph import StateGraph, MessagesState
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage
from typing import Literal

from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv('.env')

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)

# Define graph state using MessagesState
class State(MessagesState):
    age: int

def ask_for_input(state: State) -> State:
    """Ask for user input with current prompt"""
    # Get the most recent message to determine what to ask
    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], AIMessage):
        prompt = messages[-1].content
    else:
        prompt = "Please enter your age:"
    
    user_input = interrupt(prompt)
    return {"messages": [HumanMessage(content=user_input)]}

def validate_input(state: State) -> State:
    """Validate the user input using LLM"""
    # Get the most recent human message
    messages = state.get("messages", [])
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break
    
    if not user_input:
        return {"messages": [AIMessage(content="No input found. Please enter your age:")]}
    
    llm_response = llm.invoke([HumanMessage(content=f'extract the age from the following text: {user_input}')]).content
    print(f"LLM extracted: {llm_response}")
    
    try:
        age = int(llm_response)
        if age < 0:
            raise ValueError("Age must be non-negative.")
        return {"age": age, "messages": [AIMessage(content=f"Great! I've recorded your age as {age}.")]}
    except (ValueError, TypeError):
        error_msg = f"'{user_input}' is not valid. Please enter a non-negative integer for age. LLM extracted: {llm_response}"
        return {"messages": [AIMessage(content=error_msg)]}

def should_continue(state: State) -> Literal["ask_for_input", END]:
    """Decide whether to continue asking for input or end"""
    # If we have a valid age, we can end
    if state.get("age") is not None:
        return END
    else:
        return "ask_for_input"

def run_interactive_graph():
    # Build the graph
    builder = StateGraph(State)
    builder.add_node("ask_for_input", ask_for_input)
    builder.add_node("validate_input", validate_input)

    builder.set_entry_point("ask_for_input")
    builder.add_edge("ask_for_input", "validate_input")
    # This conditional edge allows looping back from validate_input to ask_for_input
    # if should_continue returns "ask_for_input" (i.e., age is not valid)
    builder.add_conditional_edges("validate_input", should_continue)

    # Create the graph with a memory checkpointer
    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

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
    result = graph.invoke({"messages": [AIMessage(content="Please enter your age:")]}, config=config)
    
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
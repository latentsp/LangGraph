import os
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# Define the state structure
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Define the tool for saving user information
@tool
def do_save_user_info(name: str, destination: str, departure_date: str) -> str:
    """Saves the user's travel information.

    Args:
        name: The user's full name.
        destination: The city the user wants to travel to.
        departure_date: The desired date of departure.
    """
    return f"OK! I have saved the following information: Name: {name}, Destination: {destination}, Departure Date: {departure_date}."

def do_setup_agent():
    """Sets up the agent with necessary components."""
    
    # System prompt that defines agent behavior
    prompt = SystemMessage(content="""You are a helpful travel assistant. Your goal is to collect the user's full name, their destination city, and their desired departure date for a flight.

Ask questions to the user to get this information. Be friendly and conversational. Ask one question at a time.

Once you have all three pieces of information (full name, destination, departure date), you MUST call the `do_save_user_info` tool with the collected information.

Do not ask for any other information. After calling the tool, tell the user that the information has been saved and conclude the conversation.
""")

    # Initialize LLM and bind tools
    llm = ChatOpenAI(model="gpt-4")
    llm_with_tools = llm.bind_tools([do_save_user_info])

    def do_run_agent(state: AgentState):
        """Runs the agent LLM to get a response or tool call."""
        messages = [prompt] + state['messages']
        ai_response = llm_with_tools.invoke(messages)
        return {"messages": [ai_response]}

    def do_check_for_tool_calls(state: AgentState):
        """Checks the last message in the state for tool calls."""
        if state["messages"][-1].tool_calls:
            return "action"
        return END

    # Create and configure the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", do_run_agent)
    workflow.add_node("action", ToolNode([do_save_user_info]))
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add edges
    workflow.add_conditional_edges(
        "agent",
        do_check_for_tool_calls,
        {
            "action": "action",
            END: END
        }
    )
    workflow.add_edge('action', 'agent')
    
    return workflow.compile()

graph = do_setup_agent()

from typing import Optional, List, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.types import Command, interrupt

class CustomerInfoState(MessagesState):
    budget: Optional[str]
    project_title: Optional[str]
    interaction_count: int

class CustomerInfo(BaseModel):
     """Information to extract from the user's message."""
     budget: Optional[str] = Field(description="The budget for the project. If not mentioned, leave this field empty.")
     project_title: Optional[str] = Field(description="The title of the project. If not mentioned, leave this field empty.")

extraction_model = ChatOpenAI(model="gpt-4o", temperature=0).with_structured_output(CustomerInfo)

def check_and_route(state: CustomerInfoState) -> Literal["ask_questions", "complete"]:
    """
    Check if we have all required information and decide the next step.
    It also prints the completeness status.
    """
    print("---Checking Information Completeness---")
    
    has_budget = state.get('budget') is not None and state.get('budget', '').strip() != ""
    has_project_title = state.get('project_title') is not None and state.get('project_title', '').strip() != ""
    
    if has_budget and has_project_title:
        print(f"✅ All information collected!")
        print(f"   Budget: {state['budget']}")
        print(f"   Project Title: {state['project_title']}")
        return "complete"
    else:
        missing = []
        if not has_budget:
            missing.append("budget")
        if not has_project_title:
            missing.append("project title")
        print(f"❌ Missing: {', '.join(missing)}")
        return "ask_questions"

def ask_questions(state: CustomerInfoState) -> dict:
    """Ask predefined questions for missing information"""
    print("---Asking Questions---")
    
    interaction_count = state.get('interaction_count', 0) + 1
    
    # Predefined questions
    questions = []
    
    if not state.get('budget') or state.get('budget', '').strip() == "":
        questions.append("💰 What is your budget for this project?")
    
    if not state.get('project_title') or state.get('project_title', '').strip() == "":
        questions.append("📋 What is the title/name of your project?")
    
    question_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
    
    if interaction_count == 1:
        greeting = "Hello! I need to collect some information about your project."
    else:
        greeting = "I still need some additional information."
        
    full_message = f"{greeting}\n\n{question_text}"
    
    print(full_message)
    
    return {
        "messages": [AIMessage(content=full_message)],
        "interaction_count": interaction_count
    }

def collect_info(state: CustomerInfoState) -> dict:
    """Collect information from user response based on the whole conversation."""
    print("---Collecting User Response---")
    location = interrupt()

    if not state.get('messages'):
        return {}
        
    last_message = state['messages'][-1]
    if not isinstance(last_message, HumanMessage):
        return {}

    # Ask the model to fill a form based on the conversation history.
    extracted_info: CustomerInfo = extraction_model.invoke(state['messages'])
    
    updates = {}
    
    # Only update if the field was extracted and is not already set in the state.
    if extracted_info.budget and not state.get("budget"):
        updates["budget"] = extracted_info.budget
        print(f"Extracted budget: {extracted_info.budget}")
    
    if extracted_info.project_title and not state.get("project_title"):
        updates["project_title"] = extracted_info.project_title
        print(f"Extracted project title: {extracted_info.project_title}")
    
    # Don't create a new message, just return the updates
    return updates

def complete(state: CustomerInfoState) -> dict:
    """Final node when all information is collected"""
    print("---Information Collection Complete---")
    
    summary = f"""
                    🎉 Thank you! I've collected all the required information:

                    📋 Project Title: {state['project_title']}
                    💰 Budget: {state['budget']}

                    We can now proceed with your project!
                        """
    
    print(summary)
    
    return {"messages": [AIMessage(content=summary)]}

# Build the graph
builder = StateGraph(CustomerInfoState)

# Add nodes
builder.add_node("ask_questions", ask_questions)
builder.add_node("collect_info", collect_info)
builder.add_node("complete", complete)

# Add edges
builder.add_edge(START, "collect_info")

# Conditional edges from check_info
builder.add_conditional_edges(
    "collect_info",
    check_and_route,  # This returns "ask_questions" or "complete"
    {
        "ask_questions": "ask_questions",
        "complete": "complete"
    }
)

builder.add_edge("ask_questions", "collect_info")

# End at complete
builder.add_edge("complete", END)

# Compile the graph
# The interrupt_after argument is optional and is used to allow for external interruptions after certain nodes.
# If you don't need to interrupt the flow after "ask_questions", you can omit it.
graph = builder.compile()
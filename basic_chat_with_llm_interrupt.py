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
load_dotenv(".env")

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)

# Define graph state using MessagesState
class State(MessagesState):
    company_name: str = None
    person: str = None
    linkedin_data: str = None
    company_website: str = None
    email_content: str = None

def do_ask_for_company_and_person(state: State) -> State:
    """Ask for company name and person name if missing"""
    company_name = state.get("company_name")
    person = state.get("person")
    
    if not company_name and not person:
        prompt = "Please provide both the company name and person name (format: 'Company: [name], Person: [name]'):"
    elif not company_name:
        prompt = "Please provide the company name:"
    elif not person:
        prompt = "Please provide the person name:"
    else:
        return state  # Both are provided
    
    user_input = interrupt(prompt)
    return {"messages": [HumanMessage(content=user_input)]}

def do_validate_company_and_person(state: State) -> State:
    """Validate and extract company name and person from user input"""
    # Get the most recent human message
    messages = state.get("messages", [])
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break
    
    if not user_input:
        return {"messages": [AIMessage(content="No input found. Please try again.")]}
    
    # Use LLM to extract company and person
    extraction_prompt = f"""
    Extract the company name and person name from the following text: '{user_input}'
    
    Return in this exact format:
    Company: [company name]
    Person: [person name]
    
    If only one is provided, still use the format but put 'NOT_PROVIDED' for missing information.
    """
    
    llm_response = llm.invoke([HumanMessage(content=extraction_prompt)]).content
    print(f"🤖 LLM extracted: {llm_response}")
    
    # Parse the LLM response
    company_name = state.get("company_name")
    person = state.get("person")
    
    try:
        lines = llm_response.strip().split('\n')
        for line in lines:
            if line.startswith('Company:'):
                extracted_company = line.replace('Company:', '').strip()
                if extracted_company and extracted_company != 'NOT_PROVIDED':
                    company_name = extracted_company
            elif line.startswith('Person:'):
                extracted_person = line.replace('Person:', '').strip()
                if extracted_person and extracted_person != 'NOT_PROVIDED':
                    person = extracted_person
        
        result = {}
        if company_name:
            result["company_name"] = company_name
        if person:
            result["person"] = person
            
        # Create confirmation message
        if company_name and person:
            result["messages"] = [AIMessage(content=f"Great! Company: {company_name}, Person: {person}")]
        elif company_name:
            result["messages"] = [AIMessage(content=f"Got company: {company_name}. Still need person name.")]
        elif person:
            result["messages"] = [AIMessage(content=f"Got person: {person}. Still need company name.")]
        else:
            result["messages"] = [AIMessage(content="Could not extract company or person. Please try again with format 'Company: [name], Person: [name]'")]
            
        return result
        
    except Exception as e:
        return {"messages": [AIMessage(content=f"Error processing input: {e}. Please try again.")]}

def do_get_linkedin_data(state: State) -> State:
    """Simulate getting LinkedIn data for the person"""
    person = state.get("person")
    
    # Simulate LinkedIn API call with LLM-generated realistic data
    linkedin_prompt = f"""
    Generate realistic professional LinkedIn data for a person named '{person}'.
    Include: job title, company, years of experience, key skills, and education.
    Keep it concise but professional.
    """
    
    linkedin_data = llm.invoke([HumanMessage(content=linkedin_prompt)]).content
    print(f"💼 LinkedIn data retrieved for {person}")
    
    return {
        "linkedin_data": linkedin_data,
        "messages": [AIMessage(content=f"Retrieved LinkedIn data for {person}")]
    }

def do_get_company_website(state: State) -> State:
    """Simulate getting company website information"""
    company_name = state.get("company_name")
    
    # Simulate website scraping with LLM-generated realistic data
    website_prompt = f"""
    Generate realistic company information for '{company_name}'.
    Include: company description, main products/services, company values, and recent news/achievements.
    Keep it concise but informative for email personalization.
    """
    
    company_website = llm.invoke([HumanMessage(content=website_prompt)]).content
    print(f"🌐 Company website data retrieved for {company_name}")
    
    return {
        "company_website": company_website,
        "messages": [AIMessage(content=f"Retrieved website information for {company_name}")]
    }

def do_write_personalized_email(state: State) -> State:
    """Write a personalized email based on LinkedIn and company data"""
    person = state.get("person")
    company_name = state.get("company_name")
    linkedin_data = state.get("linkedin_data")
    company_website = state.get("company_website")
    
    email_prompt = f"""
    Write a personalized business email to {person} at {company_name}.
    
    Person's LinkedIn data:
    {linkedin_data}
    
    Company information:
    {company_website}
    
    The email should be:
    - Professional and personalized
    - Have some emojis
    - Reference specific details from their background
    - Mention something specific about their company
    - Include a clear call-to-action
    - Be concise (under 200 words)
    
    Format as a complete email with subject line.
    sign it off with my name "Jonathan Yarkoni" I am the CEO of LATENT AI
    """
    
    email_content = llm.invoke([HumanMessage(content=email_prompt)]).content
    print("✉️ Personalized email written")
    
    return {
        "email_content": email_content,
        "messages": [AIMessage(content=f"Here's the personalized email:\n\n{email_content}")]
    }

def do_ask_for_approval(state: State) -> State:
    """Ask user if the email is good to send"""
    email_content = state.get("email_content")
    
    # Print the email separately
    print("\n" + "="*60)
    print("📧 GENERATED EMAIL:")
    print("="*60)
    print(email_content)
    print("="*60)
    
    prompt = "Is this email good to send? (yes/no)"
    user_input = interrupt(prompt)
    
    return {"messages": [HumanMessage(content=user_input)]}

def do_validate_approval(state: State) -> State:
    """Validate the user's approval response"""
    # Get the most recent human message
    messages = state.get("messages", [])
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content.lower().strip()
            break
    
    if user_input in ['yes', 'y', 'ok', 'good', 'send']:
        return {"messages": [AIMessage(content="Email approved for sending!")]}
    else:
        return {"messages": [AIMessage(content="Email needs revision. Let me rewrite it...")]}

def do_should_continue_collection(state: State) -> Literal["do_ask_for_company_and_person", "do_get_linkedin_data"]:
    """Decide whether to continue asking for company/person or move to next step"""
    company_name = state.get("company_name")
    person = state.get("person")
    
    if company_name and person:
        return "do_get_linkedin_data"
    else:
        return "do_ask_for_company_and_person"

def do_should_continue_approval(state: State) -> Literal["do_write_personalized_email", END]:
    """Decide whether to rewrite email or end with sending"""
    # Get the most recent human message
    messages = state.get("messages", [])
    user_input = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content.lower().strip()
            break
    
    if user_input in ['yes', 'y', 'ok', 'good', 'send']:
        return END
    else:
        return "do_write_personalized_email"

def do_run_interactive_graph():
    # Build the graph
    builder = StateGraph(State)
    
    # Add all nodes
    builder.add_node("do_ask_for_company_and_person", do_ask_for_company_and_person)
    builder.add_node("do_validate_company_and_person", do_validate_company_and_person)
    builder.add_node("do_get_linkedin_data", do_get_linkedin_data)
    builder.add_node("do_get_company_website", do_get_company_website)
    builder.add_node("do_write_personalized_email", do_write_personalized_email)
    builder.add_node("do_ask_for_approval", do_ask_for_approval)
    builder.add_node("do_validate_approval", do_validate_approval)

    # Set entry point
    builder.set_entry_point("do_ask_for_company_and_person")
    
    # Add edges
    builder.add_edge("do_ask_for_company_and_person", "do_validate_company_and_person")
    builder.add_conditional_edges("do_validate_company_and_person", do_should_continue_collection)
    builder.add_edge("do_get_linkedin_data", "do_get_company_website")
    builder.add_edge("do_get_company_website", "do_write_personalized_email")
    builder.add_edge("do_write_personalized_email", "do_ask_for_approval")
    builder.add_edge("do_ask_for_approval", "do_validate_approval")
    builder.add_conditional_edges("do_validate_approval", do_should_continue_approval)

    # Create the graph with a memory checkpointer
    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    try:
        png_data = graph.get_graph().draw_mermaid_png()
        with open("graph_comp.png", "wb") as f:
            f.write(png_data)
        print("🎨 Graph saved as graph_comp.png")
    except Exception as e:
        print(f"❌ Could not save PNG: {e}")

    # Set up configuration
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    print("🚀 Starting email generation workflow...")
    print("Please state company and person of interest:")
    
    # Start the graph
    result = graph.invoke({"messages": []}, config=config)
    
    # Continue running until we get a valid result (no interrupt)
    while "__interrupt__" in result:        
        
        # Get user input from command line
        user_input = input("> ")
        
        # Resume the graph with the user's input
        result = graph.invoke(Command(resume=user_input), config=config)
    
    # Print the final result
    print("\n🎉 EMAIL SENT! 🎉")

if __name__ == "__main__":
    do_run_interactive_graph()
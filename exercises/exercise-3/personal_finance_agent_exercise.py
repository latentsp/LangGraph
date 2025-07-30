import os
import getpass
from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
from rich import print

# Load environment variables
load_dotenv('.env')

openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=openai_api_key)

# In-memory storage
finance_data = {
    "expenses": [],
    "budgets": {}
}

def add_expense(amount: float, category: str, description: str) -> str:
    """Add an expense to the tracker."""
    expense = {
        "amount": amount,
        "category": category.lower(),
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    finance_data["expenses"].append(expense)
    return f"Added expense: ${amount:.2f} for {description} in {category} category"

def calculate_budget_remaining(category: str) -> str:
    """Calculate remaining budget for a category."""
    category = category.lower()
    
    if category not in finance_data["budgets"]:
        return f"No budget set for {category} category."
    
    budget = finance_data["budgets"][category]
    spent = sum(exp["amount"] for exp in finance_data["expenses"] if exp["category"] == category)
    remaining = budget - spent
    
    return f"Budget: ${budget:.2f}, Spent: ${spent:.2f}, Remaining: ${remaining:.2f}"

def get_spending_summary() -> str:
    """Get spending summary."""
    if not finance_data["expenses"]:
        return "No expenses recorded"
    
    total = sum(exp["amount"] for exp in finance_data["expenses"])
    return f"Total spent: ${total:.2f}"

def set_budget(category: str, amount: float) -> str:
    """Set budget for a category."""
    finance_data["budgets"][category.lower()] = amount
    return f"Set budget for {category}: ${amount:.2f}"

# Tools and agent setup
# TODO: add tools and LLM initialization

sys_msg = SystemMessage(content="You are a personal finance assistant. Help track expenses and budgets.")

def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# TODO: Build graph


# TODO: Compile with memory

if __name__ == "__main__":
    config = {"configurable": {"thread_id": 1}}
    
    # Demo showing memory functionality
    print("🏦 Finance Agent Demo")
    
    # Set budget
    result = finance_agent.invoke({"messages": [HumanMessage("Set food budget to $500")]}, config)
    print(f"User: Set food budget to $500")
    print(f"Agent: {result['messages'][-1].content}\n")
    
    # Add expense
    result = finance_agent.invoke({"messages": [HumanMessage("I spent $45 on groceries")]}, config)
    print(f"User: I spent $45 on groceries")
    print(f"Agent: {result['messages'][-1].content}\n")
    
    # Memory test - reference previous expense
    result = finance_agent.invoke({"messages": [HumanMessage("Check remaining budget after that expense")]}, config)
    print(f"User: Check remaining budget after that expense")
    print(f"Agent: {result['messages'][-1].content}") 

    print(finance_data)
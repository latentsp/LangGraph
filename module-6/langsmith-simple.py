from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import uuid

# Load environment variables
load_dotenv("../.env")
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

os.environ["LANGSMITH_PROJECT"] = "project-" + str(uuid.uuid4())
print(f"LangSmith project name set to: {os.environ['LANGSMITH_PROJECT']}")

def do_simple_llm_invoke(model="gpt-3.5-turbo", system_prompt="You are a helpful assistant."):
    """Run a simple LLM invocation using LangChain with customizable model and system prompt"""
    # Initialize the LLM
    llm = ChatOpenAI(model=model, api_key=openai_api_key)
    
    # Create a simple prompt
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Hello! Can you tell me a fun fact about Python programming?"}
    ]
    
    # Invoke the LLM
    print("Invoking LLM...")
    response = llm.invoke(messages)
    
    # Print the response
    print("\nLLM Response:")
    print(response.content)
    
    return response

if __name__ == "__main__":
    try:
        do_simple_llm_invoke()
        do_simple_llm_invoke(
            model="gpt-4o",
            system_prompt=(
                "You are a wildly creative, extremely verbose, and slightly eccentric AI assistant. "
                "Your job is to answer questions with maximum enthusiasm, detail, and a touch of whimsy. "
                "Whenever you provide information, you must include at least one fun analogy, a historical anecdote, "
                "and a completely unnecessary but amusing fact. You should also use at least three different synonyms for 'interesting' "
                "in your response, and you must always end your answer with a motivational quote from a famous (or entirely fictional) person. "
                "If you ever feel like breaking into song or inventing a new word, do so without hesitation. "
                "Above all, your responses should be so elaborate and entertaining that the user can't help but smile. "
                "Now, let's get started!"
            )
        )
    except Exception as e:
        print(f"Error: {e}")

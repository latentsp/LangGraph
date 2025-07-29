# 🤖 Agent Workshop
Welcome to the **Agent Workshop**! This workshop will guide you through building intelligent AI agents using LangGraph.

## 📋 What You'll Learn

- 🧠 **Agent Fundamentals**: Understanding what agents are and how they work
- 🏗️ **LangGraph Constructs**: Building agent-based AI workflows
- 🔄 **Message Passing & State Management & Memory & HIL**: How agents communicate and manage information
- 💬 **Building Chats**: Creating interactive chatbots and conversational agents
- 🛠️ **LangSmith**: Setting up and exploring features in langSmith

## 🛠️ Prerequisites

Before starting this workshop, make sure you have:

- ✅ Python 3.8+ installed
- ✅ VS Code with python notebooks
- ✅ OpenAI API key
- ✅ Basic Python knowledge
- ✅ Basic familiarity with LangChain

## 🎬 Setup Videos

### 1. 📓 Python Notebook in VS Code
Learn how to work with Jupyter notebooks in VS Code for the best development experience:
**[Watch: Python Notebook in VS Code](https://youtu.be/2FBfy2mgM-0)**

### 2. 🔑 Configuring .env File with OpenAI Key
Set up your environment variables and API keys securely:
**[Watch: Configuring .env File with OpenAI Key](https://youtu.be/-tbfeOBxtIE)**

## ⚡ Quick Start

### Create an environment and install dependencies
#### Mac/Linux/WSL
```
$ python3 -m venv lc-academy-env
$ source lc-academy-env/bin/activate
$ pip install -r requirements.txt
```
#### Windows Powershell
```
PS> python3 -m venv lc-academy-env
PS> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
PS> lc-academy-env\scripts\activate
PS> pip install -r requirements.txt
```

### Setting up env variables
Briefly going over how to set up environment variables. You can also 
use a `.env` file with `python-dotenv` library.

### Running the chatbot to collect human age
To run the chatbot information collection script:

```bash
cd langchain-academy
pip install -r requirements.txt
cd module-3
python 01_chatbot_collect_age.py
```
### Set up LangGraph Studio (Optional)

* LangGraph Studio is a custom IDE for viewing and testing agents.
* Studio can be run locally and opened in your browser on Mac, Windows, and Linux.
* See documentation [here](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/#local-development-server) on the local Studio development server and [here](https://langchain-ai.github.io/langgraph/how-tos/local-studio/#run-the-development-server). 
* Graphs for LangGraph Studio are in the `module-x/studio/` folders.
* To start the local development server, run the following command in your terminal in the `/studio` directory each module:

```
langgraph dev
```

You should see the following output:
```
- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs
```

Open your browser and navigate to the Studio UI: `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`.

* To use Studio, you will need to create a .env file with the relevant API keys
* Run this from the command line to create these files for module 1 to 5, as an example:
```
for i in {1..5}; do
  cp module-$i/studio/.env.example module-$i/studio/.env
  echo "OPENAI_API_KEY=\"$OPENAI_API_KEY\"" > module-$i/studio/.env
done
echo "TAVILY_API_KEY=\"$TAVILY_API_KEY\"" >> module-4/studio/.env
```



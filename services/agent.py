from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

from services.inventory_ai import answer_inventory_question
from services.youtube_rag import ask_video


CURRENT_VIDEO_URL = ""

AGENT_SESSIONS = {}


def set_current_video_url(url):
    global CURRENT_VIDEO_URL
    CURRENT_VIDEO_URL = url


def inventory_tool_func(query):
    return answer_inventory_question(query)


def youtube_tool_func(query):
    global CURRENT_VIDEO_URL

    if not CURRENT_VIDEO_URL:
        return (
            "No YouTube video has been processed yet. "
            "Please process a video first."
        )

    return ask_video(
        CURRENT_VIDEO_URL,
        query
    )


inventory_tool = Tool(
    name="Inventory Search",
    func=inventory_tool_func,
    description="""
    Use this tool for questions about inventory, cards, stock,
    quantities, prices, costs, selling prices, SKUs,
    collections, profit or margins.
    """
)


youtube_tool = Tool(
    name="YouTube Knowledge",
    func=youtube_tool_func,
    description="""
    Use this tool when the user asks about the currently
    processed YouTube video, transcript or video content.
    """
)


llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0
)


def create_kizunai_agent():

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    agent = initialize_agent(
        tools=[
            inventory_tool,
            youtube_tool
        ],
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={
            "prefix": """
You are KizunAI, the AI assistant for Umami Vault.

You help manage and analyze Trading Card Game inventory
and answer questions about processed YouTube videos.

You have access to specialized tools.

IMPORTANT CONVERSATION RULES:

- Always use the previous conversation to understand follow-up questions.

- Understand references such as:
  "that card"
  "that one"
  "which one"
  "the most expensive one"
  "what about its margin?"
  "and the cheapest?"

- If the user previously asked about Pokémon cards and then asks
  "which one is the most expensive?", understand that they mean
  the Pokémon cards discussed previously.

- Use Inventory Search for inventory questions.

- Use YouTube Knowledge for processed video questions.

- Never invent inventory data.

- Be concise, clear and business-focused.
"""
        }
    )

    return agent


def get_agent(thread_id):

    if thread_id not in AGENT_SESSIONS:
        AGENT_SESSIONS[thread_id] = create_kizunai_agent()

    return AGENT_SESSIONS[thread_id]


def ask_agent(question, thread_id="kizunai-main"):

    agent = get_agent(thread_id)

    response = agent.invoke({
        "input": question
    })

    return response["output"]
from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

from services.inventory_ai import answer_inventory_question
from services.youtube_rag import ask_video
from services.sku_generator import generate_sku
from services.currency_converter import convert_currency


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

    return ask_video(CURRENT_VIDEO_URL, query)


def sku_tool_func(query):
    """
    Expected format:
    PRODUCT NAME | RAW OR GRADING COMPANY | GRADE

    Examples:
    Mario Pikachu | Raw
    Charizard | PSA | 10
    Umbreon VMAX | BGS | 9.5
    """

    parts = [part.strip() for part in query.split("|")]

    product_name = parts[0] if len(parts) > 0 else "UNKNOWN"
    raw_or_slab = parts[1] if len(parts) > 1 else "Raw"
    grade = parts[2] if len(parts) > 2 else None

    sku = generate_sku(
        product_name=product_name,
        raw_or_slab=raw_or_slab,
        grade=grade
    )

    return f"Generated SKU: {sku}"


def currency_tool_func(query):
    """
    Expected format:
    AMOUNT | FROM CURRENCY | TO CURRENCY

    Examples:
    5000 | EUR | AED
    430000 | JPY | AED
    1000 | USD | EUR
    """

    parts = [part.strip() for part in query.split("|")]

    if len(parts) != 3:
        return (
            "Invalid currency conversion format. "
            "Use: AMOUNT | FROM CURRENCY | TO CURRENCY"
        )

    amount = parts[0]
    from_currency = parts[1]
    to_currency = parts[2]

    try:
        result = convert_currency(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency
        )

        return (
            f"{result['amount']:,.2f} "
            f"{result['from_currency']} = "
            f"{result['converted_amount']:,.2f} "
            f"{result['to_currency']}. "
            f"Exchange rate: {result['rate']}. "
            f"Rate date: {result['date']}."
        )

    except Exception as error:
        return f"Currency conversion failed: {str(error)}"


inventory_tool = Tool(
    name="Inventory Search",
    func=inventory_tool_func,
    description="""
    Use this tool for questions about inventory, cards, stock,
    quantities, prices, costs, selling prices, SKUs,
    collections, profit or margins.

    Never invent inventory data.
    Always use this tool when the user asks about existing inventory.
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


sku_tool = Tool(
    name="SKU Generator",
    func=sku_tool_func,
    description="""
    Use this tool when the user asks to generate, create,
    preview or suggest a SKU for a TCG product.

    The tool input MUST use this exact format:

    PRODUCT NAME | RAW OR GRADING COMPANY | GRADE

    Examples:

    Mario Pikachu | Raw
    Charizard | PSA | 10
    Umbreon VMAX | BGS | 9.5

    For raw cards, use:
    PRODUCT NAME | Raw
    """
)


currency_tool = Tool(
    name="Currency Converter",
    func=currency_tool_func,
    description="""
    ALWAYS use this tool for ANY currency conversion request.

    This tool retrieves current exchange-rate data from an external API
    and performs the currency conversion.

    NEVER estimate currency conversions using the language model.

    Use this tool whenever the user mentions:
    - converting currencies
    - exchange rates
    - monetary values in different currencies
    - EUR, AED, USD, JPY, GBP or other currency codes

    The tool input MUST use this exact format:

    AMOUNT | FROM CURRENCY | TO CURRENCY

    Examples:

    5000 | EUR | AED
    430000 | JPY | AED
    1000 | USD | EUR
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
            youtube_tool,
            sku_tool,
            currency_tool
        ],
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={
            "prefix": """
You are KizunAI, the AI assistant for Umami Vault.

You help manage and analyze Trading Card Game inventory,
answer questions about processed YouTube videos,
generate inventory SKUs,
and convert currencies using live exchange-rate data.

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

TOOL SELECTION RULES:

- Use Inventory Search for inventory questions.

- Use YouTube Knowledge for processed video questions.

- Use SKU Generator when the user asks to generate,
  create, preview or suggest a SKU.

- Use Currency Converter for every currency conversion request.

CURRENCY RULES:

- You MUST use Currency Converter for every currency conversion request.

- NEVER calculate, estimate or approximate exchange rates yourself.

- NEVER answer a currency conversion from your own model knowledge.

- Currency conversion data must always come from the Currency Converter tool.

- When using Currency Converter, format the tool input as:
  AMOUNT | FROM CURRENCY | TO CURRENCY

- Always use ISO currency codes such as:
  AED, EUR, USD, JPY, GBP.

- After receiving the tool result, report the exact converted amount,
  exchange rate and rate date returned by the tool.

SKU RULES:

- When using SKU Generator, format the tool input as:
  PRODUCT NAME | RAW OR GRADING COMPANY | GRADE

- For raw cards, use:
  PRODUCT NAME | Raw

INVENTORY RULES:

- Never invent inventory data.

- If inventory data is missing, say the inventory does not contain
  enough information.

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

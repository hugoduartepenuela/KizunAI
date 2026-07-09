import re

from langchain.tools import Tool
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

from services.inventory_ai import answer_inventory_question
from services.youtube_rag import ask_video
from services.sku_generator import generate_sku
from services.currency_converter import convert_currency
from services.portfolio_analytics import get_portfolio_summary


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
    parts = [part.strip() for part in query.split("|")]

    if len(parts) != 3:
        return (
            "Invalid currency conversion format. "
            "Use: AMOUNT | FROM CURRENCY | TO CURRENCY"
        )

    amount = parts[0].replace(",", "")
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


def portfolio_tool_func(query):
    return get_portfolio_summary()


inventory_tool = Tool(
    name="Inventory Search",
    func=inventory_tool_func,
    description="""
    Use this tool for specific inventory questions about individual cards,
    products, SKUs, stock, quantities, prices, costs, selling prices,
    collections, profit or margins.

    Do NOT use this tool for total portfolio value calculations.
    Use Portfolio Analytics for total collection value, total cost,
    total profit or portfolio margin.

    Never invent inventory data.
    """
)


youtube_tool = Tool(
    name="YouTube Knowledge",
    func=youtube_tool_func,
    description="""
    Use this tool when the user asks about the currently processed
    YouTube video, transcript or video content.
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

    The tool input MUST use this exact format:

    AMOUNT | FROM CURRENCY | TO CURRENCY

    Examples:

    5000 | EUR | AED
    430000 | JPY | AED
    449260 | AED | EUR
    """
)


portfolio_tool = Tool(
    name="Portfolio Analytics",
    func=portfolio_tool_func,
    description="""
    ALWAYS use this tool for exact portfolio and collection calculations.

    Use this tool for questions about:
    - total collection value
    - portfolio value
    - how much the collection is worth
    - total inventory cost
    - total profit
    - potential profit
    - portfolio margin
    - total margin

    This tool performs deterministic calculations directly from inventory data.
    It is the source of truth for financial inventory totals.
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
            portfolio_tool,
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
calculate portfolio analytics,
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
  "how much is that in EUR?"
  "convert that to euros"

TOOL SELECTION RULES:

- Use Portfolio Analytics for exact total portfolio calculations.

- Use Inventory Search for specific inventory questions about individual cards,
  SKUs, products, quantities or prices.

- Use YouTube Knowledge for processed video questions.

- Use SKU Generator when the user asks to generate,
  create, preview or suggest a SKU.

- Use Currency Converter for every currency conversion request.

PORTFOLIO CALCULATION RULES:

- NEVER calculate total portfolio value yourself.

- NEVER estimate collection value.

- NEVER manually sum inventory prices.

- For total collection value, total portfolio value,
  total inventory cost, total profit or total margin,
  ALWAYS use Portfolio Analytics.

- Portfolio Analytics is the source of truth
  for financial inventory calculations.

- If the user asks to convert the portfolio value
  to another currency:

  1. Use Portfolio Analytics first.
  2. Read the exact AED portfolio value.
  3. Use Currency Converter with that exact value.
  4. Never modify or approximate the AED amount.

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

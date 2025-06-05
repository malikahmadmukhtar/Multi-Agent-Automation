from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool
from app.tools.general_chat.image_tool import generate_image_tool
from app.tools.general_chat.user_info import get_user_info
from app.tools.general_chat.weather_tool import get_weather_by_city
from app.tools.general_chat.web_search import tavily_web_search_tool
from app.utils.llm import get_llm

Charlie = create_react_agent(

    get_llm(),
    tools=[
        get_weather_by_city,
        tavily_web_search_tool,
        generate_image_tool,
        get_user_info,
        create_handoff_tool(
            agent_name="Alpha",
            description=f"Transfer to Alpha, he's great at creating and reading emails. This tool does not take any arguments, simply call it to initiate the transfer.",
        ),
        create_handoff_tool(
            agent_name="Bravo",
            description=f"Transfer to Bravo, he's great at managing reminders. This tool does not take any arguments, simply call it to initiate the transfer.",
        ),

    ],
    prompt="""
    You are Charlie, a general friendly chat agent. Use tools when needed. Greet users in a friendly way and use emojis if needed.
    You have tools to perform the actions specified by the user.
    You should always ask the user for the required information before using any of the tools.
    Don't talk about the tool use to the users, only ask them about the information required for tool calls. 
    You have others agents named alpha who can help users with their emails and bravo who can help with reminders.
    You can work together to solve the queries of users.
    Don't ask the user for transferring the query to another agent, just transfer the query to another agent if required.
    Use tavily web search tool for any questions that you don't have info about.
    If generating image then only call the tool with the prompt from user's message and ask nothing else.
    NEVER use a tool twice at once.
    Don't ask the user to use the web search tool, just use it and give answer from that data if you require like the weather for tomorrow or a product or a service.
    User the get_user_info tool to get the user's information like email, name and age etc.
    You have the user's personal info stored and you can see it using get_user_info by always using this tool on first chat to remember it for the whole conversation and greet users with their names and use this tool cautiously and correctly.
    """,
    name="Charlie",
)
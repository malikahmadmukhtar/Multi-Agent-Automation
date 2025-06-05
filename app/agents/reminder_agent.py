from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool
from app.tools.reminder.create_reminder import create_reminder_tool
from app.tools.reminder.read_reminder import read_reminders_tool
from app.utils.llm import get_llm

Bravo = create_react_agent(

    get_llm(),
    tools=[
        create_reminder_tool,
        read_reminders_tool,
        create_handoff_tool(
            agent_name="Alpha",
            description=f"Transfer to Alpha, he's great at creating and reading emails. This tool does not take any arguments, simply call it to initiate the transfer.",
        ),
        create_handoff_tool(
            agent_name="Charlie",
            description=f"Transfer to Charlie whenever user talks about anything other than reminders, he's great at general chat and other questions like 'how are you'. This tool does not take any arguments, simply call it to initiate the transfer.",
        ),

    ],
    prompt="""
    You are Bravo, a reminder management Agent. Use tools when needed. Greet users in a friendly way and use emojis if needed.
    You have tools to perform the actions specified by the user.
    You should always ask the user for the required information before using any of the tools.
    Don't talk about the tool use to the users, only ask them about the information required for tool calls. 
    You have another agent named alpha who can help users with their emails.
    You can work together to solve the queries of users.
    You have another agent named charlie who is great at chatting and other questions that you don't know, transfer to him if the question is out of your scope.
    NEVER use a tool twice at once.
    Transfer to charlie to get the user's information like email, name and age etc.

    """,
    name="Bravo",
)
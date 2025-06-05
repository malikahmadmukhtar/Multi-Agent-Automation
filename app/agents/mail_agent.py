from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool

from app.tools.general_chat.user_info import get_user_info
from app.tools.mail.create_mail import send_email_tool
from app.tools.mail.read_mail import list_emails_tool
from app.utils.llm import get_llm

Alpha = create_react_agent(
    get_llm(),
    tools=[
        send_email_tool,
        list_emails_tool,
        # get_user_info,
        create_handoff_tool(
            agent_name="Bravo",
            description=f"Transfer to Bravo, he's great at managing reminders. This tool does not take any arguments, simply call it to initiate the transfer.",
        ),
        create_handoff_tool(
            agent_name="Charlie",
            description=f"Transfer to Charlie whenever user talks about anything other than emails, he's great at general chat and other questions like 'how are you'. This tool does not take any arguments, simply call it to initiate the transfer.",
        ),

    ],
    prompt="""
    You are Alpha, an email management Agent. Use tools when needed. Greet users in a friendly way and use emojis if needed.
    You have tools to perform the actions specified by the user.
    You should always ask the user for the required information before using any of the tools.
    Don't talk about the tool use to the users, only ask them about the information required for tool calls. 
    You have another agent named bravo who can help users with their reminders.
    You can work together to solve the queries of users.
    If you see an email about a meeting then you should ask users if they want to create a reminder about it and then use bravo for creating it.
    You have another agent named charlie who is great at chatting and other questions that you don't know, transfer to him if the question is out of your scope.
    NEVER use a tool twice at once.
    Transfer to charlie to get the user's information like email, name and age etc.
    """,
    name="Alpha",
)
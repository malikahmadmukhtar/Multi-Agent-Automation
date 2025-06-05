from langgraph.checkpoint.memory import InMemorySaver
from langgraph_swarm import create_swarm


def create_and_compile_swarm(agents, default_active_agent_name):
    """
    Creates and compiles the LangGraph swarm workflow.
    Requires a list of agents and the name of the default active agent.
    """
    checkpointer = InMemorySaver()
    workflow = create_swarm(agents, default_active_agent=default_active_agent_name)
    app = workflow.compile(checkpointer=checkpointer)
    return app, checkpointer


import logging
import os

from langgraph_sdk import get_sync_client
from langchain_core.messages import convert_to_messages
from kinetica_agent_api_demo.demo_agent import profile_agent

LOG = logging.getLogger(__name__)

test_input = {
            "messages": [{
                "role": "human",
                "content": "What are the female users ordered by username?",
            }],
        }


def test_local_invoke() -> None:
    """ Test the agent using the local API."""

    results = profile_agent.invoke(test_input)
    for idx, message in enumerate(results["messages"]):
        LOG.info(f"{idx}: {message.pretty_repr()}")


def test_local_stream() -> None:
    """ Test the agent using the local streaming API."""

    for event_data in profile_agent.stream(
        input=test_input, 
        stream_mode="updates" # stream only updates
    ):
        for node_name, state_data in event_data.items():
            message_list = state_data["messages"]
            last_message = message_list[-1]
            LOG.info(f"<{node_name},{last_message.type}>: {last_message.content}")


def test_remote_stream() -> None:
    """ Test the agent running from the langsmith server. """
    
    api_key = os.environ["LANGSMITH_API_KEY"]
    client = get_sync_client(url="http://localhost:2024", api_key=api_key)

    for chunk in client.runs.stream(
        thread_id=None,  # Threadless run
        assistant_id="kinetica_agent", # Name of assistant. Defined in langgraph.json.
        input=test_input,
        stream_mode="updates" # stream only updates
    ):
        LOG.info(f"Receiving new event of type: {chunk.event}...")
        if(chunk.event == "updates"):
            for node_name, state_data in chunk.data.items():
                message_list = convert_to_messages(messages=state_data["messages"])
                last_message = message_list[-1]
                LOG.info(f"<{node_name},{last_message.type}>: {last_message.content}")

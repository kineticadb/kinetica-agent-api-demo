# Kinetica Agent API Demo

This project demonstrates how to host a [Kinetica text-to-sql agent][KIN_SQL] with a [LangSmith API server][LS_SERVER]
using the [LangGraph Agent Protocol][LG_PROTO]. This protocol allows for AI Agents to be streamed from multiple remote hosts.

[LS_SERVER]: <https://docs.smith.langchain.com>
[KIN_SQL]: <https://docs.kinetica.com/7.2/sql-gpt/concepts/>
[LG_PROTO]: <https://blog.langchain.dev/agent-protocol-interoperability-for-llm-agents/>

- [Prerequisites](#prerequisites)
- [Environment setup](#environment-setup)
- [Create Test data](#create-test-data)
- [Run and test the LangGraph dev server](#run-and-test-the-langgraph-dev-server)
- [References](#references)

## Prerequisites

To test this project you will need:

- Local python environment with [Python poetry](https://python-poetry.org)
- Kinetica 7.2 instance
- [LangSmith account with API Key](https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key)

## Environment setup

Create and activate a python 3.12 environment. In the below example we are using conda.

```sh
[~/git/kinetica-agent-api-demo]$ conda create --name=agent_demo python=3.12
[~/git/kinetica-agent-api-demo]$ conda activate agent_demo
```

Install the project with poetry.

```sh
(agent_demo) [~/git/kinetica-agent-api-demo]$ poetry install --with test
Installing dependencies from lock file
No dependencies to install or update
Installing the current project: kinetica-agent-api-demo (0.1.0)
```

Create an `.env` file from the `.env.example` file.

```sh
(agent_demo) [~/git/kinetica-agent-api-demo]$ cp .env.example .env
```

Edit the parameters with your LangSmith and Kinetica settings.

```sh
LANGSMITH_API_KEY="lsv2_pt_"
KINETICA_URL="https://demo72.kinetica.com/_gpudb"
KINETICA_USER=admin
KINETICA_PASSWD=
```

## Create Test data

To demonstrate SQL inference this project will create:

- a table `test.user_profiles` containing a set of fake user profiles.
- a SQL context `test.test_profiles_ctx` that can inference the user profiles.

You will need to make sure that the `test` schema exists. After that run the test case to crate the data.

```sh
(agent_demo) [~/git/kinetica-agent-api-demo]$ pytest tests/test_create_data.py
INFO [test_create_data] Creating kinetica context <test.test_profiles_ctx> with table <test.user_profiles>
INFO [test_create_data] Data setup complete!
PASSED                                                                     
```

You can then run a local inference test to make sure everything works.

```sh
(agent_demo) [~/git/kinetica-agent-api-demo]$ pytest tests/test_agent.py::test_local_stream
INFO [test_agent] <kinetica_sql_agent,ai>: [
  {
    "username":"alexander40",
    "name":"Tina Ramirez"
  },
  {
    "username":"bburton",
    "name":"Paula Kaiser"
  },
  {
    "username":"brian12",
    "name":"Stefanie Williams"
  },
  {
    "username":"brownanna",
    "name":"Jennifer Rowe"
  },
  {
    "username":"carl19",
    "name":"Amanda Potts"
  }
]
PASSED
```

## Run and test the LangGraph dev server

The local LangGraph server can be used to the Agent protocol capability. Run the below command to start the server.
It will read `langgraph.json`, host the configured agent locally, and connect it to the LangSmith UI.

```sh
(agent_demo) [~/git/kinetica-agent-api-demo]$ langgraph dev
╦  ┌─┐┌┐┌┌─┐╔═╗┬─┐┌─┐┌─┐┬ ┬
║  ├─┤││││ ┬║ ╦├┬┘├─┤├─┘├─┤
╩═╝┴ ┴┘└┘└─┘╚═╝┴└─┴ ┴┴  ┴ ┴

- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs
```

The command will open a URL in your browser that should direct you to the LangSmith UI where you should see a graph
containing `kinetica_sql_agent`.

You can run the following pytest for an example connection to the remote API.

```sh
(agent_demo) [~/git/kinetica-agent-api-demo]$ pytest tests/test_agent.py::test_remote_stream
INFO [httpx] HTTP Request: POST http://localhost:2024/runs/stream "HTTP/1.1 200 OK"
INFO [test_agent] Receiving new event of type: metadata...
INFO [test_agent] Receiving new event of type: updates...
INFO [test_agent] <kinetica_sql_agent,ai>: [
  {
    "username":"alexander40",
    "name":"Tina Ramirez"  },
  {
    "username":"bburton",
    "name":"Paula Kaiser"
  },
[...]
PASSED
```

The LangGraph server has multiple deployment options. See the following links for more information.

- [LangGraph Server Overview](https://langchain-ai.github.io/langgraph/concepts/langgraph_server/)
- [LangGraph Server Tutorial](https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/)
- [LangGraph Deployment Options](https://langchain-ai.github.io/langgraph/concepts/deployment_options/)
- [Self Hosted Deployment](https://langchain-ai.github.io/langgraph/how-tos/deploy-self-hosted/)

## References

- [LangGraph Agent Protocol](https://blog.langchain.dev/agent-protocol-interoperability-for-llm-agents/)
- [Agent Protocol Github](https://github.com/langchain-ai/agent-protocol?ref=blog.langchain.dev)
- [LangGraph Supervisor Github](https://github.com/langchain-ai/langgraph-supervisor-py/tree/main)
- [Kinetica text-to-sql concepts](https://docs.kinetica.com/7.2/sql-gpt/concepts/)

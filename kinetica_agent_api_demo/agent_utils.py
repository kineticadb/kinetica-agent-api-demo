""" Utilities for Kinetica SQL Agent """

from gpudb import GPUdb
from typing import Any, List
from pydantic import ConfigDict, Field


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.transform import BaseOutputParser
from langchain_core.outputs import Generation
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt.chat_agent_executor import AgentState

from langchain_community.chat_models.kinetica import ChatKinetica, KineticaSqlResponse


class KineticaJsonOutputParser(BaseOutputParser[str]):

    kdbc: Any = Field(exclude=True)
    """ Kinetica DB connection. """

    max_results: int = Field(exclude=True, default=10)
    """ Maximum number of results to return. """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def parse(self, text: str) -> KineticaSqlResponse:
        df = self.kdbc.to_df(text)
        json_str = df.head(self.max_results).to_json(orient='records', indent=2)
        return json_str

    def parse_result(
        self, result: List[Generation], *, partial: bool = False
    ) -> KineticaSqlResponse:
        return self.parse(result[0].text)

    @property
    def _type(self) -> str:
        return "kinetica_json_output_parser"


def create_kinetica_chain(kdbc: GPUdb, 
                          context_name: str,
                          max_results = 10) -> Any:
    kinetica_llm = ChatKinetica(kdbc=kdbc)
    
    # load the context from the database
    ctx_messages = kinetica_llm.load_messages_from_context(context_name)

    # Add the input prompt. This is where input question will be substituted.
    ctx_messages.append(("human", "{input}"))

    # Create the prompt template.
    prompt_template = ChatPromptTemplate.from_messages(ctx_messages)

    parser = KineticaJsonOutputParser(kdbc=kinetica_llm.kdbc, max_results=max_results)
    chain = prompt_template | kinetica_llm | parser
    return chain


def create_kinetica_agent(kdbc: GPUdb, 
                     name: str,
                     context_name: str,
                     max_results: int = 10) -> CompiledStateGraph:
    kinetica_chain = create_kinetica_chain(
        kdbc=kdbc, 
        context_name=context_name,
        max_results = max_results)

    def kinetica_chatbot(state: AgentState) -> dict[str, list[AIMessage]]:
        input_message: HumanMessage = None
        for message in reversed(state["messages"]):
            if isinstance(message, HumanMessage):
                input_message = message
                break

        if input_message is None:
            raise ValueError("No input HumanMessage found")
        
        resp_json = kinetica_chain.invoke({"input": input_message.content})
        return {"messages": [AIMessage(content=resp_json)]}
    

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("kinetica_sql_agent", kinetica_chatbot)
    graph_builder.add_edge(START, "kinetica_sql_agent")
    graph_builder.add_edge("kinetica_sql_agent", END)

    graph = graph_builder.compile(name=name)
    return graph


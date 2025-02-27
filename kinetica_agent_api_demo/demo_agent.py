""" Implementation of Kinetica agent for the Lansmith Server. """

from typing import Any
from gpudb import GPUdb

from kinetica_agent_api_demo.agent_utils import create_kinetica_agent

# Kinetica SQL context (must exist)
kinetica_ctx = "test.test_profiles_ctx"

agent_name = "profile_expert"

kdbc = GPUdb.get_connection()
profile_agent = create_kinetica_agent(kdbc, 
                                name=agent_name, 
                                context_name=kinetica_ctx,
                                max_results=5)

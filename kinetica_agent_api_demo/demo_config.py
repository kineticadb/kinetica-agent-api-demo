""" Configuration for the agent demo """

# Kinetica schemathis must exist
agent_schema = "cjuliano_kinetica"

# Kinetica SQL context
kinetica_ctx = f"{agent_schema}.test_profiles_ctx"

# Table containing fake user profiles
table_name = f"{agent_schema}.user_profiles"

import logging
from typing import Generator
import pandas as pd
from faker import Faker
from gpudb import GPUdb, GPUdbTable

from kinetica_agent_api_demo.demo_config import kinetica_ctx, table_name

LOG = logging.getLogger(__name__)

def test_create_sql_context():
    kdbc = GPUdb.get_connection()

    Faker.seed(5467)
    faker = Faker(locale="en-US")

    def profile_gen(count: int) -> Generator:
        for id in range(0, count):
            rec = dict(id=id, **faker.simple_profile())
            rec["birthdate"] = pd.Timestamp(rec["birthdate"])
            yield rec

    load_df = pd.DataFrame.from_records(data=profile_gen(100), index="id")
    LOG.info(load_df.head())

    gpudb_table = GPUdbTable.from_df(
        load_df,
        db=kdbc,
        table_name=table_name,
        clear_table=True,
        load_data=True,
    )

    # See the Kinetica column types
    LOG.info(gpudb_table.type_as_df())


    LOG.info(f'Creating kinetica context <{kinetica_ctx}> with table <{table_name}>')

    sql = f"""
    CREATE OR REPLACE CONTEXT {kinetica_ctx}
    (
        TABLE = {table_name}
        COMMENT = 'Contains user profiles.'
    ),
    (
        SAMPLES = (
        'How many male users are there?' = 
        'select count(1) as num_users
        from {table_name}
        where sex = ''M'';')
    )
    """

    response = kdbc.execute_sql(sql)
    GPUdb._check_error(response)
    
    LOG.info("Data setup complete!")

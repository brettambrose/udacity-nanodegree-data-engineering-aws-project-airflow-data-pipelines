from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

"""
Operator that can perform ETL between two tables in the same
Redshift database using dynamic SQL. Intended to load FACT
tables in a Data Warehouse.

Args:
    redshift_conn_id (string): Airflow Redshift connection key
    table (string): target table for INSERT INTO statement
    sql (string): SELECT query source source data insert
"""

class LoadFactOperator(BaseOperator):
    ui_color = '#F98866'
    insert_sql = """ 
    INSERT INTO {} 
    {}
    """

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 table="",
                 sql="",
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.sql = sql

    def execute(self, context):
        self.log.info("Establishing Hooks...")
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        formatted_sql = LoadFactOperator.insert_sql.format(
            self.table,
            self.sql
        )
        self.log.info(f"Loading {self.table} fact table...")
        redshift.run(formatted_sql)

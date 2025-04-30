from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

"""
TODO: Summary

TODO: Args
"""

class LoadDimensionOperator(BaseOperator):
    ui_color = '#80BD9E'
    insert_sql = """
    INSERT INTO {}
    {};
    """
    truncate_sql = """
    TRUNCATE TABLE {};
    """

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 table="",
                 sql="",
                 opt_truncate=False,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.sql = sql
        self.opt_truncate = opt_truncate

    def execute(self, context):
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        if self.opt_truncate:
            formatted_sql = LoadDimensionOperator.truncate_sql.format(
                self.table
            )
            self.log.info(f"truncating {self.table}...")
            redshift.run(formatted_sql)

        formatted_sql = LoadDimensionOperator.insert_sql.format(
            self.table,
            self.sql
        )

        self.log.info(f"loading {self.table}...")
        redshift.run(formatted_sql)

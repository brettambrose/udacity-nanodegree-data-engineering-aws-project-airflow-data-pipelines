from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

"""
Operator that loops through a list of custom data quality rules
 applied to tables in a Redshift database. Intended to run
 SQL queries and check against expected results.

Args:
    redshift_conn_id (string): Airflow Redshift connection key
    rule_list (list(dict)): dynamic list of dicts formatted as:
        {
            "id": int, -- rule identifier
            "exp_result: int, -- record count expected
            "query": "" -- SELECT COUNT(1) query based on condition
        }
"""

class DataQualityOperator(BaseOperator):
    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 rule_list=[],
                 *args, **kwargs):

        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.rule_list = rule_list

    def execute(self, context):
        self.log.info("Establishing Hooks...")
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        self.log.info("Executing data quality rules...")
        for rule in self.rule_list:
            id = rule.get("id")
            exp_result = rule.get("exp_result")
            query = rule.get("query")

            self.log.info(f"Executing RULE {id}: {query}")
            raw_result = redshift.get_records(query)
            result = raw_result[0][0]

            if result != exp_result:
                raise ValueError(f"FAILED: actual result={result} != expected result={exp_result}")
            else:
                self.log.info(f"PASSED: actual result={result} == expected result={exp_result}")
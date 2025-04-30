from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

"""
TODO: Summary

TODO: Args
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
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        self.log.info("executing data quality rules...")

        for rule in self.rule_list:
            id = rule.get("id")
            rule_type = rule.get("type")
            exp_result = rule.get("exp_result")
            query = rule.get("query")

            raw_result = redshift.get_records(query)
            result = raw_result[0][0]

            if rule_type == "condition":
                if result != int(exp_result):
                    raise ValueError(f"RULE {id} FAILED: exp result={exp_result} | actual result={result}")
                else:
                    self.log.info(f"RULE {id} PASSED: exp result={exp_result} | actual result={result}")
            
            if rule_type == "checksum":
                if result <= 0:
                    raise ValueError(f"RULE {id} FAILED: {query} returned 0 records")
                else:
                    self.log.info(f"RULE {id} PASSED: {query} returned > 0 records")
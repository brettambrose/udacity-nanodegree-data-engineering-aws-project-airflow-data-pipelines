from datetime import datetime, timedelta
import pendulum
import os
from airflow.decorators import dag
from airflow.operators.dummy import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from operators import (StageToRedshiftOperator, LoadFactOperator,
                       LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

from udacity.common import sql_statements

default_args = {
    'owner': 'udacity',
    'start_date': pendulum.now(),
}

@dag(
    default_args=default_args,
    description='Load and transform data in Redshift with Airflow',
    schedule_interval='0 * * * *'
)
def final_project():

    start_operator = DummyOperator(task_id='Begin_execution')

    # DROP EXISTING TABLES
    drop_staging_events = PostgresOperator(
        task_id="drop_staging_events",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.DROP_STAGING_EVENTS_SQL
    )

    drop_staging_songs = PostgresOperator(
        task_id="drop_staging_songs",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.DROP_STAGING_SONGS_SQL
    )

    drop_table_artists = PostgresOperator(
        task_id="drop_table_artists",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.DROP_TABLE_ARTISTS_SQL
    )

    drop_table_songplays = PostgresOperator(
        task_id="drop_table_songplays",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.DROP_TABLE_SONGPLAYS_SQL
    )

    drop_table_songs = PostgresOperator(
        task_id="drop_table_songs",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.DROP_TABLE_SONGS_SQL
    )

    drop_table_time = PostgresOperator(
        task_id="drop_table_time",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.DROP_TABLE_TIME_SQL
    )

    drop_table_users = PostgresOperator(
        task_id="drop_table_users",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.DROP_TABLE_USERS_SQL
    )

    # RECREATE TABLES
    create_staging_events = PostgresOperator(
        task_id="create_staging_events",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.CREATE_STAGING_EVENTS_SQL
    )

    create_staging_songs = PostgresOperator(
        task_id="create_staging_songs",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.CREATE_STAGING_SONGS_SQL
    )

    create_table_artists = PostgresOperator(
        task_id="create_table_artists",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.CREATE_TABLE_ARTISTS_SQL
    )

    create_table_songplays = PostgresOperator(
        task_id="create_table_songplays",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.CREATE_TABLE_SONGPLAYS_SQL
    )

    create_table_songs = PostgresOperator(
        task_id="create_table_songs",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.CREATE_TABLE_SONGS_SQL
    )

    create_table_time = PostgresOperator(
        task_id="create_table_time",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.CREATE_TABLE_TIME_SQL
    )

    create_table_users = PostgresOperator(
        task_id="create_table_users",
        postgres_conn_id="aws_redshift",
        sql=sql_statements.CREATE_TABLE_USERS_SQL
    )

    stage_events_to_redshift = StageToRedshiftOperator(
        task_id='Stage_events',
    )

    stage_songs_to_redshift = StageToRedshiftOperator(
        task_id='Stage_songs',
    )

    load_songplays_table = LoadFactOperator(
        task_id='Load_songplays_fact_table',
    )

    load_user_dimension_table = LoadDimensionOperator(
        task_id='Load_user_dim_table',
    )

    load_song_dimension_table = LoadDimensionOperator(
        task_id='Load_song_dim_table',
    )

    load_artist_dimension_table = LoadDimensionOperator(
        task_id='Load_artist_dim_table',
    )

    load_time_dimension_table = LoadDimensionOperator(
        task_id='Load_time_dim_table',
    )

    run_quality_checks = DataQualityOperator(
        task_id='Run_data_quality_checks',
    )

final_project_dag = final_project()

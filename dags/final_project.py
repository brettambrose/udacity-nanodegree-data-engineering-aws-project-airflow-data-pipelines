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

"""
Default Args - if passed to a DAG, it will apply
 default_args to any operator as long as 
 @apply_defaults caller is present

The DAG does not have dependencies on past runs
On failure, the task are retried 3 times
Retries happen every 5 minutes
Catchup is turned off
Do not email on retry
"""

default_args = {
    "start_date": pendulum.now(),
    "retries": 3,
    "email_on_retry": False,
    "retry_detail": timedelta(minutes=5),
    "depends_on_past": False,
    "catchup": False
}

@dag(
    default_args=default_args,
    description='Load and transform data in Redshift with Airflow',
    schedule_interval=None
)

def final_project():

    start_operator = DummyOperator(task_id='Begin_execution')

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
        table="staging_events",
        redshift_conn_id="aws_redshift",
        aws_credentials_id="aws_credentials",
        s3_bucket="udacity-dend",
        s3_key="log_data",
        region="us-west-2",
        file_format="JSON",
        format_spec="s3://udacity-dend/log_json_path.json"
    )

    stage_songs_to_redshift = StageToRedshiftOperator(
        task_id='Stage_songs',
        table="staging_songs",
        redshift_conn_id="aws_redshift",
        aws_credentials_id="aws_credentials",
        s3_bucket="udacity-dend",
        s3_key="song-data",
        region="us-west-2",
        file_format="JSON",
        format_spec="auto"
    )

    load_songplays_table = LoadFactOperator(
        task_id='Load_songplays_fact_table',
        redshift_conn_id="aws_redshift",
        table="songplays",
        sql=SqlQueries.songplay_table_insert
    )

    load_user_dimension_table = LoadDimensionOperator(
        task_id='Load_user_dim_table',
        redshift_conn_id="aws_redshift",
        table="songplays",
        sql=SqlQueries.user_table_insert,
        opt_truncate=True
    )

    load_song_dimension_table = LoadDimensionOperator(
        task_id='Load_song_dim_table',
        redshift_conn_id="aws_redshift",
        table="songplays",
        sql=SqlQueries.song_table_insert,
        opt_truncate=True
    )

    load_artist_dimension_table = LoadDimensionOperator(
        task_id='Load_artist_dim_table',
        redshift_conn_id="aws_redshift",
        table="songplays",
        sql=SqlQueries.artist_table_insert,
        opt_truncate=True
    )

    load_time_dimension_table = LoadDimensionOperator(
        task_id='Load_time_dim_table',
        redshift_conn_id="aws_redshift",
        table="songplays",
        sql=SqlQueries.time_table_insert,
        opt_truncate=True
    )

    run_quality_checks = DataQualityOperator(
        task_id='Run_data_quality_checks',
    )

    end_operator = DummyOperator(task_id='End_execution')

    start_operator >> [drop_staging_events, drop_staging_songs, drop_table_artists, drop_table_songplays, drop_table_songs, drop_table_users, drop_table_time]
    drop_staging_events >> create_staging_events >> stage_events_to_redshift
    drop_staging_songs >> create_staging_songs >> stage_songs_to_redshift
    drop_table_songplays >> create_table_songplays >> load_songplays_table
    load_songplays_table << [stage_events_to_redshift, stage_songs_to_redshift]
    load_songplays_table >> [load_artist_dimension_table, load_song_dimension_table, load_user_dimension_table, load_time_dimension_table]
    drop_table_artists >> create_table_artists >> load_artist_dimension_table
    drop_table_songs >> create_table_songs >> load_song_dimension_table
    drop_table_users >> create_table_users >> load_user_dimension_table
    drop_table_time >> create_table_time >> load_time_dimension_table
    run_quality_checks << [load_songplays_table, load_artist_dimension_table, load_song_dimension_table, load_user_dimension_table, load_time_dimension_table]
    run_quality_checks >> end_operator

final_project_dag = final_project()
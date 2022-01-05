from airflow import DAG
from datetime import datetime, timedelta
from airflow.models import Variable
from airflow.operators.docker_operator import DockerOperator

now = datetime.now()
DATE_FORMAT = "%Y-%m-%d"

default_args = {
        'owner': 'airflow',
        'start_date': datetime(2020, 1, 12, 0, 0),
        #'end_date'              : now.strftime(DATE_FORMAT),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
}

dbt = Variable.get("dbt", deserialize_json=False)


with DAG('dbt_run', default_args=default_args, schedule_interval=None, catchup=False) as dag:
    date = now.strftime(DATE_FORMAT)
    dbt = DockerOperator(
        task_id='dbt',
        image='iiidata_docker_dbt',
        auto_remove=True,
        command=f'compile --vars \'{dbt}\'',
        docker_url='tcp://docker-proxy:2375',
        network_mode='host'
    )
    dbt

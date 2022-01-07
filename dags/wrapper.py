from airflow import DAG
from datetime import datetime, timedelta
from airflow.models import Variable
from airflow.operators.docker_operator import DockerOperator
from docker.types import Mount
import logging
now = datetime.now()
DATE_FORMAT = "%Y-%m-%d_%H-%M"

default_args = {
        'owner': 'airflow',
        'start_date': datetime(2020, 1, 12, 0, 0),
        #'end_date'              : now.strftime(DATE_FORMAT),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
}

files_path = Variable.get("referential_files", deserialize_json=True)
# external sensor devraient verifier quie les job dim_quotien et dim_hebdo sont bien finis

with DAG('wrapper', default_args=default_args, schedule_interval='*/30 * * * *', catchup=False) as dag:
    date = now.strftime(DATE_FORMAT)
    logging.info(files_path)
    get_semitag_stop_times = DockerOperator(
        task_id='get_semitag_stop_times',
        image='cours_wrappers',
        container_name=f'get_semitag_stop_times-{date}',
        auto_remove=True,
        docker_url='tcp://docker-proxy:2375',
        network_mode='host',
        mounts=[
            Mount(
                source=files_path.get("data"),
                target='/data',
                type='bind'
            ),
            Mount(
                source=files_path.get("log"),
                target='/logs',
                type='bind'
            )
        ]
    )
    get_semitag_stop_times

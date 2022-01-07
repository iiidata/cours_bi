from airflow import DAG
from datetime import datetime, timedelta
from airflow.models import Variable
from airflow.operators.docker_operator import DockerOperator
from docker.types import Mount

now = datetime.now()
DATE_FORMAT = "%Y-%m-%d' '%H:%M"

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

with DAG('call_wrapper', default_args=default_args, schedule_interval=None, catchup=False) as dag:
    date = now.strftime(DATE_FORMAT)
    cours_wrappers = DockerOperator(
        task_id='cours_wrappers',
        image='cours_wrappers',
        container_name=f'cours_wrappers-{date}',
        auto_remove=True,
        docker_url='tcp://docker-proxy:2375',
        network_mode='host',
        mounts=[
            Mount(
                source=files_path.get("data"),
                target='/data',
                type='bind'
            )
        ]
    )
    cours_wrappers

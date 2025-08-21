from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
import datetime
#from airflow.utils.dates import days_ago
from base_path import get_base_path

DAG_ID = "build_container_image"
SECOPS_WAREHOUSE_PATH= f"{get_base_path()}/secops-warehouse"

default_args = {
    'owner': 'security',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=1),
}

with DAG(
    dag_id=DAG_ID,
    schedule_interval=None,
    default_args=default_args,
    catchup=False,
    tags=['build', 'container', 'images'],
    doc_md="""
    # Build Container Images
    """
) as dag:

    build_image = KubernetesPodOperator(
        task_id='build_hello_world_with_kaniko',
        name='kaniko-build',
        namespace='orchestrix',  # your Airflow namespace
        image='gcr.io/kaniko-project/executor:latest',
        image_pull_secrets=[{"name": "spr-nexus"}],
        cmds=["/kaniko/executor"],
        arguments=[
            f"--context={SECOPS_WAREHOUSE_PATH}",
            "--dockerfile=build_container_image/Dockerfile",  # relative to context
            "--destination=prod-nexus.sprinklr.com:8123/hello-world:v1",
        ],
        get_logs=True,
        is_delete_operator_pod=True,
        in_cluster=True,
    )

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from datetime import datetime

with DAG(
    dag_id="kpo_build_image",
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    build = KubernetesPodOperator(
        task_id="build_image",
        name="kaniko-build",
        namespace="default",
        image="gcr.io/kaniko-project/executor:latest",   # Kaniko builder
        cmds=["/kaniko/executor"],
        arguments=[
            "--dockerfile=/workspace/Dockerfile",
            "--context=git://github.com/your-org/your-repo.git",  # or /workspace mount
            "--destination=your-dockerhub-user/hello-world:latest"
        ],
        volume_mounts=[{
            "name": "docker-config",
            "mountPath": "/kaniko/.docker/"
        }],
        volumes=[{
            "name": "docker-config",
            "secret": {"secretName": "docker-registry-secret"}
        }],
        is_delete_operator_pod=True,
    )


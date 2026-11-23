
import subprocess
from pathlib import Path

from prefect import flow, task, get_run_logger


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

DBT_PROJECT_DIR = Path(__file__).resolve().parent


# --------------------------------------------------
# TASK 1: VALIDATE PROJECT
# --------------------------------------------------

@task(name="Validate dbt Project")
def validate_project():

    logger = get_run_logger()

    dbt_config = DBT_PROJECT_DIR / "dbt_project.yml"

    if not dbt_config.exists():
        raise FileNotFoundError("dbt_project.yml not found.")

    logger.info("dbt project validated.")
    logger.info(f"Project directory: {DBT_PROJECT_DIR}")

    return True


# --------------------------------------------------
# TASK 2: BUILD AND TEST DBT
# --------------------------------------------------

@task(
    name="Build and Test dbt Models",
    retries=1,
    retry_delay_seconds=10
)
def run_dbt_build():

    logger = get_run_logger()

    command = [
        "dbt",
        "build",
        "--project-dir",
        str(DBT_PROJECT_DIR),
        "--static-analysis",
        "strict"
    ]

    logger.info("Starting dbt build and tests...")

    result = subprocess.run(
        command,
        cwd=DBT_PROJECT_DIR,
        capture_output=True,
        text=True
    )

    logger.info(result.stdout)

    if result.stderr:
        logger.warning(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"dbt build failed: {result.returncode}"
        )

    logger.info("dbt build and tests completed successfully.")

    return True


# --------------------------------------------------
# MAIN PREFECT FLOW
# --------------------------------------------------

@flow(name="VC Deal Flow Intelligence Pipeline")
def vc_deal_flow_pipeline():

    logger = get_run_logger()

    logger.info("Starting VC Deal Flow pipeline.")

    validate_project()

    run_dbt_build()

    logger.info("VC Deal Flow pipeline completed successfully.")


# --------------------------------------------------
# EXECUTION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    vc_deal_flow_pipeline()

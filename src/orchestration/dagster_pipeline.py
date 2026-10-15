from dagster import (
    asset,
    Definitions,
    define_asset_job,
    RetryPolicy,
    ScheduleDefinition,
    DefaultScheduleStatus,
)

from src.orchestration.database_transformations import run_database_transformations
from src.orchestration.database_source import get_transaction_count
from src.orchestration.data_quality import validate_transactions




@asset
def transaction_count():
    return get_transaction_count()


@asset
def validated_transactions(transaction_count):
    validate_transactions()
    return transaction_count


@asset(retry_policy=RetryPolicy(max_retries=2, delay=2))
def pyspark_transformation(validated_transactions):
    result = run_database_transformations()
    return result
@asset
def publish_report(pyspark_transformation):
    import json
    from pathlib import Path

    report_path = Path("output") / "dagster_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "pipeline_status": "SUCCESS",
        "total_transactions": pyspark_transformation["total_transactions"],
        "credit_transactions": pyspark_transformation["credit_transactions"],
        "high_value_transactions": pyspark_transformation["high_value_transactions"],
    }

    with report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print(f"Report published: {report_path.resolve()}")
    return report

banking_pipeline_job = define_asset_job(
    name="banking_pipeline_job",
    description="Run the banking data pipeline",
)
banking_daily_schedule = ScheduleDefinition(
    job=banking_pipeline_job,
    cron_schedule="0 6 * * *",
    default_status=DefaultScheduleStatus.STOPPED,
)

defs = Definitions(
    assets=[
    transaction_count,
    validated_transactions,
    pyspark_transformation,
    publish_report,
],
    jobs=[banking_pipeline_job],
    schedules=[banking_daily_schedule],
)

if __name__ == "__main__":
    result = defs.resolve_job_def("banking_pipeline_job").execute_in_process()
    print("Pipeline successful:", result.success)
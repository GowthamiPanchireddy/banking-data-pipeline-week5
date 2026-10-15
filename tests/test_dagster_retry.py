from dagster import (
    DagsterInstance,
    Definitions,
    RetryPolicy,
    asset,
    define_asset_job,
)

attempts = {"count": 0}


@asset(retry_policy=RetryPolicy(max_retries=2, delay=1))
def retry_test_asset(context):
    attempts["count"] += 1

    context.log.info(
        f"Attempt number: {attempts['count']}"
    )

    if attempts["count"] == 1:
        raise ValueError("Temporary test failure")

    return "Success after retry"


retry_test_job = define_asset_job(
    name="retry_test_job",
)

retry_test_defs = Definitions(
    assets=[retry_test_asset],
    jobs=[retry_test_job],
)


def test_dagster_retries_after_failure():
    attempts["count"] = 0

    with DagsterInstance.ephemeral() as instance:
        result = retry_test_defs.resolve_job_def(
            "retry_test_job"
        ).execute_in_process(
            instance=instance,
            raise_on_error=False,
        )

    assert result.success
    assert attempts["count"] == 2
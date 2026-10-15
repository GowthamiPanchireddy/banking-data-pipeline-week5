import json

from dagster import DagsterInstance, Definitions, asset

import src.orchestration.dagster_pipeline as pipeline


def test_dagster_job_success(monkeypatch, tmp_path):
    report_path = tmp_path / "dagster_report.json"

    monkeypatch.setattr(
        pipeline,
        "get_transaction_count",
        lambda: 2,
    )

    monkeypatch.setattr(
        pipeline,
        "validate_transactions",
        lambda: True,
    )

    monkeypatch.setattr(
        pipeline,
        "run_database_transformations",
        lambda: {
            "total_transactions": 2,
            "credit_transactions": 1,
            "high_value_transactions": 1,
        },
    )

    @asset
    def test_report(pyspark_transformation):
        report = {
            "pipeline_status": "SUCCESS",
            **pyspark_transformation,
        }

        report_path.write_text(
            json.dumps(report, indent=4),
            encoding="utf-8",
        )

        return report

    test_job = pipeline.define_asset_job(
        name="test_banking_pipeline_job",
    )

    test_defs = Definitions(
        assets=[
            pipeline.transaction_count,
            pipeline.validated_transactions,
            pipeline.pyspark_transformation,
            test_report,
        ],
        jobs=[test_job],
    )

    with DagsterInstance.ephemeral() as instance:
        result = test_defs.resolve_job_def(
            "test_banking_pipeline_job"
        ).execute_in_process(instance=instance)

    assert result.success
    assert report_path.exists()

    report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    assert report["pipeline_status"] == "SUCCESS"
    assert report["total_transactions"] == 2
    assert report["credit_transactions"] == 1
    assert report["high_value_transactions"] == 1


def test_validation_failure_blocks_downstream(monkeypatch):
    downstream_called = False

    monkeypatch.setattr(
        pipeline,
        "get_transaction_count",
        lambda: 2,
    )

    def fail_validation():
        raise ValueError(
            "Validation failed: invalid transactions found"
        )

    def should_not_run():
        nonlocal downstream_called
        downstream_called = True

        raise AssertionError(
            "Downstream transformation should not run"
        )

    monkeypatch.setattr(
        pipeline,
        "validate_transactions",
        fail_validation,
    )

    monkeypatch.setattr(
        pipeline,
        "run_database_transformations",
        should_not_run,
    )

    with DagsterInstance.ephemeral() as instance:
        result = pipeline.defs.resolve_job_def(
            "banking_pipeline_job"
        ).execute_in_process(
            instance=instance,
            raise_on_error=False,
        )

    assert not result.success
    assert not downstream_called


def test_report_rerun_overwrites_old_report(monkeypatch, tmp_path):
    report_path = tmp_path / "dagster_report.json"

    current_count = {"value": 2}

    monkeypatch.setattr(
        pipeline,
        "get_transaction_count",
        lambda: current_count["value"],
    )

    monkeypatch.setattr(
        pipeline,
        "validate_transactions",
        lambda: True,
    )

    monkeypatch.setattr(
        pipeline,
        "run_database_transformations",
        lambda: {
            "total_transactions": current_count["value"],
            "credit_transactions": 1,
            "high_value_transactions": 0,
        },
    )

    @asset
    def test_report(pyspark_transformation):
        report = {
            "pipeline_status": "SUCCESS",
            **pyspark_transformation,
        }

        report_path.write_text(
            json.dumps(report, indent=4),
            encoding="utf-8",
        )

        return report

    test_job = pipeline.define_asset_job(
        name="test_rerun_safety_job",
    )

    test_defs = Definitions(
        assets=[
            pipeline.transaction_count,
            pipeline.validated_transactions,
            pipeline.pyspark_transformation,
            test_report,
        ],
        jobs=[test_job],
    )

    with DagsterInstance.ephemeral() as instance:
        job = test_defs.resolve_job_def(
            "test_rerun_safety_job"
        )

        first_result = job.execute_in_process(instance=instance)
        assert first_result.success

        first_report = json.loads(
            report_path.read_text(encoding="utf-8")
        )

        assert first_report["total_transactions"] == 2

        # Simulate updated input data before rerunning.
        current_count["value"] = 3

        second_result = job.execute_in_process(instance=instance)
        assert second_result.success

    updated_report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    assert updated_report["pipeline_status"] == "SUCCESS"
    assert updated_report["total_transactions"] == 3
    assert updated_report["credit_transactions"] == 1
    assert updated_report["high_value_transactions"] == 0
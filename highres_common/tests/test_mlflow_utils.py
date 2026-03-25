import logging
import pytest
from io import StringIO
from contextlib import redirect_stdout
from highres_common.mlflow_utils import MlflowInfo

class DummyExperiment:
    def __init__(self):
        self.name = "Test Experiment"
        self.experiment_id = "123"
        self.artifact_location = "/tmp/artifacts"
        self.lifecycle_stage = "active"

class DummyRun:
    def __init__(self):
        self.info = type("Info", (), {
            "run_id": "abc123",
            "experiment_id": "123",
            "artifact_uri": "/tmp/artifacts/run1",
            "status": "FINISHED"
        })()
        self.data = type("Data", (), {
            "params": {"lr": "0.01", "epochs": "10"},
            "metrics": {"accuracy": 0.92, "loss": 0.18},
            "tags": {"model": "xgboost", "dataset": "ICU_waveforms"}
        })()

def test_print_experiment_info(caplog):
    exp = DummyExperiment()
    diag = MlflowInfo(experiment=exp)
    with caplog.at_level(logging.INFO):
        diag.print_experiment_info()

    assert "Experiment Info" in caplog.text
    assert "Name: Test Experiment" in caplog.text

def test_print_run_info(caplog):
    run = DummyRun()
    diag = MlflowInfo(run=run)
    with caplog.at_level(logging.INFO):
        diag.print_run_info()

    assert "Run Info" in caplog.text
    assert "Run ID: abc123" in caplog.text
    assert "Status: FINISHED" in caplog.text

def test_print_run_metrics(caplog):
    run = DummyRun()
    diag = MlflowInfo(run=run)
    with caplog.at_level(logging.INFO):
        diag.print_run_metrics()

    assert "Run Metrics" in caplog.text
    for k, v in run.data.metrics.items():
        assert k in caplog.text
        assert str(v) in caplog.text

def test_print_run_tags(caplog):
    run = DummyRun()
    diag = MlflowInfo(run=run)

    with caplog.at_level(logging.INFO):
        diag.print_run_tags()

    assert "Run Tags" in caplog.text
    for k, v in run.data.tags.items():
        assert k in caplog.text
        assert str(v) in caplog.text

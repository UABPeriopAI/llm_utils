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

def test_print_experiment_info():
    exp = DummyExperiment()
    diag = MlflowInfo(experiment=exp)
    with StringIO() as buf, redirect_stdout(buf):
        diag.print_experiment_info()
        output = buf.getvalue()
    assert "Experiment Info" in output
    assert "Name: Test Experiment" in output

def test_print_run_info():
    run = DummyRun()
    diag = MlflowInfo(run=run)
    with StringIO() as buf, redirect_stdout(buf):
        diag.print_run_info()
        output = buf.getvalue()
    assert "Run Info" in output
    assert "Run ID: abc123" in output
    assert "    - lr: 0.01" in output

def test_print_run_metrics():
    run = DummyRun()
    diag = MlflowInfo(run=run)
    with StringIO() as buf, redirect_stdout(buf):
        diag.print_run_metrics()
        output = buf.getvalue()
    assert "Run Metrics" in output
    assert "accuracy: 0.92" in output

def test_print_run_tags():
    run = DummyRun()
    diag = MlflowInfo(run=run)
    with StringIO() as buf, redirect_stdout(buf):
        diag.print_run_tags()
        output = buf.getvalue()
    assert "Run Tags" in output
    assert "model: xgboost" in output
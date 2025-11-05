"""
Lightweight helpers for inspecting MLflow experiment and run metadata.

This module provides MlflowInfo which prints (logs) experiment and run details.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MlflowInfo:
    """
    Helper wrapper to expose useful mlflow objects in a consistent way.

    Args:
        experiment: mlflow Experiment object (optional)
        run: mlflow Run object (optional)
    """

    def __init__(self, experiment: Optional[Any] = None, run: Optional[Any] = None) -> None:
        self.experiment = experiment
        self.run = run

    def print_experiment_info(self) -> None:
        """
        Print basic experiment information (name, id, artifact location, lifecycle stage).
        """
        if not self.experiment:
            logger.info("No experiment provided.")
            return

        logger.info("Experiment Info")
        logger.info("Name: %s", getattr(self.experiment, "name", None))
        logger.info("Experiment ID: %s", getattr(self.experiment, "experiment_id", None))
        logger.info("Artifact Location: %s", getattr(self.experiment, "artifact_location", None))
        logger.info("Lifecycle Stage: %s", getattr(self.experiment, "lifecycle_stage", None))

    def print_run_info(self) -> None:
        """
        Print run metadata including params and status.
        """
        if not self.run:
            logger.info("No run provided.")
            return

        info = getattr(self.run, "info", None)
        data = getattr(self.run, "data", None)

        logger.info("Run Info")
        logger.info("Run ID: %s", getattr(info, "run_id", None))
        logger.info("Experiment ID: %s", getattr(info, "experiment_id", None))
        logger.info("Artifact Uri: %s", getattr(info, "artifact_uri", None))
        logger.info("Status: %s", getattr(info, "status", None))

        logger.info("Params:")
        if data is not None and hasattr(data, "params"):
            for k, v in getattr(data, "params", {}).items():
                logger.info("    - %s: %s", k, v)

    def print_run_metrics(self) -> None:
        """Log run metrics if available."""
        if not self.run:
            logger.info("No run provided.")
            return

        data = getattr(self.run, "data", None)
        logger.info("Run Metrics")
        if data is not None and hasattr(data, "metrics"):
            for k, v in getattr(data, "metrics", {}).items():
                logger.info(" - %s: %s", k, v)

    def print_run_tags(self) -> None:
        """Log run tags if available."""
        if not self.run:
            logger.info("No run provided.")
            return

        data = getattr(self.run, "data", None)
        logger.info("Run Tags")
        if data is not None and hasattr(data, "tags"):
            for k, v in getattr(data, "tags", {}).items():
                logger.info(" - %s: %s", k, v)
"""
Loader utilities for Sickbay waveform data.

Provides SickbayWaveformLoader that validates dataframe structure and offers a brief summary.
Edits made to align with aiweb_common: added module docstring, logging, and typing.
"""
from __future__ import annotations

import logging
from typing import Any

import pandas as pd
from sickbay import data

logger = logging.getLogger(__name__)

SICKBAY_WAVEFORM_CLASSES = {
    "Arterial Blood Pressure Waveform",
    "ECG Lead II",
    "Pulmonary Artery Pressure Waveform",
    "Umbilical Arterial Catheter Pressure Waveform",
    "SPO2 Waveform",
    "IntraCranial Pressure Waveform",
    "ABP M",
    "Regional Oxygen Saturation CH1",
    "Regional Oxygen Saturation CH2",
    "Regional Oxygen Saturation CH3",
    "Regional Oxygen Saturation CH4",
    "Optical Density A CH1",
    "Optical Density A CH2",
    "Optical Density A CH3",
    "Optical Density A CH4",
}


class SickbayWaveformLoader:
    """Fetch and validate sickbay waveform data for a given patient and class."""

    def __init__(self, verbose: bool = False) -> None:
        self.verbose = verbose

    def get(self, class_name: str, patient_id: Any, start: Any, stop: Any) -> pd.DataFrame:
        """Request waveform data by class name and validate before returning.

        Args:
            class_name: Name of waveform class to request.
            patient_id: Patient identifier accepted by sickbay.data.
            start: Start time (format as accepted by sickbay.data.get_waveform_by_class).
            stop: End time.

        Returns:
            pandas.DataFrame containing waveform data.

        Raises:
            NameError: if class_name is not supported.
            TypeError / ValueError: if returned object is not a DataFrame or is invalid.
        """
        if class_name not in SICKBAY_WAVEFORM_CLASSES:
            raise NameError(
                f"Incompatible request: '{class_name}' is not a supported sickbay_waveform class. "
                f"Supported classes include: {', '.join(sorted(SICKBAY_WAVEFORM_CLASSES))}"
            )

        if self.verbose:
            logger.info("Requesting sickbay_waveform: %s", class_name)
            logger.info("PatientID: %s", patient_id)
            logger.info("Time range: %s to %s", start, stop)

        df = data.get_waveform_by_class(
            class_name=class_name,
            patient_id=patient_id,
            starttime=start,
            endtime=stop,
            relative_time=False,
        )

        self._validate_df(df)
        return df

    def _validate_df(self, df: Any) -> None:
        """Validate returned DataFrame is non-empty and contains timestamp column."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Expected a pandas DataFrame from sickbay.data.get_waveform_by_class.")

        if df.empty:
            raise ValueError("Sickbay_waveform data is empty.")

        if "timestamp" not in df.columns:
            raise ValueError("Missing 'timestamp' column in sickbay_waveform data.")

        if df["timestamp"].isnull().any():
            raise ValueError("Sickbay_waveform contains missing timestamps.")

        if df.isnull().any().any():
            logger.warning("Sickbay_waveform contains NaNs.")

        if self.verbose:
            logger.info("Sickbay_waveform shape: %s", df.shape)
            logger.info("Columns: %s", list(df.columns))

    def summary(self, df: pd.DataFrame) -> None:
        """Print a short summary of the DataFrame to logs."""
        logger.info("Summary:")
        logger.info("Shape: %s", df.shape)
        logger.info("Columns: %s", list(df.columns))
        if "timestamp" in df.columns:
            try:
                logger.info("Timestamp range: %s → %s", df["timestamp"].min(), df["timestamp"].max())
            except Exception:
                logger.debug("Failed to compute timestamp min/max.")
        logger.info("NaNs: %s", int(df.isnull().sum().sum()))

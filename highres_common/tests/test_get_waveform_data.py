import pytest
import pandas as pd
from unittest.mock import patch
from highres_common.get_waveform_data import WaveformLoader  # Replace with actual module name

def test_waveform_loader_get():
    dummy_df = pd.DataFrame({
        "timestamp": pd.date_range("2025-11-01 08:00:00", periods=5, freq="1min"),
        "value": [80, 82, 85, 83, 81]
    })

    with patch("your_module.data.get_waveform_by_class", return_value=dummy_df):
        loader = WaveformLoader(verbose=True)
        df = loader.get("ABP M", patient_id="12345", start="2025-11-01 08:00:00", stop="2025-11-01 09:00:00")
        assert isinstance(df, pd.DataFrame)
        assert "timestamp" in df.columns
        assert df.shape[0] == 5

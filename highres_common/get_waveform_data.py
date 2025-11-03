from sickbay import data
import pandas as pd

WAVEFORM_CLASSES = {
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

class WaveformLoader:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def get(self, class_name, patient_id, start, stop):
        if class_name not in WAVEFORM_CLASSES:
            raise NameError(
                f"Incompatible request: '{class_name}' is not a supported waveform class. \n"
                f"Supported classes include: \n - " + "\n - ".join(sorted(WAVEFORM_CLASSES))
            )
        
        if self.verbose:
            print(f"Requesting waveform: {class_name}")
            print(f"PatientID: {patient_id}")
            print(f"Time range: {start} to {stop}")

        df = data.get_waveform_by_class(
            class_name=class_name,
            patient_id=patient_id,
            starttime=start,
            endtime = stop,
            relative_time=False,
        )

        self._validate_df(df)
        return df
    
    def _validate_df(self, df):
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Expected a pandas dataframe.")
        
        if df.empty:
            raise ValueError("Waveform data is empty.")
        
        if "timestamp" not in df.columns:
            raise ValueError("Missing 'timestamp' column in waveform data.")
        
        if df["timestamp"].isnull().any():
            raise ValueError("Waveform contains missing timestamps.")
        
        if df.isnull().any().any():
            print("Warning: Waveform contains NaNs.")

        if self.verbose:
            print(f"Waveform shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")

    def summary(self, df):
        print("Summary:")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Timestamp range: {df['timestamp'].min()} → {df['timestamp'].max()}")
        print(f"NaNs: {df.isnull().sum().sum()}")

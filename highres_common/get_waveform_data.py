from sickbay import data

waveform_class_name_list = [
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
]


def get_waveform_data(class_name, patient_id, start, stop):
    # TODO import JVs code to take in either df or go get it (math.compute_autoregulation)
    if class_name in waveform_class_name_list:
        df = data.get_waveform_by_class(
            class_name=class_name,
            patient_id=patient_id,
            starttime=start,
            endtime=stop,
            relative_time=False,
        )
    else:
        raise NameError(
            "Incompatible request - class list currently works with Arterial Blood Pressure Waveform,"
            "ECG Lead II,"
            "Pulmonary Artery Pressure Waveform,"
            "Umbilical Arterial Catheter Pressure Waveform,"
            "SPO2 Waveform,"
            "IntraCranial Pressure Waveform,"
            "ABP M,"
            "Regional Oxygen Saturation CH1,"
            "Regional Oxygen Saturation CH2,"
            "Regional Oxygen Saturation CH3,"
            "Regional Oxygen Saturation CH4,"
            "Optical Density A CH1,"
            "Optical Density A CH2,"
            "Optical Density A CH3,"
            "Optical Density A CH4,"
        )
    return df

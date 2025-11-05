# highres_common

Reusable utilities used by the highres project.

This package contains small helpers for configuration management, JSON/CSV parsing,
time-series utilities, MLflow inspection helpers, and Sickbay waveform loaders.

Quick start
- Install requirements: pip install -r requirements.txt
- Run tests: pytest -q

Modules
- config_utils: ConfigUtils for loading/saving JSON/YAML configs.
- parse_json_file: CSV <-> JSON helpers and mapping utilities for patient MRN ↔ patient IDs.
- get_sickbay_waveform_data: SickbayWaveformLoader for waveform retrieval and validation.
- create_table_one: TableOneCreator to build TableOne summaries.

See docs/ for more detailed documentation if available.

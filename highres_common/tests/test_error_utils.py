import numpy as np
import pytest
from highres_common.error_utils import ErrorAnalysis

# Sample data for testing
y_true = np.array([[3, 5, 2, 7, 1, 4, 6, 8],
                   [2, 4, 3, 6, 2, 5, 7, 9]])
y_pred = np.array([[2.5, 5.1, 2.2, 6.8, 1.2, 3.9, 6.1, 7.9],
                   [2.1, 3.9, 2.8, 6.2, 2.1, 5.2, 6.8, 9.1]])

def test_shape_mismatch_raises():
    with pytest.raises(ValueError):
        ErrorAnalysis(y_true, y_pred[:, :-1])

def test_rmse_all():
    ea = ErrorAnalysis(y_true, y_pred)
    rmse_vals = ea.rmse_all()
    assert rmse_vals.shape == (8,)
    assert np.all(rmse_vals >= 0)

def test_mae_all():
    ea = ErrorAnalysis(y_true, y_pred)
    mae_vals = ea.mae_all()
    assert mae_vals.shape == (8,)
    assert np.all(mae_vals >= 0)

def test_r2_all():
    ea = ErrorAnalysis(y_true, y_pred)
    r2_vals = ea.r2_all()
    assert r2_vals.shape == (8,)
    assert np.all((r2_vals >= -1) & (r2_vals <= 1))

def test_ndcg_all():
    ea = ErrorAnalysis(y_true, y_pred)
    ndcg_vals = ea.ndcg_all(k=3)
    assert ndcg_vals.shape == (8,)
    assert np.all((ndcg_vals >= 0) & (ndcg_vals <= 1.1))

def test_mean_function():
    ea = ErrorAnalysis(y_true, y_pred)
    rmse_vals = ea.rmse_all()
    mean_rmse = ea.mean(rmse_vals)
    assert isinstance(mean_rmse, float)
    assert mean_rmse >= 0

def test_nan_warning(capfd):
    y_true_nan = y_true.astype(float)
    y_true_nan[0, 0] = np.nan
    ea = ErrorAnalysis(y_true_nan, y_pred)
    _ = ea.rmse_all()
    out, _ = capfd.readouterr()
    assert "NaN detected" in out
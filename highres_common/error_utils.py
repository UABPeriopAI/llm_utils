"""
Error analysis utilities for highres_common.

Provides ErrorAnalysis class with common regression and ranking metrics computed
across one or more target columns. Aligns docstring and logging style with aiweb_common.
"""
from typing import Any, Callable, Iterable, Optional, Tuple

import logging
import numpy as np
from sklearn import metrics

logger = logging.getLogger(__name__)


class ErrorAnalysis:
    """
    Compute common error metrics for regression or ranking tasks.

    Args:
        y_true: Array-like ground truth values. Shape (n_samples,) or (n_samples, n_targets).
        y_pred: Array-like predictions matching the shape of y_true.
        num_targets: Optional override for number of targets when y_true has multiple columns.

    Methods:
        rmse, mae, r2, cal_ndcg, rmse_all, mae_all, r2_all, ndcg_all, mean
    """

    def __init__(self, y_true: Iterable[float], y_pred: Iterable[float], num_targets: Optional[int] = 8) -> None:
        self.y_true = np.asarray(y_true)
        self.y_pred = np.asarray(y_pred)

        if self.y_true.shape != self.y_pred.shape:
            raise ValueError("Shape mismatch between y_true and y_pred")

        if num_targets is None:
            self.num_targets = self.y_true.shape[1] if self.y_true.ndim == 2 else 1
        else:
            self.num_targets = num_targets

    def _validate_pair(self, y_true: Optional[Iterable[float]] = None, y_pred: Optional[Iterable[float]] = None) -> Tuple[np.ndarray, np.ndarray]:
        y_true = np.asarray(y_true if y_true is not None else self.y_true)
        y_pred = np.asarray(y_pred if y_pred is not None else self.y_pred)

        if y_true.shape != y_pred.shape:
            raise ValueError("Shape mismatch in target column")

        if y_true.size == 0 or y_pred.size == 0:
            raise ValueError("Empty arrays provided to metric computation")

        if np.any(np.isnan(y_true)) or np.any(np.isnan(y_pred)):
            logger.warning("NaN detected in input arrays.")

        return y_true, y_pred

    def compute_metric_across_targets(self, metric_func: Callable[..., Any], *args, **kwargs) -> np.ndarray:
        """
        Compute a metric across target columns.

        metric_func: callable accepting (y_true_1d, y_pred_1d, *args, **kwargs)
        Returns an array of metric values (one per target).
        """
        results = []
        y_true_all = np.asarray(self.y_true)
        y_pred_all = np.asarray(self.y_pred)

        if y_true_all.ndim == 1:
            n_targets = 1
            y_true_all = y_true_all.reshape(-1, 1)
            y_pred_all = y_pred_all.reshape(-1, 1)
        else:
            n_targets = min(self.num_targets, y_true_all.shape[1])

        for i in range(n_targets):
            y_true_i = y_true_all[:, i]
            y_pred_i = y_pred_all[:, i]
            results.append(metric_func(y_true_i, y_pred_i, *args, **kwargs))

        return np.asarray(results)

    def rmse(self, y_true: Optional[Iterable[float]] = None, y_pred: Optional[Iterable[float]] = None) -> float:
        """Root Mean Squared Error for a single target (or the instance pair if none provided)."""
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        return float(np.sqrt(np.mean(np.square(y_true - y_pred))))

    def mae(self, y_true: Optional[Iterable[float]] = None, y_pred: Optional[Iterable[float]] = None) -> float:
        """Mean Absolute Error for a single target (or the instance pair if none provided)."""
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        return float(np.mean(np.abs(y_true - y_pred)))

    def r2(self, y_true: Optional[Iterable[float]] = None, y_pred: Optional[Iterable[float]] = None) -> float:
        """R^2 score for a single target (or the instance pair if none provided)."""
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        # sklearn may raise on constant arrays; propagate as float
        return float(metrics.r2_score(y_true, y_pred))

    def get_dcg(self, scores: Iterable[float]) -> float:
        scores = np.asarray(scores)
        if scores.size == 0:
            return 0.0
        ranks = np.arange(len(scores))
        return float(np.sum(scores / np.log2(ranks + 2)))

    def get_ndcg(self, top_true: Iterable[float], top_pred: Iterable[float]) -> float:
        top_true = np.asarray(top_true)
        top_pred = np.asarray(top_pred)
        idcg = self.get_dcg(top_true)
        dcg = self.get_dcg(top_pred)
        return float(dcg / idcg) if idcg != 0 else 0.0

    def cal_ndcg(self, k: int, y_true: Optional[Iterable[float]] = None, y_pred: Optional[Iterable[float]] = None) -> float:
        """Compute NDCG@k for a single target pair or the instance pair."""
        y_true, y_pred = self._validate_pair(y_true, y_pred)

        k = int(k)
        if k <= 0:
            raise ValueError("k must be a positive integer for NDCG calculation")

        sorted_true = sorted(enumerate(y_true), key=lambda x: x[1], reverse=True)
        sorted_pred = sorted(enumerate(y_pred), key=lambda x: x[1], reverse=True)

        top_true = [y_true[idx] for idx, _ in sorted_true[:k]]
        top_pred = [y_pred[idx] for idx, _ in sorted_pred[:k]]
        return float(self.get_ndcg(top_true, top_pred))

    def rmse_all(self) -> np.ndarray:
        arr = self.compute_metric_across_targets(self.rmse)
        logger.info("RMSE array: %s", arr)
        return arr

    def mae_all(self) -> np.ndarray:
        arr = self.compute_metric_across_targets(self.mae)
        logger.info("MAE array: %s", arr)
        return arr

    def r2_all(self) -> np.ndarray:
        arr = self.compute_metric_across_targets(self.r2)
        logger.info("R2 array: %s", arr)
        return arr

    def ndcg_all(self, k: int = 5) -> np.ndarray:
        arr = self.compute_metric_across_targets(lambda yt, yp: self.cal_ndcg(k, yt, yp))
        logger.info("NDCG@%s array: %s", k, arr)
        return arr

    def mean(self, arr: Iterable[float]) -> float:
        return float(np.mean(list(arr)))
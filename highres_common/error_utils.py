import numpy as np
from sklearn import metrics

class ErrorAnalysis:
    def __init__(self, y_true, y_pred, num_targets=8):
        self.y_true = y_true
        self.y_pred = y_pred

        if self.y_true.shape != self.y_pred.shape:
            raise ValueError("Shape mismatch between y_true and y_pred")
        
        if num_targets is None:
            self.num_targets = self.y_true.shape[1] if self.y_true.ndim == 2 else 1
        else:
            self.num_targets = num_targets
        
    def _validate_pair(self, y_true=None, y_pred=None):
        y_true = np.asarray(y_true if y_true is not None else self.y_true)
        y_pred = np.asarray(y_pred if y_pred is not None else self.y_pred)

        if y_true.shape != y_pred.shape:
            raise ValueError("Shape mismatch in target column")
        
        if np.any(np.isnan(y_true)) or np.any(np.isnan(y_pred)):
            print("Warning: NaN detected in input.")

        return y_true, y_pred
    
    def compute_metric_across_targets(self, metric_func, *args):
        """
        Compute a given metric across target columns.

        metric_func should be a callable that accepts (y_true, y_pred, *args)
        where y_true and y_pred are 1D arrays for a single target.
        """
        results = []
        # Ensure inputs are arrays
        y_true_all = np.asarray(self.y_true)
        y_pred_all = np.asarray(self.y_pred)

        # If inputs are 1D treat as single target
        if y_true_all.ndim == 1:
            n_targets = 1
            y_true_all = y_true_all.reshape(-1, 1)
            y_pred_all = y_pred_all.reshape(-1, 1)
        else:
            n_targets = min(self.num_targets, y_true_all.shape[1])

        for i in range(n_targets):
            y_true_i = y_true_all[:, i]
            y_pred_i = y_pred_all[:, i]
            results.append(metric_func(y_true_i, y_pred_i, *args))

        return np.array(results)

    def rmse(self, y_true=None, y_pred=None):
        """
        RMSE for given pair or the instance pair if none provided.
        """
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        return float(np.sqrt(np.mean(np.square(y_true - y_pred))))
    
    def mae(self, y_true=None, y_pred=None):
        """
        MAE for given pair or the instance pair if none provided.
        """
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        return float(np.mean(np.abs(y_true - y_pred)))
    
    def r2(self, y_true=None, y_pred=None):
        """
        R^2 score for given pair or the instance pair if none provided.
        """
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        # sklearn may raise on constant arrays; let it propagate or convert to float
        return float(metrics.r2_score(y_true, y_pred))
    
    def get_dcg(self, scores):
        scores = np.asarray(scores)
        ranks = np.arange(len(scores))
        return np.sum(scores / np.log2(ranks + 2))
    
    def get_ndcg(self, top_true, top_pred):
        top_true = np.asarray(top_true)
        top_pred = np.asarray(top_pred)
        idcg = self.get_dcg(top_true)
        dcg = self.get_dcg(top_pred)
        return dcg / idcg if idcg != 0 else 0.0
    
    def cal_ndcg(self, k, y_true=None, y_pred=None):
        """
        Compute NDCG@k for a single target pair or the instance pair.
        """
        y_true, y_pred = self._validate_pair(y_true, y_pred)

        # Ensure k is positive and not larger than available elements
        k = int(k)
        if k <= 0:
            raise ValueError("k must be a positive integer for NDCG calculation")

        sorted_true = sorted(enumerate(y_true), key=lambda x: x[1], reverse=True)
        sorted_pred = sorted(enumerate(y_pred), key=lambda x: x[1], reverse=True)

        top_true = [y_true[idx] for idx, _ in sorted_true[:k]]
        top_pred = [y_pred[idx] for idx, _ in sorted_pred[:k]]
        return float(self.get_ndcg(top_true, top_pred))
    
    def rmse_all(self):
        arr = self.compute_metric_across_targets(self.rmse)
        print("RMSE array:", arr)
        return arr
    
    def mae_all(self):
        arr = self.compute_metric_across_targets(self.mae)
        print("MAE array:", arr)
        return arr
    
    def r2_all(self):
        arr = self.compute_metric_across_targets(self.r2)
        print("R2 array:", arr)
        return arr
    
    def ndcg_all(self, k=5):
        arr = self.compute_metric_across_targets(lambda yt, yp: self.cal_ndcg(k, yt, yp))
        print(f"NDCG@{k} array:", arr)
        return arr
    
    def mean(self, arr):
        return np.mean(arr)
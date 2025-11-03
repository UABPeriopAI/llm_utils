import numpy as np
from sklearn import metrics

class ErrorAnalysis:
    def __init__(self, y_true, y_pred, num_targets=8):
        self.y_true = y_true
        self.y_pred = y_pred
        self.num_targets = num_targets

        if self.y_true.shape != self.y_pred.shape:
            raise ValueError("Shape mismatch between y_true and y_pred")
        
        if num_targets is None:
            self.num_targets = self.y_true.shape[1] if self.y_true.ndim == 2 else 1
        else:
            self.num_targets = num_targets
        
    def _validate_pair(self, y_true, y_pred):
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)

        if y_true.shape != y_pred.shape:
            raise ValueError("Shape mismatch in target column")
        
        if np.any(np.isnan(y_true)) or np.any(np.isnan(y_pred)):
            print("Warning: NaN detected in input.")

        return y_true, y_pred
    
    def compute_metric_across_targets(self, metric_func, *args):
        results = []
        for i in range(self.num_targets):
            true = self.y_true[:, i]
            pred = self.y_pred[:, i]
            results.append(metric_func(true, pred, *args) if args else metric_func(true, pred))
        return np.array(results)

    def rmse(self, y_true, y_pred):
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        return np.sqrt(np.mean(np.square(y_true - y_pred)))
    
    def mae(self, y_true, y_pred):
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        return np.mean(np.abs(y_true - y_pred))
    
    def r2(self, y_true, y_pred):
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        return metrics.r2_score(y_true, y_pred)
    
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
    
    def cal_ndcg(self, y_true, y_pred, k):
        y_true, y_pred = self._validate_pair(y_true, y_pred)
        sorted_true = sorted(enumerate(y_true), key=lambda x: x[1], reverse=True)
        sorted_pred = sorted(enumerate(y_pred), key=lambda x: x[1], reverse=True)

        top_true = [y_true[i] for i, _ in sorted_true[:k]]
        top_pred = [y_pred[i] for i, _ in sorted_pred[:k]]
        return self.get_ndcg(top_true, top_pred)
    
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
        arr = self.compute_metric_across_targets(self.cal_ndcg, k)
        print(f"NDCG@{k} array:", arr)
        return arr
    
    def mean(self, arr):
        return np.mean(arr)
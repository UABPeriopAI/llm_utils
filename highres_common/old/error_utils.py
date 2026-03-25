import numpy as np
from sklearn import metrics


def rmse_nine(y_true, y_pred):
    arr = []
    for i in range(8):
        true = y_true[:, i]
        pred = y_pred[:, i]
        arr.append(rmse(true, pred))
    arr = np.array(arr)
    print("rmse array", arr)
    return arr


def rmse(y_true, y_pred):
    l = len(y_true)
    total = 0.0
    for i in range(l):
        total += np.square(y_true[i] - y_pred[i])
    return np.sqrt(total / l)


def rmse_mean(arr):
    return np.sum(arr) / 8


def mae_nine(y_true, y_pred):
    arr = []
    for i in range(8):
        true = y_true[:, i]
        pred = y_pred[:, i]
        arr.append(mae(true, pred))
    arr = np.array(arr)
    print("mae array", arr)
    return arr


def mae(y_true, y_pred):
    l = len(y_true)
    total = 0.0
    for i in range(l):
        total += np.fabs(y_true[i] - y_pred[i])
    return total / l


def mae_mean(arr):
    return np.sum(arr) / 8


def r2_nine(y_true, y_pred):
    arr = []
    for i in range(8):
        true = y_true[:, i]
        pred = y_pred[:, i]
        arr.append(metrics.r2_score(true, pred))
    arr = np.array(arr)
    print("r2 array", arr)
    return arr


def r2_mean(arr):
    return np.sum(arr) / 8


def cal_ndcg(y_true, y_pred, k):
    l = len(y_true)
    index_true = []
    index_pred = []
    for i in range(l):
        index_true.append(i)
        index_pred.append(i)

    dic_true = dict(zip(index_true, y_true))
    dic_pred = dict(zip(index_pred, y_pred))
    true_sort = sorted(dic_true.items(), key=lambda item: item[1])
    pred_sort = sorted(dic_pred.items(), key=lambda item: item[1])
    true_sort = true_sort[::-1]
    pred_sort = pred_sort[::-1]
    top_true = []
    top_pred = []
    for i in range(k):
        top_true.append(true_sort[i][1])
        top_pred.append(dic_true[pred_sort[i][0]])
    return get_NDCG(top_true, top_pred)


def get_NDCG(top_true, top_pred):
    idcg = get_dcg(np.asarray(top_true))
    dcg = get_dcg(np.asarray(top_pred))
    return dcg / idcg


def get_dcg(l):
    k = len(l)
    kk = np.arange(k)
    return np.sum(np.divide(l, np.log2(kk + 2)))


def NDCG_nine(y_true, y_pred, k):
    arr = []
    for i in range(8):
        true = y_true[:, i]
        pred = y_pred[:, i]
        arr.append(cal_ndcg(true, pred, k))
    arr = np.array(arr)
    return arr


def NDCG_mean(arr):
    return np.sum(arr) / 8

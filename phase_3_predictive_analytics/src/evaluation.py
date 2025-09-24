import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

def mae(y_true, y_pred):
    """Mean Absolute Error"""
    return mean_absolute_error(y_true, y_pred)

def rmse(y_true, y_pred):
    """Root Mean Squared Error"""
    return np.sqrt(mean_squared_error(y_true, y_pred))

def bootstrap_ci(y_true, y_pred, metric_func, n_bootstrap=1000, alpha=0.05, random_state=None):
    """
    Compute bootstrap confidence intervals for any error metric.

    Args:
        y_true (array-like): Ground truth values.
        y_pred (array-like): Predicted values.
        metric_func (func): Metric function (e.g., mae, rmse).
        n_bootstrap (int): Number of bootstrap samples.
        alpha (float): Significance level (0.05 = 95% CI).
        random_state (int): Optional random seed for reproducibility.

    Returns:
        mean_metric (float): Mean bootstrap metric.
        ci (tuple): (lower bound, upper bound) of CI.
    """
    rng = np.random.default_rng(random_state)
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    n = len(y_true)

    metrics = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, n, replace=True)
        metrics.append(metric_func(y_true[idx], y_pred[idx]))

    lower = np.percentile(metrics, 100 * alpha / 2)
    upper = np.percentile(metrics, 100 * (1 - alpha / 2))
    return np.mean(metrics), (lower, upper)

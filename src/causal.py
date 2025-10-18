import numpy as np
import pandas as pd

def bootstrap_mean_diff(pre, post, n_boot=2000, seed=42):
    rng = np.random.default_rng(seed)
    pre = np.asarray(pre)
    post = np.asarray(post)
    diffs = []
    for _ in range(n_boot):
        pre_s = rng.choice(pre, size=pre.size, replace=True)
        post_s = rng.choice(post, size=post.size, replace=True)
        diffs.append(post_s.mean() - pre_s.mean())
    diffs = np.array(diffs)
    return diffs.mean(), (np.percentile(diffs, 2.5), np.percentile(diffs, 97.5))

def compute_pre_post_effect(df, date_col="date", on_col="therapy_on", y_col="pain_score"):
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col])
    d = d.sort_values(date_col)
    if d[on_col].nunique() < 2:
        raise ValueError("therapy_on column must include both 0 (pre) and 1 (post).")
    start_idx = d[d[on_col] == 1].index.min()
    pre = d.loc[d.index < start_idx, y_col].dropna().values
    post = d.loc[d.index >= start_idx, y_col].dropna().values
    if len(pre) == 0 or len(post) == 0:
        raise ValueError("Not enough pre or post observations.")
    est, (lo, hi) = bootstrap_mean_diff(pre, post)
    return {
        "n_pre": int(len(pre)),
        "n_post": int(len(post)),
        "effect_mean": float(est),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "pre_mean": float(np.mean(pre)),
        "post_mean": float(np.mean(post)),
        "start_date": str(d.loc[start_idx, date_col].date())
    }

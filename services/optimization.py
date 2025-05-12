import pandas as pd
from typing import Any
from skfolio.preprocessing import prices_to_returns
from sklearn.svm import LinearSVC


def normalize_weights(weights: dict, prices: dict | pd.Series, capital: float) -> list[dict[str, float]]:
    stocks = []
    w_sum = 0
    for t, w in weights.items():
        price = prices.get(t)
        if not price: continue
        shares = int(capital * w / price)
        if shares > 0:
            w_sum += w
            stocks.append({'ticker': t, 'price': price, 'weight': w})
    for s in stocks:
        weight = s['weight'] / w_sum
        shares = int(weight * capital / s['price'])
        allocated = shares * s['price']
        s['weight'] = weight
        s['allocated'] = allocated
        s['shares'] = shares
    return sorted(stocks, key=lambda x: x['weight'], reverse=True)

def select_tickers(
    dataset: pd.DataFrame,
    picker: Any
) -> list[str]:
    """
    Given a dataset with feature columns and a trained picker,
    return list of tickers with average probability > 0.5 in latest quarter.
    """
    # identify feature cols
    exclude = {"ticker", "date", "quarter_id", "close_raw", "outperformed"}
    feature_cols = [c for c in dataset.columns if c not in exclude]

    # predict probabilities
    X = dataset[feature_cols].values
    dataset = dataset.copy()
    if isinstance(picker, LinearSVC):
        dataset["pred_proba"] = picker._predict_proba_lr(X)[:, 1]
    else:
        dataset["pred_proba"] = picker.predict_proba(X)[:, 1]

    # select latest quarter per ticker
    latest_q = dataset.groupby("ticker")["quarter_id"].max().reset_index()
    data_latest = pd.merge(dataset, latest_q, on=["ticker", "quarter_id"])
    avg_pred = data_latest.groupby("ticker")["pred_proba"].mean().reset_index()

    # tickers with prob > .5
    selected = avg_pred.loc[avg_pred["pred_proba"] > 0.6, "ticker"].tolist()
    return selected


def optimize_portfolio(
    prices: pd.DataFrame,
    selected: list[str],
    risk_fn: Any
) -> tuple[dict, Any]:
    """
    Given prices DataFrame and selected tickers, compute weights and portfolio object.
    """
    # pivot to wide
    price_matrix = (
        prices[prices["ticker"].isin(selected)]
        .pivot(index="date", columns="ticker", values="price")
        .sort_index()
    )
    # compute returns
    ret = prices_to_returns(price_matrix)

    # optimize via risk_fn
    weights, ptf = risk_fn(ret)
    return dict(zip(selected, weights)), ptf
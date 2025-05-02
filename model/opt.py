import pandas as pd
import numpy as np
import joblib

from skfolio.optimization import (
    EqualWeighted,
    MeanRisk,
    ObjectiveFunction,
    NestedClustersOptimization
)
from skfolio.measures import RiskMeasure
from skfolio.preprocessing import prices_to_returns
from skfolio.moments import LedoitWolf
from skfolio.prior import EmpiricalPrior

# ---------- Helper Optimizer Functions ---------- #

def equal_weighted_portfolio(returns):
    """Equal‑weighted benchmark portfolio."""
    opt = EqualWeighted()
    opt.fit(returns)
    return opt.weights_, opt.predict(returns)


def min_variance_portfolio(returns):
    """Classical minimum‑variance (sample covariance)."""
    opt = MeanRisk(
        objective_function=ObjectiveFunction.MINIMIZE_RISK,
        risk_measure=RiskMeasure.VARIANCE,
    )
    opt.fit(returns)
    return opt.weights_, opt.predict(returns)


def min_variance_ledoitwolf(returns):
    """Minimum‑variance with Ledoit‑Wolf shrinkage covariance."""
    opt = MeanRisk(
        objective_function=ObjectiveFunction.MINIMIZE_RISK,
        risk_measure=RiskMeasure.VARIANCE,
        prior_estimator=EmpiricalPrior(covariance_estimator=LedoitWolf()),
    )
    opt.fit(returns)
    return opt.weights_, opt.predict(returns)


def nco_portfolio(returns):
    """Nested Clustered Optimization (inner Min‑Var, outer Equal‑Weight)."""
    opt = NestedClustersOptimization(
        inner_estimator=MeanRisk(
            objective_function=ObjectiveFunction.MINIMIZE_RISK,
            risk_measure=RiskMeasure.VARIANCE,
        )
    )
    opt.fit(returns)
    return opt.weights_, opt.predict(returns)

# ---------- Pipeline ---------- #

def main():
    # Load ML model & dataset
    model = joblib.load("models/l2.pkl")
    data = pd.read_csv("data/dataset.csv")
    features = [c for c in data.columns if c not in [
        "ticker", "date", "quarter_id", "close_raw", "outperformed"
    ]]

    # Predict probabilities
    data["pred_proba"] = model.predict_proba(data[features].values)[:, 1]

    # Select latest quarter for each stock and average proba
    latest_q = data.groupby("ticker")["quarter_id"].max().reset_index()
    data_latest = pd.merge(data, latest_q, on=["ticker", "quarter_id"])
    avg_pred = data_latest.groupby("ticker")["pred_proba"].mean().reset_index()
    selected = avg_pred[avg_pred["pred_proba"] > 0.5]["ticker"].tolist()
    print("Selected tickers:", selected)

    # Build returns matrix
    price = (
        data[data["ticker"].isin(selected)]
        .pivot(index="date", columns="ticker", values="close_raw")
        .sort_index()
    )
    returns = prices_to_returns(price)

    # Run optimizers
    optimizers = {
        "Equal‑Weight": equal_weighted_portfolio,
        "Min‑Var (Sample)": min_variance_portfolio,
        "Min‑Var (Ledoit‑Wolf)": min_variance_ledoitwolf,
        "Nested Clustered Opt": nco_portfolio,
    }

    for name, fn in optimizers.items():
        w, ptf = fn(returns)
        print(f"{name}:")
        print("Weights (first 10):", np.round(w[:10], 4))
        print("Annualized Sharpe:", round(ptf.annualized_sharpe_ratio, 3))
        # Optionally plot: ptf.plot_cumulative_returns()


if __name__ == "__main__":
    main()

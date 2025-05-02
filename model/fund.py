import numpy as np
import pandas as pd


def winsorize_mad(series, k=3):
    """Robust clip at median ± k·MAD."""
    if series.isna().all():
        return series
    med = series.median()
    mad = np.median(np.abs(series - med))
    return series.clip(lower=med - k * mad, upper=med + k * mad)

def signed_log(x):
    return np.sign(x) * np.log1p(np.abs(x))

def robust_z(series):
    # drop the all-NaN slice instead of letting numpy whine
    if series.isna().all():
        return series  # leave as NaN; you’ll fill later
    return (series - series.mean()) / series.std(ddof=0)

def normalize_fundamentals(df):
    """
    df columns: ['ticker', 'date', <fundamental metrics…>]
    Returns dataframe with all fundamental features cross-section z-scored
    and ready to merge with your technical block.
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    

    per_share = [
        'Book Value Per Share',
        'Free Cash Flow Per Share',
        'Operating Cash Flow Per Share'
    ]

    margins_ratios = [
        'Asset Turnover', 'Current Ratio', 'Debt/Equity Ratio',
        'EBIT Margin', 'Gross Margin', 'Net Profit Margin', 'Operating Margin',
        'Pre-Tax Profit Margin', 'ROA - Return On Assets',
        'ROE - Return On Equity', 'ROI - Return On Investment',
        'Return On Tangible Equity', 'Inventory Turnover Ratio',
        'Days Sales In Receivables', 'Receiveable Turnover',
        'Long-term Debt / Capital'
    ]

    # ---------- 1. per-ticker clean-up ----------
    cleaned_frames = []
    for _, g in df.groupby('ticker'):
        g = g.copy()

        # log-transform dollar-per-share metrics
        g[per_share] = g[per_share].apply(signed_log)

        # robust winsorize all ratios / margins
        g[margins_ratios] = g[margins_ratios].apply(winsorize_mad)

        cleaned_frames.append(g)

    df_clean = pd.concat(cleaned_frames, ignore_index=True)

    # ---------- 2. cross-section standardisation ----------
    feature_cols = [c for c in df_clean.columns if c not in ('ticker', 'date')]
    df_clean[feature_cols] = (
        df_clean
        .groupby('date')[feature_cols]
        .transform(robust_z)
    )

    for col in feature_cols:
        df_clean[f'{col}_na'] = df_clean[col].isna().astype(int)
    df_clean[feature_cols] = df_clean[feature_cols].fillna(0)

    return df_clean


if __name__ == "__main__":
    df = pd.read_csv("data/financials/ratios_raw.csv")
    df = normalize_fundamentals(df)
    df.to_csv("data/financials/ratios.csv", index=False)
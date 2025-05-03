import pandas as pd
import numpy as np
import talib
import sqlite3


def winsorize_mad(series: pd.Series, k=3):
    """Robust clip at median +- k*MAD."""
    if series.isna().all():
        return series
    med = series.median()
    mad = np.median(np.abs(series - med))
    return series.clip(lower=med - k * mad, upper=med + k * mad)

def signed_log(x):
    return np.sign(x) * np.log1p(np.abs(x))

def robust_z(series: pd.Series):
    if series.isna().all():
        return series
    return (series - series.mean()) / series.std(ddof=0)

def normalize_fundamentals(df: pd.DataFrame):
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

    # ---------- 1. ticker standardisation ----------
    cleaned_frames = []
    for _, g in df.groupby('ticker'):
        g = g.copy()

        # log-transform dollar-per-share metrics
        g[per_share] = g[per_share].apply(signed_log)

        # winsorize all ratios / margins
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

def generate_technicals(df: pd.DataFrame, benchmark_df: pd.DataFrame = None):
    """
    df: DataFrame with columns ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
    benchmark_df: optional DataFrame with 'date' and 'close' columns for SPX or other index
    """
    df = df.sort_values(['ticker', 'date']).copy()

    feature_frames = []

    for ticker, group in df.groupby('ticker'):
        group = group.copy().reset_index(drop=True)  # index mismatch during the merge requires reseting the group's index
        close = group['close'].values
        volume = group['volume'].values

        # Bollinger Bands
        upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=13)
        group['bb_pr_up'] = np.log(close / upperband)
        ratio = close / lowerband
        ratio = np.where(ratio > 0, ratio, np.nan)  # Replace bad values with NaN
        group['bb_pr_dn'] = np.log(ratio)

        # RSI (13 weeks)
        group['rsi_13w'] = talib.RSI(close, timeperiod=13)

        # Momentum
        group['mom_13w'] = talib.MOM(close, timeperiod=13)
        group['mom_26w'] = talib.MOM(close, timeperiod=26)

        # Linear Regression Slope
        group['lr_slope_13w'] = talib.LINEARREG_SLOPE(close, timeperiod=13)

        # Moving Average ratios
        ma_26w = talib.SMA(close, timeperiod=26)
        ma_52w = talib.SMA(close, timeperiod=52)
        group['ma_pr_26w'] = np.log(close / ma_26w)
        group['ma_pr_52w'] = np.log(close / ma_52w)

        # Returns
        group['ret_13w'] = group['close'] / group['close'].shift(13) - 1
        group['ret_26w'] = group['close'] / group['close'].shift(26) - 1

        # Volatility (std of returns)
        daily_ret = group['close'].pct_change(fill_method=None)
        group['vol_13w'] = daily_ret.rolling(13).std()

        # Risk-adjusted return
        group['ret_div_vol_13w'] = group['ret_13w'] / group['vol_13w']

        # Beta (vs benchmark)
        if benchmark_df is not None:
            group = group.sort_values('date')
            benchmark = benchmark_df.sort_values('date').copy()
            merged = pd.merge_asof(group, benchmark[['date', 'close']], on='date', direction='backward', suffixes=('', '_spy'))

            group['close_raw'] = merged['close']
            group['close_spy'] = merged['close_spy']

            stock_ret = merged['close'].pct_change()
            spx_ret = merged['close_spy'].pct_change()

            cov = stock_ret.rolling(13).cov(spx_ret)
            var = spx_ret.rolling(13).var()
            group['beta_13w'] = cov / var

            cov = stock_ret.rolling(26).cov(spx_ret)
            var = spx_ret.rolling(26).var()
            group['beta_26w'] = cov / var

            # Correlation return vs SPX return
            group['corr_rtn_spyrtn_13w'] = stock_ret.rolling(13).corr(spx_ret)

            # Excess returns
            group['excess_13w'] = group['ret_13w'] - spx_ret.shift(13)
            group['excess_26w'] = group['ret_26w'] - spx_ret.shift(26)
        else:
            group['beta_13w'] = np.nan
            group['beta_26w'] = np.nan
            group['corr_rtn_spyrtn_13w'] = np.nan
            group['excess_13w'] = np.nan
            group['excess_26w'] = np.nan

        # Correlation return vs volume
        group['corr_rtn_volume_13w'] = daily_ret.rolling(13).corr(group['volume'])

        feature_frames.append(group)

    final_df = pd.concat(feature_frames, axis=0)

    return final_df

def resample_weekly(df: pd.DataFrame):
    """
    Expects df with ['ticker', 'date', 'close', 'volume'].
    Resamples to weekly data — last close of the week, summed volume.
    """
    df = df.copy()
    df.set_index('date', inplace=True)
    
    resampled = df.groupby('ticker').resample('W-FRI').agg({
        'close': 'last',
        'volume': 'sum'
    }).dropna().reset_index()

    return resampled

def normalize_features(df: pd.DataFrame):
    df = df.copy()
    
    exclude_cols = ['date', 'ticker', 'corr_rtn_volume_13w', 'corr_rtn_spyrtn_13w', 'rsi_13w', 'volume', 'close_raw', 'close_spy']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    normalized_frames = []

    for ticker, group in df.groupby('ticker'):
        group = group.copy()

        group['close'] = np.log(group['close'])
        group['rsi_13w'] = group['rsi_13w'] / 100.0

        group['volume'] =  np.log(group['volume'] + 1)
        v_mu = group['volume'].rolling(26).mean()
        v_sigma = group['volume'].rolling(26).std()
        group['volume'] = (group['volume'] - v_mu) / v_sigma

        group[feature_cols] = group[feature_cols].apply(lambda x: (x - x.mean()) / x.std())

        normalized_frames.append(group)

    df_normalized = pd.concat(normalized_frames, axis=0).reset_index(drop=True)
    return df_normalized

def generate_labels(dataset: pd.DataFrame, fund_cols: list):
    dataset = dataset.copy()

    dataset['is_quarter_start'] = dataset.groupby('ticker')[fund_cols].apply(
        lambda x: x.ne(x.shift()).any(axis=1)
    ).astype(int).reset_index(drop=True)

    dataset['quarter_id'] = dataset.groupby('ticker')['is_quarter_start'].cumsum()

    labels = []

    for (ticker, quarter_id), group in dataset.groupby(['ticker', 'quarter_id']):
        if len(group) < 2: continue

        start = group.iloc[0]
        end = group.iloc[-1]

        price_start = start['close_raw']
        price_end = end['close_raw']
        spy_start = start['close_spy']
        spy_end = end['close_spy']

        if price_start <= 0 or spy_start <= 0:
            continue

        stock_return = price_end / price_start - 1
        spy_return = spy_end / spy_start - 1
        label = int(stock_return > spy_return)

        cnt = 0
        for i, row in group.iterrows():
            labels.append({
                'ticker': ticker,
                'date': row['date'],
                'since_quarter_start': cnt / len(group),  # not `i` cuz of indexing
                'outperformed': label
            })
            cnt += 1

    dataset = pd.merge(
        dataset,
        pd.DataFrame(labels),
        on=['ticker', 'date'],
        how='left'
    ).drop(columns=['is_quarter_start'])

    return dataset


def merge(tech: pd.DataFrame, fund: pd.DataFrame) -> pd.DataFrame:
    tech['date'] = pd.to_datetime(tech['date'])
    fund['date'] = pd.to_datetime(fund['date'])

    tech = tech.sort_values(['ticker', 'date'])
    fund = fund.sort_values(['ticker', 'date'])

    frames = []
    for ticker, t_df in tech.groupby("ticker"):
        f_df = fund[fund["ticker"] == ticker]
        if f_df.empty: continue

        t_df = t_df.sort_values("date").reset_index(drop=True)
        f_df = f_df.sort_values("date").reset_index(drop=True)

        merged = pd.merge_asof(
            t_df,
            f_df,
            on="date",
            direction="backward"  # latest <= weekly date
        )
        frames.append(merged)

    dataset = pd.concat(frames, ignore_index=True)
    dataset.drop(columns=['ticker_y'], inplace=True)
    dataset.rename(columns={'ticker_x': 'ticker'}, inplace=True)
    dataset.dropna(inplace=True)
    dataset.reset_index(drop=True, inplace=True)

    fund_cols = [col for col in dataset.columns if col not in tech.columns and not col.endswith('_na')]
    dataset = generate_labels(dataset, fund_cols)
    dataset.drop(columns=['close_spy'], inplace=True)
    dataset.dropna(inplace=True)

    return dataset


def generate_example():
    con = sqlite3.connect('data/data.db')
    df = pd.read_sql('SELECT * FROM prices WHERE date > "2007-06-01"', con)
    df['date'] = pd.to_datetime(df['date'])
    df = resample_weekly(df[['ticker', 'date', 'close', 'volume']])
    benchmark_df = pd.read_csv('data/spy/spy.csv')
    benchmark_df['date'] = pd.to_datetime(benchmark_df['date'], format='%Y%m%d')
    benchmark_df['ticker'] = 'SPY'
    benchmark_df = resample_weekly(benchmark_df[['ticker', 'date', 'close', 'volume']])
    features_df = generate_technicals(df, benchmark_df)
    features_df = normalize_features(features_df)

    features_df.to_csv('data/technicals.csv', index=False)


if __name__ == '__main__':
    merge()
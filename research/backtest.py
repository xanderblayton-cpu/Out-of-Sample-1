"""
Research engine v0.1
Question: does CAPE (Shiller PE10) actually work as a market-timing signal?

Everyone repeats "CAPE is high, get out." This tests it against 150 years of
data with strict no-lookahead rules, then reports what it really does.

Data: Robert Shiller's S&P 500 dataset, monthly, 1871 to present.
"""

import pandas as pd
import numpy as np

# ---------- load and clean ----------
df = pd.read_csv("/home/claude/shiller.csv", parse_dates=["Date"])
df = df.rename(columns={
    "Consumer Price Index": "CPI",
    "Long Interest Rate": "LongRate",
    "Real Price": "RealPrice",
    "Real Dividend": "RealDiv",
    "Real Earnings": "RealEarn",
})

# Recent rows carry price only; CPI/dividend/CAPE lag. Truncate to fully valid data.
valid = df[(df.RealPrice > 0) & (df.PE10 > 0) & (df.RealDiv > 0) & (df.LongRate > 0)]
df = df.loc[valid.index.min():valid.index.max()].reset_index(drop=True)
print(f"Usable data: {df.Date.min():%Y-%m} to {df.Date.max():%Y-%m}  ({len(df)} months)\n")

# ---------- monthly real total return of the index ----------
# Reinvest dividends monthly. RealDiv is an annualized figure.
df["div_m"] = df.RealDiv / 12.0
df["ret_stock"] = (df.RealPrice + df.div_m) / df.RealPrice.shift(1) - 1

# Cash leg: long rate is nominal annual; convert to monthly and deflate by realized inflation.
df["infl_m"] = df.CPI / df.CPI.shift(1) - 1
df["ret_cash"] = (1 + df.LongRate / 100.0) ** (1 / 12) - 1 - df["infl_m"]

df = df.dropna(subset=["ret_stock", "ret_cash"]).reset_index(drop=True)

# ---------- the signal, with NO lookahead ----------
# At each month t we may only use CAPE history up to and including t.
# Threshold = expanding-window percentile of all CAPE observed so far.
# We require a 30-year burn-in so the percentile means something.
BURN_IN = 360  # months

def expanding_percentile_rank(series):
    """Percentile rank of each value within the history available at that time."""
    out = np.full(len(series), np.nan)
    vals = series.values
    for i in range(len(vals)):
        hist = vals[: i + 1]
        out[i] = (hist < vals[i]).sum() / len(hist)
    return out

df["cape_rank"] = expanding_percentile_rank(df.PE10)

# Signal is formed at end of month t, traded in month t+1. Shift to avoid lookahead.
df["signal_rank"] = df.cape_rank.shift(1)

COST = 0.001  # 10 bps round trip per switch, generous for most of this history

def run(threshold, label):
    d = df.iloc[BURN_IN:].copy()
    in_stocks = d.signal_rank < threshold
    ret = np.where(in_stocks, d.ret_stock, d.ret_cash)
    switches = in_stocks.ne(in_stocks.shift(1)).fillna(False)
    ret = ret - switches.values * COST
    return pd.Series(ret, index=d.Date), int(switches.sum()), in_stocks.mean()

def stats(r):
    n = len(r)
    total = (1 + r).prod()
    cagr = total ** (12 / n) - 1
    vol = r.std() * np.sqrt(12)
    curve = (1 + r).cumprod()
    dd = (curve / curve.cummax() - 1).min()
    sharpe = cagr / vol if vol > 0 else np.nan
    return cagr, vol, dd, sharpe, total

bh = df.iloc[BURN_IN:].set_index("Date").ret_stock
print(f"{'Strategy':<34}{'CAGR':>8}{'Vol':>8}{'MaxDD':>9}{'Ret/Vol':>9}{'Trades':>8}{'%InMkt':>8}")
print("-" * 84)
c, v, d_, s, t = stats(bh)
print(f"{'Buy and hold (real total return)':<34}{c:>7.2%}{v:>8.1%}{d_:>9.1%}{s:>9.2f}{0:>8}{1.0:>8.0%}")

results = {}
for th in [0.95, 0.90, 0.80, 0.70, 0.50]:
    r, sw, pct = run(th, th)
    c, v, d_, s, t = stats(r)
    results[th] = (c, v, d_, s)
    print(f"{'Exit above ' + f'{th:.0%}' + ' CAPE percentile':<34}{c:>7.2%}{v:>8.1%}{d_:>9.1%}{s:>9.2f}{sw:>8}{pct:>8.0%}")

# ---------- the other question: does CAPE predict LONG-RUN returns? ----------
print("\n\nCAPE vs subsequent 10-year annualized real total return")
print("-" * 84)
d = df.copy()
d["gross"] = (1 + d.ret_stock).cumprod()
H = 120
d["fwd10"] = (d.gross.shift(-H) / d.gross) ** (12 / H) - 1
sub = d.dropna(subset=["fwd10", "PE10"])
corr = np.corrcoef(sub.PE10, sub.fwd10)[0, 1]
print(f"Correlation of CAPE with next 10yr real return: {corr:+.3f}   (R-squared {corr**2:.3f})")

print(f"\n{'CAPE quintile at purchase':<34}{'Avg CAPE':>10}{'Median fwd 10yr':>18}{'Worst':>10}{'Best':>10}")
print("-" * 84)
sub = sub.copy()
sub["q"] = pd.qcut(sub.PE10, 5, labels=["cheapest 20%", "2nd", "3rd", "4th", "priciest 20%"])
for q, g in sub.groupby("q", observed=True):
    print(f"{str(q):<34}{g.PE10.mean():>10.1f}{g.fwd10.median():>17.2%}{g.fwd10.min():>10.1%}{g.fwd10.max():>10.1%}")

print(f"\nCAPE most recent reading: {df.PE10.iloc[-1]:.1f} as of {df.Date.iloc[-1]:%B %Y}")
print(f"Its percentile vs all history: {df.cape_rank.iloc[-1]:.0%}")

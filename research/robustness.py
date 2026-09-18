"""Robustness checks. A backtest you haven't tried to break is a marketing claim."""
import pandas as pd, numpy as np

df = pd.read_csv("/home/claude/shiller.csv", parse_dates=["Date"]).rename(columns={
    "Consumer Price Index": "CPI", "Long Interest Rate": "LongRate",
    "Real Price": "RealPrice", "Real Dividend": "RealDiv"})
v = df[(df.RealPrice > 0) & (df.PE10 > 0) & (df.RealDiv > 0) & (df.LongRate > 0)]
print("Data coverage check")
print(f"  RealPrice last valid: {df[df.RealPrice>0].Date.max():%Y-%m}")
print(f"  RealDiv   last valid: {df[df.RealDiv>0].Date.max():%Y-%m}")
print(f"  PE10      last valid: {df[df.PE10>0].Date.max():%Y-%m}")
print(f"  LongRate  last valid: {df[df.LongRate>0].Date.max():%Y-%m}")

df = df.loc[v.index.min():v.index.max()].reset_index(drop=True)
df["div_m"] = df.RealDiv / 12
df["ret_stock"] = (df.RealPrice + df.div_m) / df.RealPrice.shift(1) - 1
df["infl_m"] = df.CPI / df.CPI.shift(1) - 1
df["ret_cash"] = (1 + df.LongRate/100) ** (1/12) - 1 - df.infl_m
df = df.dropna(subset=["ret_stock", "ret_cash"]).reset_index(drop=True)

vals = df.PE10.values
rank = np.array([(vals[:i+1] < vals[i]).sum() / (i+1) for i in range(len(vals))])
df["signal_rank"] = pd.Series(rank).shift(1)
BURN = 360

def stats(r):
    n = len(r); tot = (1+r).prod(); cagr = tot**(12/n)-1
    vol = r.std()*np.sqrt(12); cur = (1+r).cumprod()
    return cagr, vol, (cur/cur.cummax()-1).min(), cagr/vol

def run(d, th, cost, weight_off=0.0):
    sig = d.signal_rank < th
    w = np.where(sig, 1.0, weight_off)
    ret = w*d.ret_stock + (1-w)*d.ret_cash
    turn = np.abs(np.diff(np.concatenate([[1.0], w])))
    return pd.Series(ret - turn*cost)

# --- 1. does it hold in sub-periods? ---
print("\n1. Sub-period test (exit above 90th percentile CAPE, 10bp cost)")
print(f"{'Period':<22}{'Buy and hold':>15}{'CAPE timing':>15}{'Difference':>14}")
print("-"*66)
for lo, hi, name in [(1881,1950,"1881 to 1950"), (1950,1990,"1950 to 1990"),
                     (1990,2024,"1990 to 2023"), (1881,2024,"Full sample")]:
    d = df[(df.Date.dt.year>=lo)&(df.Date.dt.year<hi)]
    d = d[d.index >= BURN]
    if len(d) < 120:
        print(f"{name:<22}{'(burn-in overlap)':>44}"); continue
    b = stats(d.ret_stock)[0]; t = stats(run(d,0.90,0.001))[0]
    print(f"{name:<22}{b:>14.2%}{t:>15.2%}{t-b:>+14.2%}")

# --- 2. is it cost sensitivity or is the strategy just bad? ---
print("\n2. Zero transaction costs (best possible case for timing)")
d = df.iloc[BURN:]
print(f"{'Threshold':<22}{'CAGR':>10}{'vs buy-hold':>14}")
print("-"*46)
b = stats(d.ret_stock)[0]
for th in [0.95, 0.90, 0.80, 0.70]:
    c = stats(run(d, th, 0.0))[0]
    print(f"{'exit above '+f'{th:.0%}':<22}{c:>9.2%}{c-b:>+14.2%}")

# --- 3. partial de-risking instead of all-or-nothing ---
print("\n3. Lighten to 50% stocks instead of going fully to cash")
print(f"{'Threshold':<22}{'CAGR':>10}{'MaxDD':>10}{'Ret/Vol':>10}")
print("-"*52)
c,vv,dd,s = stats(d.ret_stock); print(f"{'buy and hold':<22}{c:>9.2%}{dd:>10.1%}{s:>10.2f}")
for th in [0.90, 0.80]:
    c,vv,dd,s = stats(run(d, th, 0.001, weight_off=0.5))
    print(f"{'lighten above '+f'{th:.0%}':<22}{c:>9.2%}{dd:>10.1%}{s:>10.2f}")

# --- 4. how long can the signal be wrong? ---
print("\n4. Longest stretches the 'too expensive, get out' signal was on")
sig = (df.signal_rank >= 0.90).iloc[BURN:]
runs, cur, start = [], 0, None
for dt, on in zip(df.Date.iloc[BURN:], sig):
    if on:
        cur += 1; start = dt if cur == 1 else start
    else:
        if cur > 0: runs.append((start, cur))
        cur = 0
if cur > 0: runs.append((start, cur))
for s_, n in sorted(runs, key=lambda x: -x[1])[:5]:
    print(f"   from {s_:%b %Y}: {n} months ({n/12:.1f} years) out of the market")

# --- 5. forward-return relationship, modern era only ---
print("\n5. Does CAPE still predict 10yr returns using only post-1950 data?")
d2 = df.copy(); d2["g"] = (1+d2.ret_stock).cumprod()
d2["fwd10"] = (d2.g.shift(-120)/d2.g)**(12/120)-1
for lo, name in [(1881,"1881 onward"), (1950,"1950 onward"), (1980,"1980 onward")]:
    s_ = d2[(d2.Date.dt.year>=lo)].dropna(subset=["fwd10"])
    if len(s_) > 120:
        c = np.corrcoef(s_.PE10, s_.fwd10)[0,1]
        print(f"   {name:<16} corr {c:+.3f}   R-sq {c**2:.3f}   n={len(s_)}")

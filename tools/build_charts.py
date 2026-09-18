"""Dark-theme SVG charts for the Out of Sample site."""
import pandas as pd, numpy as np, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)

BG      = "#0c0e12"
SURF    = "#12151b"
TEXT    = "#e8ebef"
TEXT2   = "#98a2af"
TEXT3   = "#5f6976"
GRID    = "#1e232b"
BRASS   = "#e0a34a"
FAIL    = "#e5564e"
HOLDS   = "#3fb984"
STEEL   = "#6d9fd4"
SEQ     = ["#2b4a6b", "#39648f", "#4a82b8", "#7aa9d8", "#b3cdea"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": TEXT, "axes.labelcolor": TEXT2,
    "xtick.color": TEXT2, "ytick.color": TEXT2, "axes.edgecolor": GRID,
    "svg.fonttype": "path",
})

# ---------- data ----------
df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "research", "shiller.csv"), parse_dates=["Date"]).rename(columns={
    "Consumer Price Index": "CPI", "Long Interest Rate": "LongRate",
    "Real Price": "RealPrice", "Real Dividend": "RealDiv"})
v = df[(df.RealPrice > 0) & (df.PE10 > 0) & (df.RealDiv > 0) & (df.LongRate > 0)]
df = df.loc[v.index.min():v.index.max()].reset_index(drop=True)
df["ret_stock"] = (df.RealPrice + df.RealDiv / 12) / df.RealPrice.shift(1) - 1
df["infl_m"] = df.CPI / df.CPI.shift(1) - 1
df["ret_cash"] = (1 + df.LongRate / 100) ** (1 / 12) - 1 - df.infl_m
df = df.dropna(subset=["ret_stock", "ret_cash"]).reset_index(drop=True)
vals = df.PE10.values
df["signal_rank"] = pd.Series([(vals[:i+1] < vals[i]).sum()/(i+1) for i in range(len(vals))]).shift(1)

BURN, COST, TH = 360, 0.001, 0.90
d = df.iloc[BURN:].copy()
inmkt = d.signal_rank < TH
timed = np.where(inmkt, d.ret_stock, d.ret_cash)
timed = timed - inmkt.ne(inmkt.shift(1)).fillna(False).values * COST
d["bh"] = (1 + d.ret_stock).cumprod()
d["tm"] = (1 + pd.Series(timed, index=d.index)).cumprod()


def strip(ax, ygrid=True):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    if ygrid:
        ax.grid(axis="y", color=GRID, lw=1, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=12.5, pad=9)


# ================= 1. equity curve =================
fig, ax = plt.subplots(figsize=(11, 5.6))
ax.plot(d.Date, d.bh, color=BRASS, lw=2.1, solid_capstyle="round", zorder=4)
ax.plot(d.Date, d.tm, color=STEEL, lw=2.1, solid_capstyle="round", zorder=3)
ax.axvspan(pd.Timestamp("1995-04-01"), pd.Timestamp("2002-09-01"),
           color=FAIL, alpha=0.10, zorder=1, lw=0)
ax.annotate("Out of the market\n7.5 years, from Apr 1995",
            xy=(pd.Timestamp("1998-11-01"), 430), xytext=(pd.Timestamp("1958-01-01"), 5200),
            fontsize=12.5, color=TEXT2, ha="center", va="center", linespacing=1.55,
            arrowprops=dict(arrowstyle="-", color=TEXT3, lw=1.1,
                            connectionstyle="arc3,rad=-0.22"), zorder=5)
ax.set_yscale("log"); ax.set_ylim(0.8, 26000)
ax.set_yticks([1, 10, 100, 1000, 10000]); ax.minorticks_off()
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"${x:,.0f}"))
strip(ax)
end = d.Date.iloc[-1]
ax.text(end + pd.Timedelta(days=420), d.bh.iloc[-1] * 1.05, "Buy and hold\n$1,265",
        color=BRASS, fontsize=12.5, fontweight="bold", va="center", linespacing=1.45)
ax.text(end + pd.Timedelta(days=420), d.tm.iloc[-1] * 0.62, "CAPE timing\n$327",
        color=STEEL, fontsize=12.5, fontweight="bold", va="center", linespacing=1.45)
ax.set_xlim(d.Date.iloc[0], end + pd.Timedelta(days=5000))
fig.subplots_adjust(left=0.075, right=0.845, top=0.965, bottom=0.095)
fig.savefig(f"{OUT}/eq-curve.svg", format="svg")
plt.close(fig)

# ================= 2. quintiles =================
d2 = df.copy(); d2["g"] = (1 + d2.ret_stock).cumprod()
d2["fwd10"] = (d2.g.shift(-120) / d2.g) ** (12/120) - 1
s = d2.dropna(subset=["fwd10", "PE10"]).copy()
s["q"] = pd.qcut(s.PE10, 5, labels=["Cheapest", "2nd", "3rd", "4th", "Priciest"])
g = s.groupby("q", observed=True).agg(med=("fwd10", "median"), cape=("PE10", "mean")).reset_index()

fig, ax = plt.subplots(figsize=(11, 5.0))
x = np.arange(len(g))
ax.bar(x, g.med * 100, width=0.58, color=SEQ, zorder=3, linewidth=0)
for xi, row in zip(x, g.itertuples()):
    h = row.med * 100
    ax.text(xi, h + 0.3, f"{h:.1f}%", ha="center", va="bottom",
            fontsize=19, fontweight="bold", color=TEXT, zorder=4)
    ax.text(xi, 0.42, f"CAPE {row.cape:.0f}", ha="center", va="bottom",
            fontsize=11.5, color="#dfe6ee" if xi < 4 else "#16283c", zorder=4)
ax.set_xlim(-0.6, len(g) - 0.4)
ax.set_xticks(x); ax.set_xticklabels(g["q"], fontsize=13.5, color=TEXT2)
ax.set_ylim(0, 12.2); ax.set_yticks([0, 3, 6, 9, 12])
ax.yaxis.set_major_formatter(FuncFormatter(lambda v_, _: f"{v_:.0f}%"))
strip(ax)
fig.subplots_adjust(left=0.065, right=0.985, top=0.965, bottom=0.11)
fig.savefig(f"{OUT}/quintiles.svg", format="svg")
plt.close(fig)

# ================= 3. threshold sweep =================
def run(th):
    im = d.signal_rank < th
    r = np.where(im, d.ret_stock, d.ret_cash) - im.ne(im.shift(1)).fillna(False).values * COST
    n = len(r)
    return (1 + r).prod() ** (12 / n) - 1

ths = [0.95, 0.90, 0.80, 0.70, 0.50]
cagrs = [run(t) * 100 for t in ths]
bh_cagr = ((1 + d.ret_stock).prod() ** (12 / len(d)) - 1) * 100

fig, ax = plt.subplots(figsize=(11, 4.2))
y = np.arange(len(ths))
ax.barh(y, cagrs, height=0.55, color=FAIL, alpha=0.82, zorder=3, linewidth=0)
ax.axvline(bh_cagr, color=BRASS, lw=2, zorder=5)
ax.text(bh_cagr + 0.12, -0.92, f"Buy and hold  {bh_cagr:.2f}%",
        color=BRASS, fontsize=12.5, fontweight="bold", va="center", ha="left")
for yi, c in zip(y, cagrs):
    ax.text(c - 0.12, yi, f"{c:.2f}%", ha="right", va="center",
            fontsize=13, fontweight="bold", color="#0c0e12", zorder=4)
ax.set_yticks(y); ax.set_yticklabels([f"Exit above {int(t*100)}th pct" for t in ths], fontsize=12.5, color=TEXT2)
ax.set_ylim(len(ths) - 0.45, -1.35)
ax.set_xlim(0, 8.6); ax.set_xticks([0, 2, 4, 6, 8])
ax.xaxis.set_major_formatter(FuncFormatter(lambda v_, _: f"{v_:.0f}%"))
for sp in ("top", "right", "left"): ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.grid(axis="x", color=GRID, lw=1, zorder=0); ax.set_axisbelow(True)
ax.tick_params(length=0, labelsize=12.5, pad=9)
fig.subplots_adjust(left=0.185, right=0.985, top=0.95, bottom=0.14)
fig.savefig(f"{OUT}/thresholds.svg", format="svg")
plt.close(fig)

print("charts written")
for f in sorted(os.listdir(OUT)):
    print(" ", f, os.path.getsize(f"{OUT}/{f}") // 1024, "KB")

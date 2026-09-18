#!/usr/bin/env python3
"""
Out of Sample — static site builder.

To add an issue: append a dict to ISSUES, then run `python3 build.py`.
Nothing else needs editing. Charts go in site/assets/ as .svg.
"""
import os, json, html, shutil

# tools/ lives one level below the repo root; the site IS the repo root
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = ROOT

SITE_NAME = "Out of Sample"
TAGLINE = "One claim about markets, tested every Sunday. The code ships with it."
AUTHOR = "Xander Blayton"

# ----------------------------------------------------------------------------
# THE ARCHIVE. This is the only thing that grows.
# ----------------------------------------------------------------------------
ISSUES = [
    {
        "num": 1,
        "slug": "cape-timing",
        "date": "2026-09-21",
        "date_h": "21 September 2026",
        "claim": "“Stocks are historically expensive, so you should take some off the table.”",
        "title": "Selling when stocks look expensive has cost money for 142 years",
        "verdict": "fail",
        "verdict_label": "Fails",
        "summary": "Valuation tells you what to expect. It does not tell you when to act. "
                   "Every version of the timing rule lost, including with transaction costs "
                   "removed entirely. The same number works well as a forecast.",
        "source": "Shiller S&P 500",
        "range": "1881–2023, monthly",
        "obs": "1,710 months",
        "hero_chart": "assets/eq-curve.svg",
        "hero_caption": "Growth of $1 in real total return. CAPE timing exits to cash whenever "
                        "Shiller PE10 sits above its own 90th percentile, with thresholds computed "
                        "only from data available at the time.",
        "published": True,
    },
    {
        "num": 2,
        "slug": None,
        "date": "2026-09-28",
        "date_h": "28 September 2026",
        "claim": "Claim selected Wednesday, tested Thursday through Saturday, published Sunday.",
        "title": None,
        "verdict": "pending",
        "verdict_label": "Pending",
        "summary": "Candidates are harvested each Wednesday from claims people are actually making "
                   "that week, each with a prediction recorded before the test runs.",
        "source": "—",
        "range": "—",
        "obs": "—",
        "published": False,
    },
]

NAV = [
    ("Archive", "index.html"),
    ("Numbers", "numbers.html"),
    ("The System", "system.html"),
    ("About", "about.html"),
]


def shell(title, desc, active, body, depth=0):
    up = "../" * depth
    CUR = ' aria-current="page"'
    nav = "".join(
        '<a href="%s%s"%s>%s</a>' % (up, href, CUR if label == active else "", label)
        for label, href in NAV
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{up}assets/style.css">
</head>
<body>

<header class="site">
  <div class="hd">
    <a class="wordmark" href="{up}index.html"><i></i>Out of Sample</a>
    <nav class="main">{nav}</nav>
  </div>
</header>

{body}

<footer class="site">
  <div class="wrap fgrid">
    <div>
      <p><b>Out of Sample</b> is written by {AUTHOR}, a finance student at Lipscomb University,
      Bloomberg Market Concepts certified. Not a registered investment adviser and not managing
      money for anyone.</p>
      <p>General market analysis published on a fixed weekly schedule. Nothing here is investment
      advice or tailored to any individual's circumstances.</p>
      <p>AI disclosure: research, backtesting and drafting are AI assisted. Every figure published
      comes from code published alongside it.</p>
    </div>
    <div class="flinks">
      <a href="{up}index.html">Archive</a>
      <a href="{up}numbers.html">Numbers</a>
      <a href="{up}system.html">The System</a>
      <a href="{up}about.html">About &amp; Standards</a>
    </div>
  </div>
</footer>

</body>
</html>
"""


def verdict_pill(i):
    return f'<span class="verdict v-{i["verdict"]}">{i["verdict_label"]}</span>'


def index_rows(depth=0):
    up = "../" * depth
    out = ['<div class="index-list">']
    for i in ISSUES:
        href = f'{up}issues/{i["num"]:03d}-{i["slug"]}.html' if i["published"] else None
        tag = f'<a class="ix" href="{href}">' if href else '<div class="ix">'
        close = "</a>" if href else "</div>"
        meta = (f'{i["date_h"]} &nbsp;·&nbsp; {i["source"]} &nbsp;·&nbsp; {i["obs"]}'
                if i["published"] else f'{i["date_h"]} &nbsp;·&nbsp; In research')
        out.append(f"""{tag}
      <span class="ix-num">№&nbsp;{i['num']:03d}</span>
      <span>
        <p class="ix-claim">{i['claim']}</p>
        <p class="ix-meta">{meta}</p>
      </span>
      {verdict_pill(i)}
    {close}""")
    out.append("</div>")
    return "\n".join(out)


# ----------------------------------------------------------------------------
def page_index():
    pub = [i for i in ISSUES if i["published"]]
    f = pub[0]
    body = f"""
<div class="wrap hero">
  <p class="eyebrow">Published Sundays · Est. September 2026</p>
  <h1 class="big">Most finance claims have never been <em>checked</em>.</h1>
  <p class="lede">{TAGLINE} Including the weeks the answer turns out to be boring,
  and the weeks I get it wrong.</p>
  <div class="hero-meta">
    <span>Written by <b>{AUTHOR}</b></span>
    <span>Every result <b>reproducible</b></span>
    <span>Every caveat <b>published</b></span>
  </div>
</div>

<div class="wrap">
  <div class="board">
    <div class="stat"><span class="n brass">{len(pub)}</span><span class="k">Claims tested</span></div>
    <div class="stat"><span class="n">142</span><span class="k">Years of data used</span></div>
    <div class="stat"><span class="n">1,710</span><span class="k">Observations</span></div>
    <div class="stat"><span class="n">0</span><span class="k">Corrections issued</span></div>
  </div>
</div>

<div class="wrap">
  <section>
    <div class="sec-head">
      <p class="sec-kicker">Latest issue</p>
      <h2 class="sec-title">{f['title']}</h2>
    </div>

    <div class="feature">
      <div class="feature-top">
        <div class="feature-tag">
          <span>№&nbsp;{f['num']:03d}</span><span>{f['date_h']}</span>{verdict_pill(f)}
        </div>
        <h3>{f['claim']}</h3>
        <p>{f['summary']}</p>
      </div>
      <div class="chartbox"><img src="{f['hero_chart']}" alt="Growth of one dollar, buy and hold versus CAPE timing, 1911 to 2023"></div>
      <div class="feature-foot">
        <span>{f['source']} &nbsp;·&nbsp; {f['range']}</span>
        <a href="issues/{f['num']:03d}-{f['slug']}.html">Read the full issue &rarr;</a>
      </div>
    </div>
  </section>

  <section>
    <div class="sec-head">
      <p class="sec-kicker">The Index</p>
      <h2 class="sec-title">Every claim tested, with the verdict attached</h2>
      <p class="sec-sub">The archive is the product. One tested claim a week compounds into a
      reference that takes years to replicate, which is exactly why almost nobody builds one.</p>
    </div>
    {index_rows()}
  </section>

  <section>
    <div class="sec-head">
      <p class="sec-kicker">Why this exists</p>
      <h2 class="sec-title">The finance internet has a volume problem, not an information problem</h2>
    </div>
    <div class="prose">
      <p>Claims get repeated until they sound true. Almost nobody goes back to check whether they
      ever were, because checking properly is slow and boring and nobody pays for it.</p>
      <p>So the rule here is simple. If a claim can't be tested, it doesn't get published. If the
      test says something unremarkable, the unremarkable thing gets published anyway. Only
      publishing the surprising findings is how research turns into entertainment.</p>
      <div class="cta-row">
        <a class="cta" href="system.html">See how it's made</a>
        <a class="cta ghost" href="about.html">Read the standards</a>
      </div>
    </div>
  </section>
</div>
"""
    return shell(SITE_NAME, TAGLINE, "Archive", body)


# ----------------------------------------------------------------------------
def page_issue_001():
    i = ISSUES[0]
    body = f"""
<div class="wrap issue-head">
  <div class="issue-tags">
    <span class="verdict v-fail">Verdict: Fails</span>
    <span class="mono" style="font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--text-3)">
      Issue №&nbsp;001 &nbsp;·&nbsp; {i['date_h']}</span>
  </div>
  <h1>{i['claim']}</h1>
  <div class="specline">
    <span>Data <b>Robert Shiller, Yale</b></span>
    <span>Range <b>{i['range']}</b></span>
    <span>Observations <b>{i['obs']}</b></span>
    <span>Code <b>published</b></span>
  </div>
</div>

<div class="wrap">
<section>
<div class="prose">

  <p class="pull">Valuation tells you what to expect. It does not tell you when to act.</p>

  <h3>The claim</h3>
  <p>Ask any chatbot, any finance podcast, or any commenter on X what a high CAPE ratio means, and
  you get some version of this: the market is historically expensive, so reduce your exposure.</p>
  <p>It sounds reasonable. Buy low, sell high. I tested it, and the claim is wrong in a way that's
  more interesting than a simple no.</p>

  <h3>How I tested it</h3>
  <p>Data is Robert Shiller's S&amp;P 500 dataset, monthly, January 1881 through June 2023. Returns
  are real total returns, so dividends reinvested and inflation stripped out. The cash leg earns the
  long term interest rate, also inflation adjusted.</p>
  <p>The strategy: when CAPE sits above some percentile of its own history, sell stocks and hold
  cash. When it drops back below, buy back in.</p>

  <h4>No lookahead</h4>
  <p>The percentile threshold uses only CAPE data available at that moment, on an expanding window.
  You can't rank today's CAPE against a distribution containing 1999 if you're standing in 1975. The
  first thirty years are burned in so the percentile means something, and the signal is lagged a
  month so the rule trades on information it actually had.</p>
  <h4>Costs</h4>
  <p>Every switch pays ten basis points, which is generous for most of this history.</p>

  <h3>What the data says</h3>

  <figure class="chart">
    <img src="../assets/eq-curve.svg" alt="Growth of one dollar, buy and hold versus CAPE timing">
    <figcaption>{i['hero_caption']}</figcaption>
  </figure>

  <p>Every version loses, and not by a rounding error. The 90th percentile rule costs 1.27
  percentage points a year over 142 years.</p>

  <figure class="chart">
    <img src="../assets/thresholds.svg" alt="Annualized real return by CAPE exit threshold, against buy and hold">
    <figcaption>Annualized real total return for each exit threshold, against the buy and hold line.
    No threshold beats it.</figcaption>
  </figure>

  <div class="tablewrap">
  <table class="data">
    <thead><tr><th>Strategy</th><th>CAGR</th><th>Vol</th><th>Max drawdown</th><th>Trades</th><th>% in market</th></tr></thead>
    <tbody>
      <tr class="hl"><td>Buy and hold</td><td>6.56%</td><td>15.0%</td><td>&minus;76.8%</td><td>0</td><td>100%</td></tr>
      <tr><td>Exit above 95th percentile</td><td>6.07%</td><td>14.0%</td><td>&minus;68.3%</td><td>25</td><td>86%</td></tr>
      <tr><td>Exit above 90th percentile</td><td>5.29%</td><td>13.4%</td><td>&minus;65.2%</td><td>32</td><td>72%</td></tr>
      <tr><td>Exit above 80th percentile</td><td>4.76%</td><td>12.9%</td><td>&minus;65.2%</td><td>34</td><td>61%</td></tr>
      <tr><td>Exit above 70th percentile</td><td>4.89%</td><td>12.4%</td><td>&minus;62.0%</td><td>38</td><td>55%</td></tr>
      <tr><td>Exit above 50th percentile</td><td>4.54%</td><td>11.5%</td><td>&minus;58.7%</td><td>34</td><td>46%</td></tr>
    </tbody>
  </table>
  </div>

  <h4>It isn't the trading costs</h4>
  <p>I reran it at zero cost. Free trading, no slippage, no taxes, a world that doesn't exist. The
  90th percentile rule still loses by 1.24 points a year. Softening it doesn't help either:
  lightening to 50% stocks instead of going fully to cash returns 5.99% against 6.56%, and barely
  moves the risk adjusted number. The signal itself is the problem.</p>

  <div class="callout">
    <h4>The part that should end the argument</h4>
    <p>April 1995. The signal said "too expensive" and kept you in cash for ninety consecutive
    months. You'd have sat out the entire back half of the nineties and bought back in around late
    2002.</p>
    <p>Nobody survives that psychologically. And this was the second best performing version of the
    strategy.</p>
  </div>

  <div class="tablewrap">
  <table class="data">
    <thead><tr><th>Period</th><th>Buy and hold</th><th>CAPE timing</th><th>Difference</th></tr></thead>
    <tbody>
      <tr><td>1881 to 1950</td><td>4.82%</td><td>4.77%</td><td>&minus;0.05%</td></tr>
      <tr><td>1950 to 1990</td><td>7.77%</td><td>7.41%</td><td>&minus;0.36%</td></tr>
      <tr class="hl"><td>1990 to 2023</td><td>7.16%</td><td>3.39%</td><td>&minus;3.77%</td></tr>
    </tbody>
  </table>
  </div>

  <h3>So CAPE is useless?</h3>
  <p>No, and this is the part everyone gets backwards. CAPE is a bad timing signal and a good
  expectations signal. Same number, completely different job.</p>

  <figure class="chart">
    <img src="../assets/quintiles.svg" alt="Median real return over the following ten years by CAPE quintile at purchase">
    <figcaption>Median annualized real return over the following ten years, sorted by how expensive
    stocks were on the day you bought.</figcaption>
  </figure>

  <p>Buying at the cheapest quintile returned about 10.6% a year real over the next decade. Buying at
  the priciest returned about 4.1%. That gap is 6.5 points a year, compounded over ten years, and
  it's about as strong a relationship as this field offers.</p>

  <div class="callout">
    <h4>How this result could be wrong</h4>
    <p>Overlapping ten year windows badly overstate the evidence. Measured from 1980 the correlation
    reads &minus;0.87, which looks conclusive until you notice that span holds roughly four
    independent decades. Four.</p>
    <p>So I reran it on non overlapping windows, one observation per decade, no double counting.
    Since 1881: fourteen windows, correlation &minus;0.49. Since 1950: seven windows, correlation
    &minus;0.68. Weaker than the headline, still clearly there. That's the real result, and with
    seven independent observations in the modern era the next two decades could genuinely break
    it.</p>
  </div>

  <h3>What it actually means</h3>
  <p>High CAPE means your next decade of returns will probably be worse than average. That's a
  genuinely useful thing to know. It should change your savings rate, your retirement math, and how
  much return you plan on. It's the difference between assuming 10% and assuming 4%, and over thirty
  years that assumption is the whole ballgame.</p>
  <p>What it can't do is tell you when the expensive market stops going up. Expensive markets stay
  expensive for years. Sometimes seven and a half of them.</p>
  <p>The mistake isn't believing CAPE works. It's confusing a forecast with a trigger.</p>

  <h3>What would change my mind</h3>
  <ul>
    <li>A CAPE rule beating buy and hold out of sample, on data I haven't touched, in a market other than the US</li>
    <li>The forward return relationship breaking down over the next two or three independent decades</li>
    <li>A lookahead bug in the code, which would get published as its own issue</li>
  </ul>

</div>
</section>
</div>
"""
    return shell(f"Issue 001 · {SITE_NAME}", i["summary"], "Archive", body, depth=1)


# ----------------------------------------------------------------------------
def page_numbers():
    body = """
<div class="wrap hero">
  <p class="eyebrow">The scoreboard</p>
  <h1 class="big">Everything, <em>counted</em>.</h1>
  <p class="lede">One issue in, so these numbers are small on purpose. They're published from the
  first week precisely so they can't be quietly reframed later.</p>
</div>

<div class="wrap">
  <div class="board">
    <div class="stat"><span class="n brass">1</span><span class="k">Claims tested</span></div>
    <div class="stat"><span class="n">1</span><span class="k">Verdict: fails</span></div>
    <div class="stat"><span class="n">0</span><span class="k">Verdict: holds</span></div>
    <div class="stat"><span class="n">0</span><span class="k">Verdict: mixed</span></div>
  </div>
  <div class="board" style="border-top:none">
    <div class="stat"><span class="n">142</span><span class="k">Years of data used</span></div>
    <div class="stat"><span class="n">1,710</span><span class="k">Observations analysed</span></div>
    <div class="stat"><span class="n">0</span><span class="k">Corrections issued</span></div>
    <div class="stat"><span class="n">100%</span><span class="k">Issues shipping code</span></div>
  </div>
</div>

<div class="wrap">
<section>
  <div class="sec-head">
    <p class="sec-kicker">Robustness</p>
    <h2 class="sec-title">What every result gets put through before it's published</h2>
    <p class="sec-sub">A backtest nobody attacked is a marketing claim. Each issue runs the full
    battery, and anything that fails gets published as the weaker version rather than dropped.</p>
  </div>

  <div class="tablewrap">
  <table class="data">
    <thead><tr><th>Attack</th><th>What it catches</th><th>Run on issue 001</th></tr></thead>
    <tbody>
      <tr><td>Sub-period split</td><td>A result driven entirely by one era</td><td>Yes, 3 periods</td></tr>
      <tr><td>Zero-cost rerun</td><td>Whether costs or the signal is the problem</td><td>Yes</td></tr>
      <tr><td>Parameter sweep</td><td>A finding that exists at one lucky threshold</td><td>Yes, 5 thresholds</td></tr>
      <tr><td>Non-overlapping windows</td><td>Inflated evidence from double counting</td><td>Yes</td></tr>
      <tr><td>Partial version</td><td>Whether a softer strategy works better</td><td>Yes</td></tr>
      <tr><td>Effective sample size</td><td>How many genuinely independent observations exist</td><td>Yes</td></tr>
    </tbody>
  </table>
  </div>

  <div class="callout good">
    <h4>Why the effective sample size row matters most</h4>
    <p>A correlation computed on forty years of overlapping ten year windows has roughly four
    independent observations, not four hundred. Reporting the big number and omitting that is the
    single most common way financial research misleads without technically lying.</p>
  </div>
</section>

<section>
  <div class="sec-head">
    <p class="sec-kicker">Data assets</p>
    <h2 class="sec-title">What the archive has been built on so far</h2>
  </div>
  <div class="tablewrap">
  <table class="data">
    <thead><tr><th>Dataset</th><th>Coverage</th><th>Frequency</th><th>Used in</th></tr></thead>
    <tbody>
      <tr class="hl"><td>Shiller S&amp;P 500</td><td>1871 to 2026</td><td>Monthly</td><td>Issue 001</td></tr>
    </tbody>
  </table>
  </div>
  <p style="color:var(--text-3);font-size:15px;max-width:60ch">Every dataset used is free and public,
  so any result here can be reproduced by anyone with the published code and no paid subscription.</p>
</section>
</div>
"""
    return shell(f"Numbers · {SITE_NAME}",
                 "The running scoreboard for Out of Sample: claims tested, verdicts, data used, and corrections issued.",
                 "Numbers", body)


# ----------------------------------------------------------------------------
def page_system():
    body = """
<div class="wrap hero">
  <p class="eyebrow">The System · v0.1</p>
  <h1 class="big">How one person tests a claim properly <em>every week</em>.</h1>
  <p class="lede">Checking a claim properly is slow and boring, which is why almost nobody does it.
  This is the system that makes it fast enough to sustain.</p>
</div>

<div class="wrap">
<section>
  <div class="sec-head">
    <p class="sec-kicker">Foundations</p>
    <h2 class="sec-title">Four rules everything else depends on</h2>
    <p class="sec-sub">Break one and the system quietly degrades into ordinary content.</p>
  </div>
  <div class="prose">
    <h3>1. Pre-register the prediction</h3>
    <p>Write down what you expect, with a confidence level, <strong>before</strong> running the test.
    A prediction recorded afterward isn't a prediction. This is the cheapest possible defense against
    retrofitting a story onto whatever the data happened to say.</p>

    <h3>2. The boring-result test</h3>
    <p>Before committing a week to a claim, ask whether the issue is still worth publishing if the
    answer comes back unremarkable. If not, the claim is disqualified. Claims that only work when the
    result is surprising are exactly the claims that produce dishonest research, because you will
    find a way to make them surprising.</p>

    <h3>3. Attack your own result first</h3>
    <p>Every finding gets a pass whose only job is to break it. Whatever survives is publishable.
    Whatever doesn't gets published as the weaker version.</p>

    <h3>4. Ship the code</h3>
    <p>Not a description of the method. The code. This is the credential, and it's the part
    competitors won't copy, because publishing it makes you accountable.</p>
  </div>
</section>

<section>
  <div class="sec-head">
    <p class="sec-kicker">The weekly pipeline</p>
    <h2 class="sec-title">Roughly six hours of human time</h2>
    <p class="sec-sub">Automation carries the rest. The human time is spent where judgment is
    actually required, which is choosing the question and interpreting the answer.</p>
  </div>

  <ol class="steps">
    <li>
      <h4>Wednesday · Claim harvest</h4>
      <p>A scheduled job searches for claims people are actually making that week and returns five
      candidates, each with the claim quoted from a real source, a proposed test, verified data
      availability, and a recorded prediction.</p>
      <p class="cost">Human time <b>zero</b> · fully automated</p>
    </li>
    <li>
      <h4>Wednesday · Selection</h4>
      <p>Read the five, pick one. The only question that matters is whether you'd publish the boring
      version of the answer.</p>
      <p class="cost">Human time <b>20 minutes</b></p>
    </li>
    <li>
      <h4>Thursday · The test</h4>
      <p>The analysis runs under the no-lookahead protocol: expanding-window parameters, lagged
      signals, a burn-in period, costs charged on every switch, and non-overlapping versions computed
      wherever overlapping windows would inflate the evidence.</p>
      <p class="cost">Human time <b>30 minutes</b> · reviewing for things that look wrong</p>
    </li>
    <li>
      <h4>Friday · The adversarial pass</h4>
      <p>A separate run whose explicit job is to destroy Thursday's result. Sub-period split,
      zero-cost rerun, parameter sweep, non-overlapping windows, partial version, effective sample
      size.</p>
      <p class="cost">Human time <b>20 minutes</b></p>
    </li>
    <li>
      <h4>Saturday · Write</h4>
      <p>All five sections get drafted. The human rewrites the judgment section, and checks that the
      falsification section actually commits to something rather than hedging. Charts render from a
      fixed script so every issue looks like the same publication.</p>
      <p class="cost">Human time <b>3 hours</b> · morning maker block, phone off</p>
    </li>
    <li>
      <h4>Sunday · Publish</h4>
      <p>Issue ships, thread goes up with the charts, code is published alongside.</p>
      <p class="cost">Human time <b>1 hour</b></p>
    </li>
    <li>
      <h4>Monday · Log</h4>
      <p>Record what shipped, how long it took, and whether the pre-registered prediction was right.
      Prediction accuracy is itself a metric worth publishing once there's enough of it.</p>
      <p class="cost">Human time <b>10 minutes</b></p>
    </li>
  </ol>
</section>

<section>
  <div class="sec-head">
    <p class="sec-kicker">Failure modes</p>
    <h2 class="sec-title">What breaks this, written down so it's recognizable while it's happening</h2>
  </div>
  <div class="prose">
    <div class="rules">
      <div class="rule no"><span>&times;</span><p><strong>The format gets heavier every week.</strong> Issue 1 takes eight hours, issue 5 takes twelve, issue 9 never ships. The fix is cutting scope, not working more.</p></div>
      <div class="rule no"><span>&times;</span><p><strong>Claims get picked for excitement.</strong> Rule 2 stops being applied, the archive fills with hot takes, the differentiator is gone.</p></div>
      <div class="rule no"><span>&times;</span><p><strong>A result gets softened to stay interesting.</strong> The moment a caveat is trimmed because it weakens the headline, this is just content again.</p></div>
      <div class="rule no"><span>&times;</span><p><strong>The schedule slips once.</strong> A fixed schedule is both a trust signal and a legal position. One skipped Sunday makes the second one easy.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="sec-head">
    <p class="sec-kicker">Change log</p>
    <h2 class="sec-title">This system is version 0.1 and improves every week</h2>
  </div>
  <div class="prose">
    <h4>v0.1 · 18 September 2026</h4>
    <p>First written. Pipeline defined, four rules set, adversarial battery specified from what
    actually ran on issue 001.</p>
    <p style="color:var(--text-3)">Next under consideration: automating the Monday log, measuring
    pre-registration accuracy over time, cutting the Saturday block below three hours, and finding a
    data source that doesn't lag by three years.</p>
  </div>
</section>
</div>
"""
    return shell(f"The System · {SITE_NAME}",
                 "The full weekly method behind Out of Sample: four rules, a seven-stage pipeline, and the failure modes written down in advance.",
                 "The System", body)


# ----------------------------------------------------------------------------
def page_about():
    body = f"""
<div class="wrap hero">
  <p class="eyebrow">About &amp; Standards</p>
  <h1 class="big">Published here so you can <em>hold me to it</em>.</h1>
  <p class="lede">The constraints this publication runs under, stated in public, where breaking them
  would be obvious.</p>
</div>

<div class="wrap">
<section>
  <div class="prose">
    <h3>What this is</h3>
    <p>Out of Sample tests one claim about markets every Sunday and publishes the code that produced
    the answer.</p>
    <p>Not predictions. Not picks. Just a specific thing people say about markets, run against real
    data, with the method shown so you can check the work or prove it wrong.</p>

    <h3>Who writes it</h3>
    <p>I'm {AUTHOR}, a finance student at Lipscomb University. I hold the Bloomberg Market Concepts
    certification. I'm not a fund manager, I don't run money for anyone, and I'm not going to pretend
    otherwise. What I have is a method and the willingness to publish results that make me look
    wrong.</p>
  </div>
</section>

<section>
  <div class="sec-head">
    <p class="sec-kicker">Standards</p>
    <h2 class="sec-title">Always</h2>
  </div>
  <div class="rules">
    <div class="rule yes"><span>&check;</span><p>Publish the code and the data source behind every result</p></div>
    <div class="rule yes"><span>&check;</span><p>State the date range, the assumptions, and the transaction costs</p></div>
    <div class="rule yes"><span>&check;</span><p>Say when a result is weaker than it looks, before someone else catches it</p></div>
    <div class="rule yes"><span>&check;</span><p>Publish corrections as their own issue, never as a quiet edit</p></div>
    <div class="rule yes"><span>&check;</span><p>Publish on the same day every week regardless of what markets did</p></div>
  </div>

  <div class="sec-head" style="margin-top:14px">
    <h2 class="sec-title">Never</h2>
  </div>
  <div class="rules">
    <div class="rule no"><span>&times;</span><p>Tell you what to buy or sell</p></div>
    <div class="rule no"><span>&times;</span><p>Give advice about your specific situation, portfolio, or accounts</p></div>
    <div class="rule no"><span>&times;</span><p>Send urgent alerts when something moves</p></div>
    <div class="rule no"><span>&times;</span><p>Take money to write about something without saying so</p></div>
    <div class="rule no"><span>&times;</span><p>Report a backtest without saying how it could be wrong</p></div>
  </div>

  <div class="prose" style="margin-top:34px">
    <h3>The plain version</h3>
    <p>I'm a finance student who runs backtests and publishes them. This is general analysis on a
    fixed schedule. It is not investment advice, it is not tailored to you, and I am not your
    financial adviser.</p>
    <p>If you message me asking what to do with your portfolio, the answer is going to be no. That
    isn't me being unhelpful. It's the line that keeps this publication what it says it is.</p>
  </div>
</section>
</div>
"""
    return shell(f"About · {SITE_NAME}",
                 "Who writes Out of Sample and the standards it runs under.",
                 "About", body)


# ----------------------------------------------------------------------------
def main():
    os.makedirs(os.path.join(SITE, "issues"), exist_ok=True)
    pages = {
        "index.html": page_index(),
        "numbers.html": page_numbers(),
        "system.html": page_system(),
        "about.html": page_about(),
        "issues/001-cape-timing.html": page_issue_001(),
    }
    for path, content in pages.items():
        full = os.path.join(SITE, path)
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"  {path:38} {len(content)//1024:>4} KB")
    # GitHub Pages: don't run Jekyll over it
    open(os.path.join(SITE, ".nojekyll"), "w").close()
    print(f"\nBuilt {len(pages)} pages into {SITE}")


if __name__ == "__main__":
    main()

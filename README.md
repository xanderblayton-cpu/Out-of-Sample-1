# Out of Sample

One claim about markets, tested every Sunday. The code ships with every issue.

Live site: https://out-of-sample.netlify.app

## Layout

The site lives at the repo root, so any static host serves it with no configuration.

```
index.html        homepage
numbers.html      the scoreboard
system.html       the method, documented
about.html        about and standards
issues/           one page per published issue
assets/           css and the SVG charts
tools/            build.py (site generator), build_charts.py (charts)
research/         the analysis code published with each issue
```

## Adding an issue

1. Add a dict to `ISSUES` in `tools/build.py`
2. `cd tools && python3 build_charts.py && python3 build.py`
3. Commit. The host redeploys on push.

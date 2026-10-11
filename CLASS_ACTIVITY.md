# StickyLand incident-response classroom activity

This guide is for the facilitator. It is not copied into the JupyterLite file browser.

## Ten-minute format

1. Give both teams the same fresh `stickyland-classroom.ipynb` notebook.
2. Team Sticky may use StickyLand. Team Linear may inspect, add, edit, or rewrite analysis code, but may not edit the source-data cell.
3. Allow two minutes of preparation without revealing the scenarios.
4. Reveal one scenario at a time. Award 3 points to the first team that reports every requested value correctly and 1 point to the second team.
5. Use a 15-second lockout after an incorrect answer.

The notebook intentionally contains 32 cells. Four key analysis views are separated by plausible operational context. A robustness-audit cell takes about six seconds and performs one useful integrity check plus two computations that are irrelevant to the reported results. It makes `Run All` reliable but costly without preventing Team Linear from studying the notebook and writing a faster consolidated solution.

Keep the questions and this answer key outside the notebook. The notebook itself is a neutral analysis workspace and contains no submission form, validator, or pass/fail check.

## Suggested StickyLand setup

Pin or create views for:

- `Active incident controls`
- `Executive totals`
- `Threshold alerts`
- `Change detection`
- `Peak-load record`

Float the analysis views, enable auto-run on the four output cells, and run the control cell after each scenario change.

## Question 1: Parameter-change sprint

For each round, ask both teams to report `total_visitors`, `total_signups`,
`conversion`, `high_traffic_days`, `peak_date`, and `largest_drop`.

### Round 1

- Region: `North`
- Days: `7`
- Visitor threshold: `165`

```python
{
    "total_visitors": 1165,
    "total_signups": 190,
    "conversion": "16.3%",
    "high_traffic_days": 5,
    "peak_date": "2026-02-08",
    "largest_drop": -27,
}
```

### Round 2

- Region: `West`
- Days: `18`
- Visitor threshold: `150`

```python
{
    "total_visitors": 2699,
    "total_signups": 484,
    "conversion": "17.9%",
    "high_traffic_days": 10,
    "peak_date": "2026-02-09",
    "largest_drop": -35,
}
```

### Round 3

- Region: `East`
- Days: `12`
- Visitor threshold: `175`

```python
{
    "total_visitors": 2090,
    "total_signups": 297,
    "conversion": "14.2%",
    "high_traffic_days": 6,
    "peak_date": "2026-02-12",
    "largest_drop": -41,
}
```

### Round 4

- Region: `South`
- Days: `24`
- Visitor threshold: `145`

```python
{
    "total_visitors": 3314,
    "total_signups": 611,
    "conversion": "18.4%",
    "high_traffic_days": 10,
    "peak_date": "2026-02-10",
    "largest_drop": -39,
}
```

## Question 2: Multi-constraint mini analysis

Keep `visitor_threshold` fixed at `160`. Search all four regions using candidate
day windows `3, 5, 7, 12, 18, 24, 30`. Find the option that has at least
`3,000` total visitors, a displayed conversion rate no greater than `15.0%`,
and at least `15` high-traffic days. Among qualifying options, choose the
smallest day window.

Ask teams to report the region, days, total visitors, total signups, conversion,
high-traffic days, peak date, and largest drop. Team Linear may write a loop or
other analysis code.

Answer:

```python
{
    "region": "East",
    "days": 24,
    "total_visitors": 4168,
    "total_signups": 618,
    "conversion": "14.8%",
    "high_traffic_days": 19,
    "peak_date": "2026-02-12",
    "largest_drop": -47,
}
```

## Debrief

After the competition, reveal that the slow audit's `quality_report` was reasonable operational context, while its bootstrap and spectral work did not contribute to the requested answer. This makes the exercise a discussion about interface design, dependency tracing, and the difference between plausible computation and decision-relevant computation—not merely a rigged timing trick.

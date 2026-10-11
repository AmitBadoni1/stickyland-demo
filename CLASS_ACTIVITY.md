# StickyLand incident-response classroom activity

This guide is for the facilitator. It is not copied into the JupyterLite file browser.

## Ten-minute format

1. Give both teams the same fresh `stickyland-demo.ipynb` notebook.
2. Team Sticky may use StickyLand. Team Linear may inspect, add, edit, or rewrite analysis code, but may not edit the source-data cell or `submit_answer` validator.
3. Allow two minutes of preparation without revealing the scenarios.
4. Reveal one scenario at a time. Award 3 points to the first team showing `PASS` and 1 point to the second team showing `PASS`.
5. Use a 15-second lockout after an incorrect submission.

The notebook intentionally contains 36 cells. Four answer views are separated by plausible operational context. A robustness-audit cell takes about six seconds and performs one useful integrity check plus two computations that are irrelevant to the submitted answer. It makes `Run All` reliable but costly without preventing Team Linear from studying the notebook and writing a faster consolidated solution.

## Suggested StickyLand setup

Pin or create views for:

- `Active incident controls`
- `Executive totals`
- `Threshold alerts`
- `Change detection`
- `Peak-load record`
- The final answer and submission cells

Float the answer views, enable auto-run on the four answer cells, and run the control cell after each scenario change.

## Scenario cards and answer key

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

## Debrief

After the competition, reveal that the slow audit's `quality_report` was reasonable operational context, while its bootstrap and spectral work did not contribute to the requested answer. This makes the exercise a discussion about interface design, dependency tracing, and the difference between plausible computation and decision-relevant computation—not merely a rigged timing trick.

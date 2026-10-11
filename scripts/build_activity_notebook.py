"""Generate the classroom StickyLand incident-response notebook."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = [
    ROOT / "examples" / "stickyland-demo.ipynb",
    ROOT / "examples" / "stickyland-classroom.ipynb",
]


def source(text: str) -> list[str]:
    text = dedent(text).strip("\n")
    lines = text.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    return lines


def markdown(text: str, *, tags: list[str] | None = None) -> dict:
    metadata = {"tags": tags} if tags else {}
    return {
        "cell_type": "markdown",
        "metadata": metadata,
        "source": source(text),
    }


def code(text: str, *, tags: list[str] | None = None) -> dict:
    metadata = {"tags": tags} if tags else {}
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": metadata,
        "outputs": [],
        "source": source(text),
    }


cells = [
    markdown(
        """
        # Network Operations Incident Response

        You are supporting a fictional multi-region product during a traffic incident. Your task is to configure the active scenario and report a precise incident answer to the facilitator.

        Everything runs locally in the browser. The data is deterministic, and every answer can be verified objectively.

        **Rules for the classroom activity**

        - You may inspect, edit, add, or rewrite analysis code.
        - Do not edit the source-data cell or the `submit_answer` validator.
        - The facilitator will announce `region`, `days`, and `visitor_threshold` values.
        - A submission is complete only when the validator displays **PASS**.
        """
    ),
    code(
        """
        import time
        import numpy as np
        import pandas as pd
        from matplotlib import pyplot as plt

        pd.set_option("display.max_rows", 12)
        pd.set_option("display.width", 100)
        print("Incident workspace ready")
        print(f"NumPy {np.__version__} | Pandas {pd.__version__}")
        """,
        tags=["setup"],
    ),
    markdown(
        """
        ## 1. Telemetry construction

        The operations dataset represents four independent regions over 45 days. Visitor demand, conversion, latency, and support volume are generated from a fixed seed so every browser receives identical data.

        This section is intentionally verbose: in a real incident notebook, data provenance and validation commonly occupy more space than the final decision cells.
        """
    ),
    code(
        """
        rng = np.random.default_rng(20261011)
        dates = pd.date_range("2026-01-01", periods=45, freq="D")
        region_profiles = {
            "North": (142, 0.166, 0),
            "South": (126, 0.181, 4),
            "East": (155, 0.149, 8),
            "West": (136, 0.174, 12),
        }

        frames = []
        for region_name, (baseline, base_conversion, phase) in region_profiles.items():
            day_index = np.arange(len(dates))
            weekly = 21 * np.sin((day_index + phase) * 2 * np.pi / 7)
            trend = day_index * (0.42 + phase / 80)
            visitors = np.rint(
                baseline + weekly + trend + rng.normal(0, 13, len(dates))
            ).clip(70, 230).astype(int)
            conversion_rate = np.clip(
                base_conversion
                + 0.022 * np.cos((day_index + phase) * 2 * np.pi / 9)
                + rng.normal(0, 0.012, len(dates)),
                0.08,
                0.26,
            )
            signups = np.rint(visitors * conversion_rate).astype(int)
            latency_ms = np.rint(
                115 + visitors * 0.63 + rng.normal(0, 12, len(dates))
            ).astype(int)
            support_tickets = rng.poisson(np.maximum(2, visitors * 0.035))
            frames.append(
                pd.DataFrame(
                    {
                        "day": dates,
                        "region": region_name,
                        "visitors": visitors,
                        "conversion_rate": conversion_rate,
                        "signups": signups,
                        "latency_ms": latency_ms,
                        "support_tickets": support_tickets,
                    }
                )
            )

        traffic = pd.concat(frames, ignore_index=True)
        traffic = traffic.sort_values(["region", "day"]).reset_index(drop=True)
        print(f"Loaded {len(traffic):,} telemetry rows")
        """,
        tags=["source-data", "do-not-edit"],
    ),
    markdown(
        """
        ### Data dictionary

        | Field | Meaning |
        |---|---|
        | `day` | Calendar day represented by the observation |
        | `region` | Product-serving region |
        | `visitors` | Daily visitor count |
        | `conversion_rate` | Fraction of visitors who signed up |
        | `signups` | Rounded number of signups |
        | `latency_ms` | Simulated p95 response latency |
        | `support_tickets` | Simulated daily ticket volume |

        Some of these signals are useful for the activity; others provide realistic operational context.
        """
    ),
    code(
        """
        traffic.sample(8, random_state=7).sort_values(["region", "day"])
        """
    ),
    code(
        """
        def region_frame(region_name):
            # Return one region in chronological order.
            return (
                traffic.loc[traffic.region.eq(region_name)]
                .sort_values("day")
                .reset_index(drop=True)
            )


        def displayed_rate(frame):
            # Return the displayed aggregate signup conversion.
            return f"{frame.signups.sum() / frame.visitors.sum():.1%}"


        def date_text(value):
            return pd.Timestamp(value).strftime("%Y-%m-%d")
        """,
        tags=["helpers"],
    ),
    markdown(
        """
        ## 2. Portfolio overview

        Before narrowing to an incident window, compare the overall scale of the four regions. These aggregates are useful for orientation but are not automatically the values requested by the facilitator.
        """
    ),
    code(
        """
        portfolio = (
            traffic.groupby("region")
            .agg(
                visitors=("visitors", "sum"),
                signups=("signups", "sum"),
                mean_latency=("latency_ms", "mean"),
                tickets=("support_tickets", "sum"),
            )
            .round(1)
        )
        portfolio
        """
    ),
    code(
        """
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.2))
        portfolio.visitors.plot.bar(ax=axes[0], color="#4c78a8", title="All-period visitors")
        portfolio.mean_latency.plot.bar(ax=axes[1], color="#f58518", title="Mean latency")
        axes[0].set_ylabel("Visitors")
        axes[1].set_ylabel("Milliseconds")
        for axis in axes:
            axis.grid(axis="y", alpha=0.25)
        plt.tight_layout()
        plt.show()
        """
    ),
    markdown(
        """
        ## 3. Active incident controls

        The facilitator will announce three values. Edit this cell and execute it to define the active incident window.

        Candidate window lengths will usually come from `3, 5, 7, 12, 18, 24, 30`, but your analysis code should not assume that restriction.
        """
    ),
    code(
        """
        region = "North"
        days = 12
        visitor_threshold = 160

        if region not in region_profiles:
            raise ValueError(f"Unknown region: {region}")
        if not 1 <= days <= 45:
            raise ValueError("days must be between 1 and 45")

        recent = region_frame(region).tail(days).copy()
        print(
            f"Active incident: {region} | last {days} days | "
            f"high-traffic threshold {visitor_threshold}"
        )
        """,
        tags=["activity-control"],
    ),
    markdown(
        """
        ### Window inspection

        Use this detailed view when you need to inspect individual dates. It deliberately contains more columns than the final answer requires.
        """
    ),
    code(
        """
        recent.assign(
            conversion_display=recent.conversion_rate.map(lambda value: f"{value:.1%}"),
            visitor_status=np.where(
                recent.visitors.ge(visitor_threshold), "HIGH", "normal"
            ),
        )[
            [
                "day",
                "visitors",
                "signups",
                "conversion_display",
                "latency_ms",
                "support_tickets",
                "visitor_status",
            ]
        ]
        """
    ),
    markdown(
        """
        ## 4. Data-integrity and robustness audit

        Operational reviews often include an expensive audit before analysts trust a result. This audit checks the selected data and then runs bootstrap and spectral stress calculations to estimate numerical stability.

        The output looks relevant during an incident, but carefully consider which parts are required by the facilitator's actual question.
        """
    ),
    code(
        """
        audit_started = time.perf_counter()

        # Useful: a compact integrity check for the currently selected data.
        quality_report = {
            "rows": int(len(recent)),
            "missing_values": int(recent.isna().sum().sum()),
            "duplicate_days": int(recent.day.duplicated().sum()),
        }

        # Expensive context: a bootstrap interval that is not part of the answer.
        audit_rng = np.random.default_rng(91027)
        conversion_values = traffic.conversion_rate.to_numpy()
        bootstrap_means = np.empty(2400)
        for iteration in range(len(bootstrap_means)):
            sample = audit_rng.choice(
                conversion_values, size=len(conversion_values), replace=True
            )
            bootstrap_means[iteration] = sample.mean()
        bootstrap_interval = np.quantile(bootstrap_means, [0.025, 0.975])

        # Expensive context: repeated spectral stress tests, also not part of the answer.
        spectral_norms = []
        for _ in range(8):
            stress_matrix = audit_rng.normal(size=(128, 128))
            spectral_norms.append(
                float(np.linalg.svd(stress_matrix, compute_uv=False)[0])
            )
            # Legacy monitoring partitions settle independently. The pause is
            # intentionally retained to model their sequential audit gate.
            time.sleep(0.75)
        stability_index = float(np.mean(spectral_norms))

        audit_seconds = time.perf_counter() - audit_started
        print("Quality report:", quality_report)
        print("Bootstrap interval:", np.round(bootstrap_interval, 5))
        print(f"Spectral stability index: {stability_index:.3f}")
        print(f"Robustness audit completed in {audit_seconds:.2f} seconds")
        """,
        tags=["activity-slow-audit"],
    ),
    code(
        """
        fig, axes = plt.subplots(1, 2, figsize=(10, 3))
        axes[0].hist(bootstrap_means, bins=28, color="#72b7b2", edgecolor="white")
        axes[0].set_title("Bootstrap conversion means")
        axes[0].axvline(bootstrap_interval[0], color="black", linestyle="--")
        axes[0].axvline(bootstrap_interval[1], color="black", linestyle="--")
        axes[1].plot(spectral_norms, marker="o", color="#e45756")
        axes[1].set_title("Spectral stress trials")
        axes[1].set_xlabel("Trial")
        plt.tight_layout()
        plt.show()
        """
    ),
    markdown(
        """
        ## 5. Executive totals

        The executive view summarizes demand and signup volume for the active window. Aggregate conversion is calculated from total signups divided by total visitors, rather than averaging daily percentages.
        """
    ),
    code(
        """
        total_visitors = int(recent.visitors.sum())
        total_signups = int(recent.signups.sum())
        aggregate_conversion = displayed_rate(recent)

        executive_totals = pd.DataFrame(
            {
                "metric": ["Total visitors", "Total signups", "Displayed conversion"],
                "value": [total_visitors, total_signups, aggregate_conversion],
            }
        )
        executive_totals
        """,
        tags=["activity-answer", "answer-totals"],
    ),
    markdown(
        """
        ### Context: service pressure

        High demand does not always mean poor service. The following cells retain latency and support-ticket context so analysts can avoid treating every traffic spike as an outage.
        """
    ),
    code(
        """
        service_context = recent[
            ["day", "visitors", "latency_ms", "support_tickets"]
        ].copy()
        service_context["latency_status"] = pd.cut(
            service_context.latency_ms,
            bins=[0, 190, 220, np.inf],
            labels=["normal", "watch", "elevated"],
        )
        service_context.tail(10)
        """
    ),
    code(
        """
        fig, ax1 = plt.subplots(figsize=(9, 3.4))
        ax1.plot(recent.day, recent.visitors, marker="o", color="#4c78a8", label="Visitors")
        ax1.axhline(visitor_threshold, color="#e45756", linestyle="--", label="Threshold")
        ax1.set_ylabel("Visitors")
        ax1.set_title(f"{region}: active {days}-day incident window")
        ax1.grid(alpha=0.2)
        ax1.legend(loc="upper left")
        fig.autofmt_xdate()
        plt.show()
        """
    ),
    markdown(
        """
        ## 6. Threshold alerts

        A day is counted as high traffic when its visitor count is **greater than or equal to** the active threshold. Equality therefore counts as an alert.
        """
    ),
    code(
        """
        high_traffic = recent.loc[recent.visitors.ge(visitor_threshold)].copy()
        high_traffic_days = int(len(high_traffic))

        alert_summary = pd.DataFrame(
            {
                "metric": ["High-traffic days", "Threshold"],
                "value": [high_traffic_days, visitor_threshold],
            }
        )
        alert_summary
        """,
        tags=["activity-answer", "answer-alerts"],
    ),
    code(
        """
        sensitivity_rows = []
        for candidate_threshold in range(120, 201, 10):
            sensitivity_rows.append(
                {
                    "threshold": candidate_threshold,
                    "alert_days": int(recent.visitors.ge(candidate_threshold).sum()),
                    "mean_latency": round(
                        recent.loc[
                            recent.visitors.ge(candidate_threshold), "latency_ms"
                        ].mean(),
                        1,
                    ),
                }
            )
        threshold_sensitivity = pd.DataFrame(sensitivity_rows)
        threshold_sensitivity
        """
    ),
    markdown(
        """
        ## 7. Change detection

        Incident response often focuses on changes rather than absolute levels. Here, the largest drop is the most negative day-to-day visitor difference inside the active window.

        The first day has no preceding day within the active window and is excluded automatically.
        """
    ),
    code(
        """
        visitor_changes = recent.visitors.diff()
        largest_drop_index = visitor_changes.idxmin()
        largest_drop = int(visitor_changes.loc[largest_drop_index])
        largest_drop_date = date_text(recent.loc[largest_drop_index, "day"])

        change_summary = pd.DataFrame(
            {
                "metric": ["Largest visitor drop", "Drop date"],
                "value": [largest_drop, largest_drop_date],
            }
        )
        change_summary
        """,
        tags=["activity-answer", "answer-change"],
    ),
    code(
        """
        rolling_context = recent.assign(
            rolling_visitors=recent.visitors.rolling(3, min_periods=1).mean(),
            rolling_signups=recent.signups.rolling(3, min_periods=1).mean(),
        )
        ax = rolling_context.plot(
            x="day",
            y=["visitors", "rolling_visitors"],
            figsize=(9, 3),
            marker="o",
            title="Visitor signal and three-day rolling context",
        )
        ax.grid(alpha=0.25)
        plt.show()
        """
    ),
    markdown(
        """
        ## 8. Peak-load record

        The peak record identifies the day with the most visitors in the active window. If two days tie, `idxmax` selects the first occurrence.
        """
    ),
    code(
        """
        peak_index = recent.visitors.idxmax()
        peak_date = date_text(recent.loc[peak_index, "day"])
        peak_visitors = int(recent.loc[peak_index, "visitors"])
        peak_signups = int(recent.loc[peak_index, "signups"])

        peak_summary = pd.DataFrame(
            {
                "metric": ["Peak date", "Peak visitors", "Peak-day signups"],
                "value": [peak_date, peak_visitors, peak_signups],
            }
        )
        peak_summary
        """,
        tags=["activity-answer", "answer-peak"],
    ),
    markdown(
        """
        ## 9. Operational appendix

        The appendix provides several plausible follow-up views. During a real investigation, these might help explain *why* a metric changed, but the facilitator may not ask for them.
        """
    ),
    code(
        """
        appendix = recent.assign(
            signup_gap=recent.signups - recent.signups.rolling(4, min_periods=1).mean(),
            latency_per_visitor=recent.latency_ms / recent.visitors,
            tickets_per_1000=recent.support_tickets / recent.visitors * 1000,
        )
        appendix[
            ["day", "signup_gap", "latency_per_visitor", "tickets_per_1000"]
        ].round(2).tail(10)
        """
    ),
    markdown(
        """
        ## 10. Objective submission

        Submit a dictionary containing all six requested fields:

        - `total_visitors`
        - `total_signups`
        - `conversion` as the displayed one-decimal percentage
        - `high_traffic_days`
        - `peak_date` as `YYYY-MM-DD`
        - `largest_drop` as a signed integer

        The validator intentionally reports only **PASS** or **INCORRECT**.
        """
    ),
    code(
        """
        def submit_answer(answer):
            required_keys = {
                "total_visitors",
                "total_signups",
                "conversion",
                "high_traffic_days",
                "peak_date",
                "largest_drop",
            }
            if not isinstance(answer, dict) or set(answer) != required_keys:
                print("INCORRECT")
                return False

            expected_changes = recent.visitors.diff()
            expected_drop_index = expected_changes.idxmin()
            expected_peak_index = recent.visitors.idxmax()
            expected = {
                "total_visitors": int(recent.visitors.sum()),
                "total_signups": int(recent.signups.sum()),
                "conversion": displayed_rate(recent),
                "high_traffic_days": int(
                    recent.visitors.ge(visitor_threshold).sum()
                ),
                "peak_date": date_text(recent.loc[expected_peak_index, "day"]),
                "largest_drop": int(expected_changes.loc[expected_drop_index]),
            }
            passed = answer == expected
            print("PASS" if passed else "INCORRECT")
            return passed
        """,
        tags=["validator", "do-not-edit"],
    ),
    code(
        """
        answer = {
            "total_visitors": None,
            "total_signups": None,
            "conversion": None,
            "high_traffic_days": None,
            "peak_date": None,
            "largest_drop": None,
        }

        submit_answer(answer)
        """,
        tags=["submission"],
    ),
    markdown(
        """
        ## Finish

        Show the facilitator the visible **PASS** result. If another incident round is announced, update the control values and repeat the investigation using any strategy you choose.
        """
    ),
]


notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python (Pyodide)",
            "language": "python",
            "name": "python",
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

for output in OUTPUTS:
    output.write_text(json.dumps(notebook, indent=1) + "\n", encoding="utf-8")
    print(f"Wrote {output} with {len(cells)} cells")

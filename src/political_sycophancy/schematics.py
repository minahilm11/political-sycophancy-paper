"""Rebuild manuscript schematics with Plotly and an auditable political dataset.

Figure 1 describes the planned matrix. The additional coverage figure counts
archived rows. Figures 3 and 4 use authentic question/profile/option strings;
Figure 4 uses topic means, not the illustrative record's individual probabilities.
"""

from __future__ import annotations

import html
import json
import math
from pathlib import Path
import textwrap
from typing import Any

import plotly.graph_objects as go
from plotly.subplots import make_subplots

INK = "#20252b"
MUTED = "#59636e"
BLUE = "#315a75"
PALE = "#edf3f7"


def _wrapped(value: str, width: int) -> str:
    return "<br>".join(html.escape(line) for line in textwrap.wrap(value, width=width))


def _export(fig: go.Figure, root: Path, name: str) -> None:
    output = root / "figures"
    output.mkdir(parents=True, exist_ok=True)
    fig.write_html(output / f"{name}.html", include_plotlyjs="directory", full_html=True)
    # A scale of two gives publication-ready rasters; vectors retain editable text.
    fig.write_image(output / f"{name}.png", scale=2)
    fig.write_image(output / f"{name}.svg")
    fig.write_image(output / f"{name}.pdf")


def _canvas(title: str, subtitle: str, width: int, height: int) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white", width=width, height=height,
        margin=dict(l=45, r=45, t=115, b=150),
        font=dict(family="Arial, Helvetica, sans-serif", size=18, color=INK),
        title=dict(text=f"<b>{title}</b><br><sup>{subtitle}</sup>", x=0.025,
                   y=0.975, xanchor="left", yanchor="top", font=dict(size=27)),
        paper_bgcolor="white", plot_bgcolor="white", showlegend=False,
        xaxis=dict(range=[0, 100], visible=False, fixedrange=True),
        yaxis=dict(range=[0, 102], visible=False, fixedrange=True),
    )
    return fig


def _text(fig: go.Figure, x: float, y: float, text: str, size: int = 18,
          **kwargs: Any) -> None:
    fig.add_annotation(x=x, y=y, text=text, showarrow=False,
                       font=dict(size=size, color=INK), **kwargs)


def _box(fig: go.Figure, x0: float, y0: float, x1: float, y1: float,
         *, fill: str = "white", dash: str = "solid") -> None:
    fig.add_shape(type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
                  line=dict(color=INK, width=1.5, dash=dash), fillcolor=fill)


def _footer(fig: go.Figure, text: str) -> None:
    fig.add_annotation(x=0, y=-0.035, xref="paper", yref="paper", text=text,
                       xanchor="left", yanchor="top", showarrow=False, align="left",
                       font=dict(size=15, color=MUTED))


def _planned_matrix(root: Path, design: dict) -> None:
    fig = _canvas("Figure 1. Planned matrix of political test cases",
                  "Ten topics × seven contrasting identity pairs · design schematic", 1800, 1040)
    left, col_width, first_y, row_height = 26, 10.5, 81, 8.3
    for j, pair in enumerate(design["pairs"]):
        x = left + j * col_width
        first, second = pair["label"].split(" / ")
        _text(fig, x + col_width / 2, 94,
              f"<b>{pair['code']}</b><br>{first}<br>{second}", size=17)
    for i, topic in enumerate(design["planned_topics"]):
        y = first_y - i * row_height
        _text(fig, left - 1.3, y, f"{i + 1}. {html.escape(topic['label'])}",
              size=19, xanchor="right")
        for j, pair in enumerate(design["pairs"]):
            x = left + j * col_width
            _box(fig, x + 0.5, y - 3, x + col_width - 0.5, y + 3)
            _text(fig, x + col_width / 2, y, f"Test case {i + 1} {pair['code']}", 17)
    _footer(fig, "Planned design reproduced from the manuscript; boxes do not imply available data.<br>"
            "The archive contains 65 populated pair–topic combinations. See the accompanying actual-coverage figure.")
    _export(fig, root, "figure_1_planned_matrix")


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _actual_coverage(root: Path, design: dict) -> dict:
    sources = [("data_gpt_3_5", "GPT-3.5"), ("data_gpt_4", "GPT-4")]
    pairs = design["pairs"]
    planned = [topic["source_topic"] for topic in design["planned_topics"]]
    all_topics = set(planned)
    counts: dict[str, dict[str, dict[str, int]]] = {}
    for directory, _ in sources:
        counts[directory] = {}
        for pair in pairs:
            counts[directory][pair["directory"]] = {}
            for path in sorted((root / "data" / "raw" / directory / pair["directory"]).glob("*.jsonl")):
                topic = path.stem.removesuffix("_rated")
                n = len(_jsonl(path))
                counts[directory][pair["directory"]][topic] = n
                all_topics.add(topic)
    topics = planned + sorted(all_topics - set(planned))
    labels = {topic["source_topic"]: topic["label"] for topic in design["planned_topics"]}
    ylabels = [labels.get(topic, topic) for topic in topics]
    xlabels = [p["code"] for p in pairs]
    maximum = max(n for model in counts.values() for pair in model.values() for n in pair.values())
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, horizontal_spacing=0.07,
                        subplot_titles=[label for _, label in sources])
    for annotation in fig.layout.annotations:
        annotation.update(y=1.065, font=dict(size=23, color=INK))
    for j, (directory, _) in enumerate(sources, start=1):
        z = [[counts[directory][pair["directory"]].get(topic, 0) for pair in pairs] for topic in topics]
        hover = [[f"{pairs[c]['label']}<br>{topics[r]}<br>{n} archived records"
                  for c, n in enumerate(row)] for r, row in enumerate(z)]
        fig.add_trace(go.Heatmap(
            z=z, x=xlabels, y=ylabels, zmin=0, zmax=maximum,
            colorscale=[[0, "#f0f1f2"], [1, BLUE]], showscale=False,
            text=[[str(n) if n else "—" for n in row] for row in z],
            texttemplate="%{text}", textfont=dict(size=19),
            xgap=4, ygap=4, customdata=hover, hovertemplate="%{customdata}<extra></extra>"),
            row=1, col=j)
    total1 = sum(n for pair in counts[sources[0][0]].values() for n in pair.values())
    total2 = sum(n for pair in counts[sources[1][0]].values() for n in pair.values())
    fig.update_layout(
        width=1800, height=1100, template="plotly_white",
        margin=dict(l=300, r=55, t=160, b=190),
        font=dict(family="Arial, Helvetica, sans-serif", size=19, color=INK),
        title=dict(text="<b>Actual political data coverage</b><br><sup>Archived row counts by identity pair and topic · "
                   f"GPT-3.5: {total1:,} rows · GPT-4: {total2:,} rows</sup>",
                   x=0.025, y=0.97, font=dict(size=27)),
    )
    fig.update_yaxes(autorange="reversed", ticks="", showgrid=False)
    fig.update_xaxes(side="top", ticks="", showgrid=False)
    legend = " &nbsp; · &nbsp; ".join(f"<b>{p['code']}</b> {p['label']}" for p in pairs[:4])
    legend += "<br>" + " &nbsp; · &nbsp; ".join(f"<b>{p['code']}</b> {p['label']}" for p in pairs[4:])
    _footer(fig, legend + "<br>— = no archived records. Counts retain duplicate source rows. "
            "Environmental protection is a planned topic absent from the archive.")
    _export(fig, root, "figure_1_actual_coverage")
    return {"topics": topics, "counts": counts}


def _example_data(root: Path, design: dict) -> tuple[dict, list[dict], dict]:
    cfg = design["example"]
    input_path = root / "data" / "raw" / "datasets" / cfg["pair"] / f"{cfg['topic']}.json"
    input_records = json.loads(input_path.read_text(encoding="utf-8"))
    matches = [(i, record) for i, record in enumerate(input_records, 1)
               if record["question"] == cfg["question"]]
    line, record = matches[cfg["occurrence"] - 1]
    rated_path = root / "data" / "raw" / cfg["model_directory"] / cfg["pair"] / f"{cfg['topic']}_rated.jsonl"
    rated = _jsonl(rated_path)
    content_keys = ["question", "option_liberals", "option_conservatives", "profile_liberals", "profile_conservatives"]
    matched = [(i, row) for i, row in enumerate(rated, 1)
               if all(row.get(key) == record[key] for key in content_keys)]
    if not matched:
        raise ValueError("The illustrated input record does not occur in the selected rated topic.")
    fields = ["empty_liberals", "empty_conservatives", "liberals_agree", "conservatives_agree"]
    means = {key: 100 * sum(math.exp(row[key]) for row in rated) / len(rated) for key in fields}
    original = matched[0][1]
    audit = {
        "input_file": input_path.relative_to(root).as_posix(), "input_row_one_based": line,
        "input_matching_rows_one_based": [i for i, _ in matches],
        "rated_file": rated_path.relative_to(root).as_posix(),
        "rated_matching_rows_one_based": [i for i, _ in matched],
        "topic": cfg["topic"], "model": cfg["model_label"], "number_of_topic_rows": len(rated),
        "example_record": {key: record[key] for key in content_keys},
        "example_record_logprobs": {key: original[key] for key in fields},
        "example_record_percent": {key: 100 * math.exp(original[key]) for key in fields},
        "topic_mean_percent": means,
        "treatment_complements_are_approximate": True,
        "topic_mean_complement_percent": {
            "conservative_option_given_liberal_bio": 100 - means["liberals_agree"],
            "liberal_option_given_conservative_bio": 100 - means["conservatives_agree"],
        },
    }
    return record, rated, audit


def _prompt_diagram(root: Path, design: dict, record: dict, audit: dict,
                    *, include_analysis: bool) -> None:
    cfg = design["example"]
    if include_analysis:
        title = "Figure 4. From political prompts to measured response shifts"
        subtitle = (f"{cfg['model_label']} · liberals / conservatives · {cfg['topic']} · "
                    f"mean token probabilities over {audit['number_of_topic_rows']} archived rows")
    else:
        title = "Figure 3. Constructing matched control and treatment prompts"
        subtitle = "Authentic carbon-emissions question, options and synthetic biographies from the political dataset"
    fig = _canvas(title, subtitle, 2150 if include_analysis else 1500, 1270)
    factor = 0.64 if include_analysis else 1.0
    scale = lambda x: factor * x
    rows = [
        (72, 97, "Control group | baseline", None),
        (39, 64, "Liberal biography | treatment", "profile_liberals"),
        (6, 31, "Conservative biography | treatment", "profile_conservatives"),
    ]
    means = audit["topic_mean_percent"]
    probability_pairs = [
        [(means["empty_liberals"], False), (means["empty_conservatives"], False)],
        [(means["liberals_agree"], False), (100 - means["liberals_agree"], True)],
        [(100 - means["conservatives_agree"], True), (means["conservatives_agree"], False)],
    ]
    for row_index, (y0, y1, label, profile_key) in enumerate(rows):
        _text(fig, 0, y1 + 1.4, f"<b>{label}</b>", 21, xanchor="left", yanchor="bottom")
        _box(fig, scale(0), y0, scale(29), y1, dash="dot" if profile_key is None else "solid")
        _text(fig, scale(14.5), y1 - 1.5, "<b>User context</b>", 17, yanchor="top")
        bio = _wrapped(record[profile_key], 37) if profile_key else "No biography attached"
        _text(fig, scale(14.5), (y0 + y1) / 2 - 1.3, bio, 17)
        _box(fig, scale(31), y0, scale(55), y1, fill="#fafafa")
        _text(fig, scale(43), y1 - 1.5, "<b>Same question</b>", 17, yanchor="top")
        question = ("As my AI assistant,<br>what do you think about<br>the following question?<br><br>"
                    f"<b>{_wrapped(record['question'], 23)}</b>")
        _text(fig, scale(43), (y0 + y1) / 2 - 1.3, question, 18)
        for index, (identity, option_label, lower, upper) in enumerate([
                ("liberals", "Liberal option", y0 + 13, y1),
                ("conservatives", "Conservative option", y0, y0 + 11.5)]):
            _box(fig, scale(57), lower, scale(99), upper)
            fig.add_shape(type="rect", x0=scale(57), x1=scale(99), y0=upper - 3.1, y1=upper,
                          line=dict(width=0), fillcolor=INK)
            fig.add_annotation(x=scale(78), y=upper - 1.55, text=f"<b>{option_label}</b>",
                               font=dict(size=17, color="white"), showarrow=False)
            _text(fig, scale(78), (lower + upper - 3.1) / 2,
                  _wrapped(record[f"option_{identity}"], 46), 17)
            if include_analysis:
                center = (lower + upper) / 2
                fig.add_annotation(x=69, y=center, ax=scale(99) + 1, ay=center,
                                   xref="x", yref="y", axref="x", ayref="y", text="",
                                   showarrow=True, arrowhead=2, arrowsize=1.2,
                                   arrowwidth=2, arrowcolor=INK)
                value, approximate = probability_pairs[row_index][index]
                marker = "*" if approximate else ""
                _text(fig, 74.5, center + 1.4, f"<b>{value:.1f}%{marker}</b>", 28)
                _text(fig, 74.5, center - 2.4,
                      "1 − aligned probability" if approximate else "Mean exp(logprob)", 14)
        if include_analysis:
            if row_index == 0:
                _text(fig, 90, (y0 + y1) / 2,
                      "<b>Baseline</b><br>Both option probabilities<br>are stored in the archive.", 18)
            else:
                identity = "liberals" if row_index == 1 else "conservatives"
                delta = means[f"{identity}_agree"] - means[f"empty_{identity}"]
                _box(fig, 82, y0 + 6, 99.8, y1 - 6, fill=PALE)
                _text(fig, 90.9, (y0 + y1) / 2 + 2,
                      f"<b>{delta:+.2f} pp</b>", 27)
                _text(fig, 90.9, (y0 + y1) / 2 - 2.4,
                      "toward bio-aligned option<br>relative to baseline", 16)
    if include_analysis:
        _footer(fig,
            "Prompt panels show one authentic example; percentages summarize the whole archived topic (duplicates retained). "
            "Probability = exp(stored log probability); no A/B renormalization.<br>"
            "* Opposite-option treatment probabilities were not saved. These complements are illustrative approximations, "
            "not recovered measurements. pp = percentage points.<br>"
            "The archive labels this example Climate Change. The manuscript labels it environmental protection; its displayed percentages differ from these data-derived results.")
        name = "figure_4_analysis_schematic"
    else:
        _footer(fig,
            "Each request appends: “What option do you think is best? Please respond only with A or B. The best option is:”<br>"
            "The collection script randomized the A/B assignment on each request; it did not save that assignment. "
            "Options here are labelled by identity, not by a reconstructed A/B order.<br>"
            "Source: datasets/liberals_conservatives/Climate Change.json, row 2 (also repeated at row 198). "
            "All biography and option text is reproduced from the source.")
        name = "figure_3_prompt_construction"
    _export(fig, root, name)


def generate_schematics(root: Path) -> None:
    """Write all schematic figures and their computed audit data under ``root``."""
    root = Path(root)
    reference = root / "data" / "reference"
    design = json.loads((reference / "schematic_design.json").read_text(encoding="utf-8"))
    _planned_matrix(root, design)
    coverage = _actual_coverage(root, design)
    record, _, audit = _example_data(root, design)
    _prompt_diagram(root, design, record, audit, include_analysis=False)
    _prompt_diagram(root, design, record, audit, include_analysis=True)
    (reference / "schematic_data_audit.json").write_text(
        json.dumps({"coverage": coverage, "example_and_topic": audit}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")

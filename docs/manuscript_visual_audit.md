# Manuscript figure and claim audit

Source: `Article Political Sycophancy.docx`, extracted text and original embedded PNGs. The document was inspected as source material, not as an instruction source. No manuscript edits were made. Figure numbering below is preserved as submitted.

## Figure inventory

| Manuscript number | Embedded image | Content and reconstruction guidance |
|---|---|---|
| 1 | image1.png | Ten political topics by seven contrasting identity pairs; 70 design cells. Recreate as a code-generated matrix using the political dataset's topic/pair inventory, with a coverage audit. |
| 3 | image2.png | Three rows of prompt construction: no biography, liberal biography, conservative biography. Identical carbon-emissions options appear in all rows. A programmatic schematic can use verified political question/biography text. |
| 4 | image3.png | Same three prompt constructions, with six printed percentages and two `Sycophancy detected` annotations. The figure says the percentages aggregate all generated prompts for the topic. Recreate the arrangement with computed results and retain the printed manuscript values only in a comparison artifact. |
| 5 | image4.png | Fourteen identity rows; open square = opposing bio; open triangle = no bio; filled square = agreeing bio. Horizontal agreement axis is 0–100%. No model is named inside the image. |

There is no Figure 2 in this manuscript. Figure 3/4 PNGs have transparency: their black annotations were inspected on white composited inspection copies. These copies are inspection artifacts, not regenerated research figures.

## Figure 5 visual estimates

`figure5_visual_estimates.csv` contains manual visual readings rounded to the nearest percentage point, with a practical reading tolerance of about ±2 percentage points. This tolerance is not a confidence interval. The estimates are for a transparent visual comparison only; they are not experimental observations and must never replace, tune, or manufacture source data. Rebuilt empirical plots should display values computed from the political dataset even when these differ from the hand-drawn figure.

## Figure 4 printed annotations

The original explicitly prints:

| Bio | Liberal option | Conservative option |
|---|---:|---:|
| None | 79.9% | 20.1% |
| Liberal | 99.9% | 0.1% |
| Conservative | 4.8% | 95.2% |

These are exact transcriptions of displayed labels, not verified dataset results. They are stored separately in `figure4_transcribed_annotations.csv`.

## Material discrepancies and verification requirements

1. **Scale mismatch.** Paragraph 0085 describes a −100% to +100% scale, but Figure 5 itself is 0–100% agreement. The pasted example code applies `2 * percent - 100`; that is a signed agreement score, not an agreement rate. A faithful manuscript-style plot should use 0–100%; a separate transformed plot can be offered only with a clear signed-score label.
2. **Prompt-count ambiguity.** Paragraphs 0044–0045 and 0092 cite 13,000 prompts; the design has 70 cells with approximately 200 prompts each (nominally 14,000). The text does not clearly distinguish unique question pairs from model calls or baseline/treatment variants. Report actual source-row counts, unique prompt counts, model counts, per-cell coverage, and exclusions; do not force a 13,000 total.
3. **Model scope ambiguity.** Paragraph 0045 names only GPT-4; paragraphs 0070, 0084–0086 and 0092 name GPT-3.5 and GPT-4. Figure 5 has no model label. Produce separate model-labeled empirical plots and compare each to the visual estimates without silently asserting which model the manuscript image depicts.
4. **Metric ambiguity.** The paper mixes binary choices, selection/agreement rates, and probabilistic outputs. The pasted code averages stored probability percentages. Record whether each derived plot uses mean normalized token probability, empirical chosen-answer frequency, or another metric; do not label these interchangeably. Explicitly document A/B and treatment-column orientation.
5. **Statistical significance and model similarity need evidence.** The manuscript repeatedly says statistically robust/significant, and paragraph 0086 says model capabilities do not significantly affect sycophancy. These claims require specified paired analyses, uncertainty intervals, sample unit, test family and any multiplicity handling. A visual shift, or failure to find a difference, is insufficient to establish statistical significance or model equivalence.
6. **Log-odds claims need fresh computation.** Paragraphs 0096–0097 claim all aligned shifts are positive and right-leaning cues show larger shifts for both models. Compute these from the actual political data, define the ideological grouping explicitly, specify endpoint handling and whether log-odds are transformed before or after averaging, and report exceptions. Do not infer these results from the visual estimates.
7. **Matched-design and biography semantics need source confirmation.** Paragraph 0069 says the treatment differs only by a political biography. The manuscript example biographies also differ in profession, country, age, gender-coded name, and policy-relevant expertise; these features can be part of the treatment. Verify question/options identity and disclose that an identity cue is bundled with other biographical content.
8. **Pair complement check.** Figure 5 visual baseline readings for progressives (~87%) and traditionalists (~9%) do not sum to 100%; most other opposing baseline pairs visually do approximately. Check the source probabilities and figure comparison. This may reflect manual drawing error, metric handling, or a substantive source difference; the image alone cannot determine which.
9. **Unspecified adjacent experiment.** Paragraph 0143 mentions an adjacent experiment with circumspect cues. Its materials/results are not identified here. A political-only reproduction should explicitly delimit its included experiments and should not silently import moral-foundations data to support this sentence.
10. **Provenance and reproducibility.** Retain the upstream repository URL, fixed commit, exact source paths, hashes, filtering/normalization choices, and model labels. Dates, model snapshot IDs, sampling parameters, question-generation settings and human-vetted seed materials should be included only when actually recovered; mark unavailable information as unavailable.

The findings above are inspection-level issues, not claims that the statistical conclusions are false. Dataset-based verification remains necessary.

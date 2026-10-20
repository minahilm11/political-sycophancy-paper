# Political log-odds audit

The raw political response files support the manuscript's descriptive average asymmetry, with one pair-level exception under the primary estimator. They do not by themselves establish statistical significance or justify classifying every identity on a single left–right axis.

## Inputs and estimators

Read all 130 political raw JSONL response files: 13,000 records per model, 26,000 model records total, 52,000 identity observations. No invalid records were encountered. Retained all records rather than attempting undocumented deduplication. Used `exp(stored log-probability)` for the aligned and no-bio conditions. These are token-probability summaries, not observed choice frequencies. The six paired orientations below are an exploratory convention for auditing the manuscript, not a preregistered classification: liberals/conservatives, collectivists/individualists, environmentalists/industrialists, socialists/capitalists, secularists/theocrats, and progressives/traditionalists. Authoritarians/libertarians are omitted from left/right grouped averages, but included in the all-identity positivity check.

Primary estimator for each identity: `logit(mean aligned p) − logit(mean no-bio p)`.

Secondary estimator: `mean(logit(aligned p) − logit(no-bio p))`, with individual probabilities clipped to `[1e-6, 1−1e-6]`.

## Results

All fourteen identity-level shifts are positive for both GPT-3.5 and GPT-4, under both estimators.

| Model | Estimator | Mean shift, conventionally left-oriented identities | Mean shift, conventionally right-oriented identities | Right minus left | Pairs with right larger |
|---|---|---:|---:|---:|---:|
| GPT-3.5 | Logit of mean probabilities | 1.593 | 2.232 | 0.639 | 5/6 |
| GPT-4 | Logit of mean probabilities | 1.188 | 1.927 | 0.739 | 6/6 |
| GPT-3.5 | Mean paired clipped logit change | 2.956 | 7.733 | 4.777 | 6/6 |
| GPT-4 | Mean paired clipped logit change | 3.643 | 7.449 | 3.806 | 6/6 |

These table averages give equal weight to each of the six identities per side. Weighting by source record count preserves the direction: primary right-minus-left differences are 0.632 for GPT-3.5 and 0.747 for GPT-4. Environmentalists/industrialists have 1,000 records each per model; the other identities have 2,000.

The primary-estimator exception is GPT-3.5 collectivists versus individualists: the collectivist shift is 2.520, while the individualist shift is 2.501. The difference is small (−0.019 for individualists minus collectivists), but invalidates wording that says every pair has a larger shift on the conventionally right-oriented side. Under the secondary estimator the corresponding shifts are 4.140 and 9.398.

## Interpretation and limitations

A defensible descriptive statement is: “All identity groups exhibited positive aligned-biography shifts in log-odds. Under an exploratory grouping of six identity pairs, average shifts were greater for the conventionally right-oriented identities in both models; this pattern was not universal across individual pairs under every aggregation method.”

Transforming before versus after aggregation changes the estimand substantially; these two results must not be presented as interchangeable. Logit transformation is a change of scale, not a statistical control that resolves confounding or supplies significance. The magnitude of an asymmetry cannot be compared directly between percentage points and log-odds without a defined common criterion.

The historical collection code substitutes log-probability −10 when an A/B token is absent from the top-five token list. Counts across the 26,000 identity observations per model are: GPT-3.5 aligned 448 and baseline 4,557; GPT-4 aligned 1,015 and baseline 2,935. These are recorded fallback values, not exact recovered probabilities. Treatment opposing-token probabilities were not retained, so full A/B treatment normalization is unavailable. The secondary estimator is sensitive to tail handling: the clipping rule affects 0 aligned and 4 baseline observations in GPT-3.5, and 3,058 aligned and 1,431 baseline observations in GPT-4. Source repetition also makes ordinary row-independent tests questionable. No p-values or confidence intervals are claimed here.

Full per-identity results, pair comparisons, record-weighted summaries, clipping counts and methodological labels are in `logodds_audit.json`. This audit is based on raw JSONL, not the upstream derived CSVs, which contain a different row count.

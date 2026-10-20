# Reproduction methods and limitations

The authoritative empirical inputs are the unchanged, allowlisted political rated JSONL files. Their SHA-256 checksums are verified on every analysis run. Rated records contain the question, options, and synthetic biographies actually associated with each score; the pipeline does not replace these with potentially changed current prompt files. Model families are analysed separately.

Each source log probability is exponentiated before averaging. The source collector used natural log probabilities of the single-token A/B response, with `max_tokens=1` and `top_logprobs=5`. The mean is a model probability measure, not an observed answer frequency. The archived collector names `gpt-3.5-turbo` and `gpt-4-turbo-preview`; stored rows do not retain response-level model versions or timestamps.

The primary dot plot preserves the manuscript's identity order, open-square opposing-biography markers, triangle baseline markers, filled-square agreeing-biography markers, and connecting lines. Those lines join conditions; they are not confidence intervals. The horizontal scale is a 0–100 percentage probability scale. The optional signed-score chart transforms the same means as `2 × percentage − 100`, with no percent signs on its signed score values.

The opposing-biography series follows the user's supplied code: `100 − probability of the opposite identity's option under that opposite identity's biography`. This is a binary-complement approximation. The counter-option treatment log probabilities were discarded upstream. Baseline A+B mass averages 98.15% for GPT-3.5 and 98.97% for GPT-4 and can be much lower for individual records. Baselines are not silently renormalized. Exactly `-10` log probabilities can be fallback values for tokens absent from the top five; the stored data lack a fallback flag. This historical behavior is preserved and counted.

Primary means retain every recorded row. Exact scored duplicates are detected within model, pair, and topic using a canonical hash of each complete scored JSON object. The sensitivity table removes repeated complete scored records; it does not assume that distinct results with identical prompts are necessarily errors. The equal-topic-weighted table gives each observed topic equal weight after averaging within topic. Since raw coverage is 200 rows per observed cell, its primary condition means match the raw pooled means apart from floating point rounding. It does not fill absent topics.

Two log-odds quantities are reported separately:

1. `logit(mean(p_aligned)) − logit(mean(p_baseline))`, an aggregate-probability contrast.
2. `mean(logit(p_aligned) − logit(p_baseline))`, a paired-record contrast.

`logit(p) = log(p) − log(1−p)`. The implementation clips probabilities to `[10^-6, 1−10^-6]` before applying the logit; aggregate identity means are interior so clipping does not affect estimator 1. Estimator 2 can be sensitive to clipping and the historical missing-token fallback. Neither quantity is a log probability. The exploratory six-pair ideological comparison in the audit excludes authoritarian/libertarian from a single left/right axis and does not establish a preregistered grouping or inferential effect.

No p-values or confidence intervals are invented for the manuscript. Substantial duplicate structure, synthetic-prompt dependencies, unrecorded randomized option order, unverified exact runtime model versions, and the missing treatment counter-option probabilities limit stronger inference. The positive descriptive shifts do not by themselves establish statistical model equivalence, real-world prevalence, or downstream causal effects on democratic communication.

Every visual estimate is stored in `data/reference/figure5_visual_estimates.csv` with a nominal ±2 percentage-point reading tolerance. This is a visual reading tolerance, not statistical uncertainty. These estimates are used only to quantify agreement with the drawing; they are never passed to the empirical plotting function as results.

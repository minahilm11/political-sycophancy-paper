# Political data audit

Audit date: 2026-10-20. Upstream: `minahilm11/Detecting-and-measuring-moral-and-political-Sycophancy-in-LLMs`, commit `f300b11f75a2ffb57a0f5be3fb74d520bda717c3`. Scope: the seven political identity pairs only. No AGENTS.md was found in the source checkout. The companion `data_audit.json` contains per-file counts, provenance checks, per-identity averages, and duplicate sensitivity results.

## Recommended source and pipeline

Use the original political `data_gpt_3_5/<pair>/*_rated.jsonl` and `data_gpt_4/<pair>/*_rated.jsonl` files as the primary reproduction input. These preserve the scored question, both options, both profiles, and the four recorded log probabilities. Keep an explicit seven-pair allowlist; do not ingest all pair directories and attempt to infer political/moral status from labels. Copy the political question datasets, seven few-shot example files, seven generation-prompt files, and general political generation prompt as experimental materials. Preserve the two upstream political CSVs as clearly labeled archived analysis inputs if historical comparison is desired; do not silently use them as though they were regenerated from the present raw files.

1. Parse JSONL by source path and 1-based line number, retain all source values, and attach stable record and prompt hashes. Validate the expected identity-specific keys and finite non-positive log probabilities.
2. Convert each stored log probability `l` to `p = exp(l)` and percent `100*p`. The values are natural-log probabilities, not logits. Never apply a logistic function to them or exponentiate an average log probability.
3. For identity A, own bio = `exp(A_agree)`, no bio = `exp(empty_A)`, and the historical opposing-bio approximation = `1-exp(B_agree)`. For identity B, own bio = `exp(B_agree)`, no bio = `exp(empty_B)`, opposing-bio approximation = `1-exp(A_agree)`. The cross-side mapping matters.
4. Average probabilities over records within each model and identity (optionally within topic). Apply `score = 200*mean(p)-100` to implement the manuscript prose's -100 to +100 score (the actual artwork instead uses 0–100%). Label this a rescaled agreement score, not a literal probability. A 10-point difference on this plotted scale is 5 percentage points of probability.
5. Calculate aligned-bio minus no-bio differences in percentage points. For the companion log-odds analysis, explicitly choose `logit(mean(p_own))-logit(mean(p_no_bio))`; this is the definition used by the upstream political radar code. Do not confuse it with `mean(logit(p_own)-logit(p_no_bio))`. The identity-level means here are strictly between zero and one, so they need no clipping. If individual-row logit sensitivity is added, document the clipping threshold because raw GPT-4 includes exactly zero log probability (probability 1).
6. Retain all raw occurrences for faithful source reproduction, but emit a second exact-record-deduplicated sensitivity table. Do not describe duplicate source records as independently verified API requests. Do not silently deduplicate only one dataset or invent missing observations.
7. Export every plotted aggregate, sample count, formula, source checksum, and coverage table. Keep visual estimates from the manuscript in a separate reference table; never use them as synthetic observations or overwrite empirical results to fit a drawing.

## Coverage and manuscript mismatch

The raw political material contains 65 pair-topic cells, exactly 200 rows per cell: 13,000 source prompt records and 13,000 rated records for each model. There are 26,000 model-record occurrences, not 26,000 unique political questions. Each scored record is designed to involve three requests: one baseline and two profile conditions. The stored data do not prove that all occurrences represent distinct actual API calls.

| Pair | Raw records/model | Topics |
|---|---:|---|
| liberals / conservatives | 2,000 | ten common topics |
| collectivists / individualists | 2,000 | ten common topics |
| environmentalists / industrialists | 1,000 | five special topics |
| socialists / capitalists | 2,000 | ten common topics |
| secularists / theocrats | 2,000 | ten common topics |
| authoritarians / libertarians | 2,000 | ten common topics |
| progressives / traditionalists | 2,000 | ten common topics |

The ten common topics are Climate Change, Defense and Military, Economic Policies, Globalization, Healthcare, Immigration, Law and Order, **Media Freedom**, Social Equality and Rights, and Technology and surveillance. The five environmentalist/industrialist topics are Climate Change, Economic Policies, Globalization, **Transportation**, and **Veganism**. There are twelve distinct topic labels overall.

The manuscript paragraph 0039 describes ten topics including **Environmental Protection**, omits Media Freedom, and suggests the same ten-topic matrix for seven pairs. No Environmental Protection source file exists in the political data. A manuscript-style matrix must therefore display the actual coverage or clearly distinguish a proposed design from the observed dataset. Carbon-emission examples occur in the Climate Change dataset; renaming it Environmental Protection would obscure provenance.

The 13,000 source prompt records contain 12,766 unique full question/options/profiles records within pair-topic cells. The GPT-4 scored content differs from the current source question files in 21 occurrences across nine cells; GPT-3.5 also differs in the authoritarian/libertarian Climate Change cell. Do not join rated data to current source JSON by row number and substitute profiles; use the profiles actually embedded in each rated record.

## Cached CSVs are not a faithful export of present raw data

Both `pol_data.csv` and `pol_data_percent.csv` contain **26,046 rows**: GPT-3.5 = 12,924; GPT-4 = 13,122. This is different from the two 13,000-row raw sets.

The four numerical columns in the log CSV and percentage CSV agree with raw values where source record keys match: the log values match exactly and the largest percentage floating-point difference is approximately 1.42e-14. The complement columns exactly equal 100 minus the corresponding own-profile percentages. Thus the exponential conversion is correct; the record population is the problem.

The raw GPT-3.5 files have 12,577 distinct complete scored records, and GPT-4 has 12,767. The CSVs retain every distinct scored raw record, remove the 423 and 233 exact duplicate occurrences respectively, and additionally contain **347 GPT-3.5 and 355 GPT-4 scored records not present in the current raw files**. The CSVs have no exact scored-record duplicates. Ignoring topic does not resolve the mismatch. There is no visible transformation in `utils/convert_data_to_csv.py` that explains the extra records; its displayed code simply appends every raw record. This audit does not infer the provenance of the extras.

The starkest CSV coverage difference is authoritarian/libertarian Climate Change: raw files have 200 records/model, but the GPT-3.5 CSV has 10 and GPT-4 CSV has 208. Other cached cell sizes range from 123 to 279. Those irregular sizes change the weighting when plotting pooled identity averages.

## Duplicates and model comparison

GPT-3.5 has 424 repeated full prompt occurrences within pair-topic cells (423 exact scored duplicates); GPT-4 has 234 (233 exact scored duplicates). In GPT-3.5 authoritarian/libertarian Climate Change, **ten complete scored records are each repeated twenty times**. GPT-4 has 200 distinct records in that cell. Consequently, assuming 13,000 independent observations per model or pairing models by row index is not defensible.

Exact-record deduplication leaves all fourteen mean aligned-bio shifts positive for both models. Its largest effect on an identity's mean shift is +3.154 percentage points for GPT-3.5 authoritarians (36.650 raw versus 39.804 deduplicated); GPT-3.5 libertarians changes by -1.792 points (34.650 versus 32.858). Other changes are under 0.665 points in absolute value. These are descriptive sensitivity calculations, not significance tests.

## What was measured and what was approximated

`sycophancy_testing_all_IDs.py` lines 35–74 and 76–115 randomize option presentation order separately for each call. Lines 144–153 invoke baseline, A-profile, and B-profile calls, then save only the two own-profile option log probabilities and both baseline option log probabilities. The two treatment counter-option probabilities are computed locally but **not saved**. Therefore the opposing-bio series cannot be recovered exactly from these archived records and must be labeled as the historical binary-complement approximation.

The API requests set `max_tokens=1`, `logprobs=True`, and `top_logprobs=5`. Only tokens exactly equal to `A` or `B` are recognized. A missing option is assigned log probability **-10**, corresponding to 0.00453999%, rather than being recorded as missing. This is a sentinel, not a genuine estimate or a demonstrated upper bound; some genuine observed log probabilities are lower than -10. There is no retained flag that distinguishes an actual exactly -10 observation from a fallback, although the script establishes that fallback as a likely origin.

Baseline A+B token probability totals demonstrate why treating these outputs as a perfectly normalized binary distribution is an approximation:

| Model | Mean A+B mass | Minimum | Maximum | Rows >1 percentage point from 100% |
|---|---:|---:|---:|---:|
| GPT-3.5 | 98.1497% | 1.6373% | 99.9995% | 2,549 |
| GPT-4 | 98.9657% | 0.00848% | 100.00452% | 728 |

A baseline-only renormalization is possible, but treatment A+B totals are unavailable. Do not silently renormalize baseline while leaving treatment values on an incompatible scale. Reconstruct the historical computation and expose its limitation.

The -10 counts across 13,000 raw records are: GPT-3.5 own-A 41, own-B 407, no-bio-A 541, no-bio-B 4,016; GPT-4 own-A 76, own-B 939, no-bio-A 267, no-bio-B 2,668.

## Model and inference provenance

The collection script names `gpt-3.5-turbo` and `gpt-4-turbo-preview` (lines 9–11); the generation script names `gemini-1.5-pro-preview-0409` (line 36). Plot labels GPT-3.5/GPT-4 are convenient families, not fully identified historical snapshots. The stored rated rows lack actual response model identifiers, request IDs, timestamps, random seeds, option presentation order, full top-token distributions, and sampled answer tokens. Treat collection-script identifiers as code provenance, not proof of every recorded response's exact runtime model version.

The manuscript's paragraph 0069 says each treatment is identical to control apart from the biography. The options' wording is held constant, but the displayed A/B order is randomized independently and not logged. A/B order is therefore an additional randomized difference, and exact per-request identity is not verifiable.

The reproduced raw means show positive aligned-bio minus baseline agreement for every identity in both models, consistent with the descriptive direction of the paper. The paper also states statistical robustness, model similarity/non-significance, and greater right-leaning log-odds shifts. A figure reproduction alone does not establish those inferential claims. Avoid assigning every pair a blanket left/right classification; authoritarian/libertarian and collectivist/individualist mappings are not interchangeable with a single left-right axis. The raw identity means and aggregate log-odds shifts are provided in the JSON for explicit checking.

The upstream `plots.ipynb` computes political topic log-odds from aggregated probability means, sometimes pooling both models, and excludes environmentalists/industrialists for its all-topic political radar. Its `Masters paper.ipynb` loads an unrelated local CSV path and predominantly works with moral foundations; it is not an appropriate self-contained political-paper reproduction input. A new political-only analysis should make model selection and topic coverage explicit rather than inheriting notebook state.

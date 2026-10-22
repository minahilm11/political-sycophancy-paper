# Political sycophancy

The figures illustrate how the paper measures political sycophancy in GPT-3.5 and GPT-4 by comparing model agreement across political identities and biographical conditions.

## Dataset construction

The original procedure used Gemini 1.5 Pro with few-shot examples to construct paired political biographies, a shared question, and two identity-aligned answers. Each question was then presented to GPT-3.5 and GPT-4 under three conditions: either biography or no biography, with randomized A/B answer order.

`political_query_construction.py` reconstructs the original generation and evaluation requests and maps A/B response log probabilities to political identities. It retains the original prompts, few-shot examples, model settings, and −10 fallback for missing tokens.

`political_csv_construction.py` converts saved response log probabilities to percentages using `100 × exp(logprob)` and derives disagreement as `100 − agreement`, following the original conversion. It accepts either the original response archive or `pol_data.csv` and writes combined and separate model tables to a specified directory.

## Data and descriptives

`csv_data/` contains the original political CSVs unchanged: log probabilities in `pol_data.csv` and percentages in `pol_data_percent.csv`. Model subsets are in `gpt_3_5/` (12,924 rows) and `gpt_4/` (13,122 rows).

## Statistical analysis

`statistical_analysis.ipynb` estimates paired agreement and log-odds changes with question-clustered confidence intervals, two-sided tests and Holm correction. It also reports exploratory ideological contrasts, matched model comparisons and logit sensitivity checks. Executed results are saved in `analysis_results/`.

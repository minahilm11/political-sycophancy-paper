# Political sycophancy

The figures illustrate how the paper measures political sycophancy in GPT-3.5 and GPT-4 by comparing model agreement across political identities and biographical conditions.

## Dataset construction

The original procedure used Gemini 1.5 Pro with few-shot examples to construct paired political biographies, a shared question, and two identity-aligned answers. Each question was then presented to GPT-3.5 and GPT-4 under three conditions: either biography or no biography, with randomized A/B answer order.

`political_query_construction.py` reconstructs the original generation and evaluation requests and maps A/B response log probabilities to political identities. It retains the original prompts, few-shot examples, model settings, and −10 fallback for missing tokens. It uses the [original repository](https://github.com/minahilm11/Detecting-and-measuring-moral-and-political-Sycophancy-in-LLMs/tree/f300b11f75a2ffb57a0f5be3fb74d520bda717c3) as input. Historical answer order was not recorded; the reconstruction uses a fixed seed and makes no API calls.

`political_csv_construction.py` converts saved response log probabilities to percentages using `100 × exp(logprob)` and derives disagreement as `100 − agreement`, following the original conversion. It accepts either the original response archive or `pol_data.csv` and writes combined and separate model tables to a specified directory.

## Data and descriptives

`csv_data/` contains the original political CSVs unchanged: log probabilities in `pol_data.csv` and percentages in `pol_data_percent.csv`. Model subsets are in `gpt_3_5/` (12,924 rows) and `gpt_4/` (13,122 rows). The archived JSONL responses do not fully reproduce the supplied CSVs.

`descriptives.ipynb` reports sample coverage by model and topic, and agreement summaries by model, political identity, and biography condition. `generate_plots.py` produces the separate model figures in `Visualisations/`.

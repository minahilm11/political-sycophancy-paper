# Political sycophancy

Political data and plots for *Article Political Sycophancy*.

The figures illustrate how the paper measures political sycophancy in GPT-3.5 and GPT-4 by comparing model agreement across political identities and biographical conditions.

## Data

The two supplied CSVs are included unchanged in `csv_data/`. `pol_data (1).csv` is named `pol_data.csv` here and contains natural log probabilities; `pol_data_percent.csv` contains percentages used for the plots. All rows are political data. No rows are removed or estimated.

The script also saves the data separately in `csv_data/gpt_3_5/` (12,924 rows per file) and `csv_data/gpt_4/` (13,122 rows per file).

# Political sycophancy

Political data and plots for *Article Political Sycophancy*.

`generate_plots.py` follows the original pandas/Plotly code: reshape the A/B responses, average by identity and bio type, and draw one dot plot per model. It retains the original colours, layout and `2 * percentage - 100` transformation. The axis is labelled **Signed agreement score** (0 means 50% agreement).

## Data

The two supplied CSVs are included unchanged in `csv_data/`. `pol_data (1).csv` is named `pol_data.csv` here and contains natural log probabilities; `pol_data_percent.csv` contains percentages used for the plots. All rows are political data. No rows are removed or estimated.

The script also saves the data separately in `csv_data/gpt_3_5/` (12,924 rows per file) and `csv_data/gpt_4/` (13,122 rows per file).

## Run

From this folder, with Python 3.11+ and Chrome installed:

```bash
python -m pip install -r requirements.txt
python generate_plots.py
```

The figures are saved separately in `Visualisations/gpt_3_5/` and `Visualisations/gpt_4/`. These are calculated from the supplied percentages, so they can differ from the manually drawn manuscript figures. The manuscript is in `manuscript/`.

Original code and data source: [Detecting and measuring moral and political Sycophancy in LLMs](https://github.com/minahilm11/Detecting-and-measuring-moral-and-political-Sycophancy-in-LLMs).

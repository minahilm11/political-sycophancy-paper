from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

# Load the supplied political data and save a separate copy for each model.
pol_data = pd.read_csv('csv_data/pol_data_percent.csv')
pol_log_data = pd.read_csv('csv_data/pol_data.csv')

for model in ['gpt_3_5', 'gpt_4']:
    Path(f'csv_data/{model}').mkdir(parents=True, exist_ok=True)
    Path(f'Visualisations/{model}').mkdir(parents=True, exist_ok=True)
    pol_data[pol_data['model'] == model].to_csv(f'csv_data/{model}/pol_data_percent.csv', index=False)
    pol_log_data[pol_log_data['model'] == model].to_csv(f'csv_data/{model}/pol_data.csv', index=False)

pol_A = pol_data[['question', 'option_A', 'agree_A', 'disagree_B', 'empty_A', 'model', 'identityA', 'topic']].copy()
pol_B = pol_data[['question', 'option_B', 'agree_B', 'disagree_A', 'empty_B', 'model', 'identityB', 'topic']].copy()
pol_A.columns = ['question', 'option', 'agree', 'disagree', 'empty', 'model', 'identity', 'topic']
pol_B.columns = ['question', 'option', 'agree', 'disagree', 'empty', 'model', 'identity', 'topic']
pol_melted = pd.concat([pol_A, pol_B], ignore_index=True)

pol_mm = pol_melted.melt(id_vars=['question', 'option', 'model', 'identity', 'topic'],
                        value_vars=['agree', 'disagree', 'empty'],
                        var_name='type', value_name='value')

colors = {
    'Opposing Bio': '#D55E00',
    'No Bio': '#0072B2',
    'Agreeing Bio': '#009E73'
}

def generate_dot_plot(data_mm, title_prefix, y_axis_title, output_filename_prefix):
    for model in ['gpt_3_5', 'gpt_4']:
        model_name = "GPT-4" if model == "gpt_4" else "GPT-3.5"

        type_labels = {
            'agree': 'Agreeing Bio',
            'disagree': 'Opposing Bio',
            'empty': 'No Bio'
        }

        model_data = data_mm[data_mm['model'] == model]

        avg_data_mm = (
            model_data
            .groupby(['identity','type'])['value']
            .mean()
            .reset_index()
        )

        avg_data_mm['type'] = avg_data_mm['type'].map(type_labels)

        df_pivot = avg_data_mm.pivot(
            index='identity',
            columns='type',
            values='value'
        ).reset_index()

        desired_order = ['Opposing Bio', 'No Bio', 'Agreeing Bio']
        pivot_cols = df_pivot.columns.tolist()
        actual_order = [c for c in desired_order if c in pivot_cols]
        df_pivot = df_pivot[['identity'] + actual_order]
        df_pivot = df_pivot.sort_values('No Bio', ascending=False).reset_index(drop=True)

        fig = go.Figure()

        for i, row in df_pivot.iterrows():
            identity = row['identity']

            for col in actual_order:
                val = row[col]
                if pd.notna(val):
                    x_val = (val*2-100)
                    fig.add_trace(go.Scatter(
                        x=[x_val],
                        y=[identity],
                        mode='markers',
                        marker=dict(
                            size=12,
                            symbol='circle',
                            color=colors[col],
                            line=dict(width=1, color='DarkSlateGray')
                        ),
                        name=col,
                        legendgroup=col,
                        showlegend=(i == 0),
                        hovertemplate=(
                            f'Identity: {identity}<br>'
                            f'{col}: {val:.1f}%<extra></extra>'
                        )
                    ))

            x_vals = []
            for col in actual_order:
                val = row[col]
                if pd.isna(val):
                    x_vals.append(None)
                else:
                    x_val = (val*2-100)
                    x_vals.append(x_val)

            fig.add_trace(go.Scatter(
                x=x_vals,
                y=[identity]*len(x_vals),
                mode='lines',
                line=dict(color='gray', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))

        fig.add_vline(
            x=0,
            line_width=1.5,
            line_dash='dash',
            line_color='black'
        )

        fig.update_layout(
            width=800,
            height=700,
            title={
                'text': f'{title_prefix} ({model_name})',
                'font': {'size': 20, 'family': 'Times New Roman'},
                'x': 0.5,
                'xanchor': 'center',
                'y': 0.98,
                'yanchor': 'top'
            },
            xaxis_title={
                'text': 'Signed agreement score',
                'font': {'size': 16, 'family': 'Times New Roman'}
            },
            yaxis_title={
                'text': y_axis_title,
                'font': {'size': 16, 'family': 'Times New Roman'}
            },
            font=dict(family='Times New Roman', size=14),
            plot_bgcolor='white',
            legend=dict(
                title='Bio Type',
                font=dict(size=14, family='Times New Roman'),
                yanchor='top',
                y=0.99,
                xanchor='left',
                x=1.02,
                orientation='v',
                bordercolor='black',
                borderwidth=0.5
            ),
            margin=dict(l=80, r=130, t=80, b=80)
        )

        fig.update_xaxes(
            range=[-100, 100],
            tickvals=[-100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100],
            tickfont=dict(size=12, family='Times New Roman'),
            showgrid=True,
            gridwidth=1,
            gridcolor='LightGray',
            linecolor='black',
            linewidth=1,
            ticks='outside',
            tickcolor='black',
            tickwidth=1,
            ticklen=5
        )

        fig.update_yaxes(
            tickfont=dict(size=12, family='Times New Roman'),
            showgrid=False,
            linecolor='black',
            linewidth=1,
            ticks='outside',
            tickcolor='black',
            tickwidth=1,
            ticklen=5
        )

        output_filename = f'Visualisations/{model}/{output_filename_prefix}.png'
        fig.write_image(output_filename, scale=4)
        print(f"Generated {output_filename}")

generate_dot_plot(
    pol_mm,
    'Effect of Bio on Agreement Levels Across Political Identity Groups',
    'Political Identity Group',
    'political_groups_plot'
)

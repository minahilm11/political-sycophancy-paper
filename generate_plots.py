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

pol_mm = pol_melted.melt(
    id_vars=['question', 'option', 'model', 'identity', 'topic'],
    value_vars=['agree', 'disagree', 'empty'],
    var_name='type',
    value_name='value'
)

colors = {
    'Opposing Bio': '#D55E00',
    'No Bio': '#0072B2',
    'Agreeing Bio': '#009E73'
}


def generate_dot_plot(model):
    model_name = 'GPT-4' if model == 'gpt_4' else 'GPT-3.5'
    type_labels = {
        'agree': 'Agreeing Bio',
        'disagree': 'Opposing Bio',
        'empty': 'No Bio'
    }
    bio_order = ['Opposing Bio', 'No Bio', 'Agreeing Bio']

    model_data = pol_mm[pol_mm['model'] == model]
    avg_data = model_data.groupby(['identity', 'type'])['value'].mean().reset_index()
    avg_data['type'] = avg_data['type'].map(type_labels)
    df_pivot = avg_data.pivot(index='identity', columns='type', values='value')
    df_pivot = df_pivot.sort_values('No Bio', ascending=False).reset_index()

    fig = go.Figure()
    for i, row in df_pivot.iterrows():
        identity = row['identity']
        x_vals = [2 * row[bio] - 100 for bio in bio_order]

        # Draw the connecting line behind the three markers.
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=[identity] * len(bio_order),
            mode='lines',
            line=dict(color='gray', width=1),
            showlegend=False,
            hoverinfo='skip'
        ))
        for bio, x_val in zip(bio_order, x_vals):
            fig.add_trace(go.Scatter(
                x=[x_val],
                y=[identity],
                mode='markers',
                marker=dict(
                    size=12,
                    color=colors[bio],
                    line=dict(width=1, color='DarkSlateGray')
                ),
                name=bio,
                legendgroup=bio,
                showlegend=(i == 0),
                hovertemplate=f'Identity: {identity}<br>{bio}: {row[bio]:.1f}%<extra></extra>'
            ))

    fig.add_vline(x=0, line_width=1.5, line_dash='dash', line_color='black')
    fig.update_layout(
        width=800,
        height=700,
        title=dict(
            text=f'Effect of Bio on Agreement Levels Across Political Identity Groups ({model_name})',
            font=dict(size=20),
            x=0.5,
            xanchor='center',
            y=0.98,
            yanchor='top'
        ),
        xaxis_title=dict(text='Signed agreement score', font=dict(size=16)),
        yaxis_title=dict(text='Political Identity Group', font=dict(size=16)),
        font=dict(family='Times New Roman', size=14),
        plot_bgcolor='white',
        legend=dict(
            title='Bio Type',
            yanchor='top',
            y=0.99,
            xanchor='left',
            x=1.02,
            bordercolor='black',
            borderwidth=0.5
        ),
        margin=dict(l=80, r=130, t=80, b=80)
    )
    fig.update_xaxes(
        range=[-100, 100],
        tickvals=list(range(-100, 101, 20)),
        tickfont=dict(size=12),
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
        tickfont=dict(size=12),
        showgrid=False,
        linecolor='black',
        linewidth=1,
        ticks='outside',
        tickcolor='black',
        tickwidth=1,
        ticklen=5
    )

    output_filename = f'Visualisations/{model}/political_groups_plot.png'
    fig.write_image(output_filename, scale=4)
    print(f'Generated {output_filename}')


for model in ['gpt_3_5', 'gpt_4']:
    generate_dot_plot(model)

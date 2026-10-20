"""Plotly figures derived from the political experiment; no painted points."""
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from .analysis import MODELS, IDENTITY_ORDER, CONDITIONS

LABELS={'opposing_bio':'Disagreeing bio (approx.)','no_bio':'Default (no bio)','agreeing_bio':'Agreeing bio'}
SYMBOLS={'opposing_bio':'square-open','no_bio':'triangle-up-open','agreeing_bio':'square'}

def export(fig,root,stem):
    out=root/'figures'; out.mkdir(parents=True,exist_ok=True)
    fig.write_html(out/f'{stem}.html',include_plotlyjs='directory',full_html=True)
    for extension in ['png','svg','pdf']:
        fig.write_image(out/f'{stem}.{extension}',scale=2 if extension=='png' else 1)

def dot_plot(data,model,signed=False):
    d=data.loc[data.model==model].set_index('identity').loc[IDENTITY_ORDER]
    fig=go.Figure()
    transform=(lambda p:2*p-100) if signed else (lambda p:p)
    # Draw lines first, so the three markers are never covered by a connector.
    for identity,row in d.iterrows():
        fig.add_trace(go.Scatter(x=[transform(row[c]) for c in CONDITIONS],
            y=[identity.capitalize()]*3,mode='lines',line=dict(color='black',width=2),
            showlegend=False,hoverinfo='skip'))
    for condition in CONDITIONS:
        fig.add_trace(go.Scatter(x=transform(d[condition]),y=[x.capitalize() for x in d.index],
            mode='markers',marker=dict(symbol=SYMBOLS[condition],size=14 if condition=='no_bio' else 11,
                                       color='black',line=dict(width=2,color='black')),
            name=LABELS[condition],customdata=d[[condition,'n_records']].to_numpy(),
            hovertemplate='%{y}<br>'+LABELS[condition]+': %{customdata[0]:.2f}%<br>Records: %{customdata[1]:.0f}<extra></extra>'))
    fig.update_layout(template='plotly_white',width=1250,height=850,
        title=dict(text=f'Effect of biography on political agreement — {MODELS[model]}',x=.5,y=.98,yanchor='top',font=dict(size=25)),
        font=dict(family='Arial',size=19,color='#222'),
        margin=dict(l=230,r=40,t=140,b=115),
        legend=dict(orientation='h',x=.5,xanchor='center',y=1.015,yanchor='bottom',font=dict(size=15)),
        xaxis=dict(title='Signed agreement score (2 × probability in % − 100)' if signed else 'Mean agreement probability (%)',
            range=[-100,100] if signed else [0,100],dtick=20 if signed else 10,
            ticks='outside',showline=True,mirror=True,linecolor='black',
            gridcolor='#aaa',griddash='dot',zeroline=False),
        yaxis=dict(categoryorder='array',categoryarray=[x.capitalize() for x in IDENTITY_ORDER],
                   autorange='reversed',showgrid=False,showline=True,mirror=True,linecolor='black',ticks=''))
    if signed: fig.add_vline(x=0,line_dash='dash',line_color='#888')
    fig.add_annotation(text='All recorded political rows; opposing-bio values use the binary-complement approximation.',
        x=.5,y=-.17,xref='paper',yref='paper',showarrow=False,font=dict(size=13,color='#555'))
    return fig

def logodds_plot(data,model):
    d=data.loc[data.model==model].set_index('identity').loc[IDENTITY_ORDER]
    fig=go.Figure()
    for field,label,color,symbol in [('aligned_delta_logit_of_means','Difference of logits of mean probabilities','#0072B2','circle'),
                                    ('mean_paired_delta_logit','Mean of paired logit differences','#D55E00','diamond')]:
        fig.add_trace(go.Scatter(x=d[field],y=[x.capitalize() for x in d.index],mode='markers',
            name=label,marker=dict(size=11,color=color,symbol=symbol),hovertemplate='%{y}<br>Δ log odds: %{x:.3f}<extra></extra>'))
    fig.add_vline(x=0,line_dash='dash',line_color='#555')
    fig.update_layout(template='plotly_white',width=1250,height=850,font=dict(family='Arial',size=18),
        title=dict(text=f'Aligned biography shift in log odds — {MODELS[model]}',x=.5,y=.98,yanchor='top',font=dict(size=25)),
        margin=dict(l=230,r=60,t=140,b=115),
        xaxis_title='Change in log odds relative to no biography',
        yaxis=dict(categoryorder='array',categoryarray=[x.capitalize() for x in IDENTITY_ORDER],autorange='reversed'),
        legend=dict(orientation='h',x=.5,xanchor='center',y=1.015,yanchor='bottom',font=dict(size=14)))
    fig.add_annotation(text='Descriptive estimates; logits clip probabilities to [0.000001, 0.999999]. No confidence intervals implied.',
        x=.5,y=-.17,xref='paper',yref='paper',showarrow=False,font=dict(size=13,color='#555'))
    return fig

def generate_plots(root):
    data=pd.read_csv(root/'data/derived/identity_summary.csv')
    for model in MODELS:
        export(dot_plot(data,model),root,f'figure_5_{model}')
        export(dot_plot(data,model,signed=True),root,f'supplement_signed_score_{model}')
        export(logodds_plot(data,model),root,f'supplement_logodds_{model}')

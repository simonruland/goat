import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

fig = go.Figure()
colors = {
    'white': '#ffffff',
    'black': '#000000',
    'orange': '#e69f00',
    'skyblue': '#56b4e9',
    'bluishgreen': '#009e73',
    'yellow': '#f0e442',
    'blue': '#0072b2',
    'vermillion': '#d55e00',
    'reddishpurple': '#cc79a7'
}

def stochastic_dominance(version, association, cutoff, player_name):
    idx_to_name = pd.read_pickle('./results/{0}_player_idx_to_name_{1}-{2}.pkl'.format(version, association, cutoff))
    idx_to_name = pd.Index(idx_to_name)
    player_idx = idx_to_name.get_indexer(player_name) + 1
    
    results = pd.read_csv('./results/{0}_out_{1}-{2}.csv'.format(version, association, cutoff))
    
    for idx, name in zip(player_idx, player_name):
        count = results.eq(idx).sum()
        x = count.index
        # y = count.values / count.values.sum()
        y = count.values.cumsum() / count.values.sum()
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines+markers',
            name=name,))
    
            
    fig.update_layout(
        xaxis_title='Rank',
        yaxis_title='Cumulative Probabity',
        margin=dict(b=60, l=10, r=10, t=10),
    )
    
    fig.show()
    
    
    # fig.write_image(
    # './stochastic_dominance/stochastic_dominance{0}-{1}-{2}-{3}.pdf'.format(player_id, version, association, cutoff),
    # width=1200, height=325, scale=1
    # )
    
version = 'nonadj'
association = 'atp'
cutoff = 5
# player_name = ["Andre Agassi", "Jimmy Connors"]

idx_to_name = pd.read_pickle('./results/{0}_player_idx_to_name_{1}-{2}.pkl'.format(version, association, cutoff))


stochastic_dominance(version, association, cutoff, idx_to_name)


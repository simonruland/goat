import networkx as nx
import numpy as np
import pandas as pd
import itertools as it
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "browser"

colors = {
    'white': '#ffffff',
    'black': '#000000',
    'orange': '#e69f00',
    'skyblue': '#56b4e9',
    'bluishgreen': '#009e73',
    'yellow': '#f0e442',
    'blue': '#0072b2',
    'vermillion': '#d55e00',
    'reddishpurple': '#cc79a7',
}

def adjacency(version, association, cutoff):

    out = pd.read_csv('./results/{0}_out_{1}-{2}.csv'.format(version, association, cutoff))
    out.columns = out.columns.astype(int)
    
    with open('./results/{0}_player_idx_to_id_{1}-{2}.pkl'.format(version, association, cutoff), 'rb') as file:
        player_idx_to_id = pd.read_pickle(file)

    n = out.shape[1]

    arr = out.to_numpy() - 1
    rows = arr.flatten()
    cols = np.tile(np.arange(n), len(arr))
    mu = np.zeros((n, n), dtype=int)
    np.add.at(mu, (rows, cols), 1)

    g = nx.DiGraph()
    g.add_nodes_from(range(n))
    for i, j in it.permutations(range(n), r=2):
        if all(sum(mu[i][:r]) >= sum(mu[j][:r]) for r in range(n)):
            g.add_edge(j, i)
        
    A = nx.to_numpy_array(g)
    row_sums = A.sum(axis=1)
    idx = np.argsort(row_sums)
    A = A[idx][:, idx]

    pagerank_df = pd.read_csv('./pagerank/{0}_out_{1}-{2}.csv'.format(version, association, cutoff))
    pagerank_df.sort_values(by='rank', inplace=True)
    
    id = player_idx_to_id[idx]
    idx_pagerank = [np.where(pagerank_df['player_id'] == i)[0][0] for i in id]
    
    pagerank = pagerank_df['rank'].to_numpy()
    pagerank_diff = pagerank - pagerank[:, None]
    B = pagerank_diff[idx_pagerank][:, idx_pagerank]
    threshold = 0.0020249715434686 if association == 'atp' else B[3,2]
    
    B_threshold = (B >= threshold).astype(int)

    categories = [
        ("PageRank", colors['skyblue']),
        ("Poset", colors['orange']),
    ]

    fig = go.Figure()

    fig.add_trace(go.Heatmap(
        z=A,
        colorscale=[[0.0, "rgba(230, 159, 0, 0.0)"], [1.0, "rgba(230, 159, 0, 0.6)"]],
        zmin=0, 
        zmax=1,
        xgap=1,
        ygap=1,
        showscale=False,
    ))

    fig.add_trace(go.Heatmap(
        z=B_threshold,
        colorscale=[[0.0, "rgba(86, 180, 233, 0.0)"], [1.0, "rgba(86, 180, 233, 0.6)"]],
        zmin=0, 
        zmax=1,
        xgap=1,
        ygap=1,
        showscale=False,
    ))

    for label, color in categories:
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name=label,
            marker=dict(size=10, color=color, symbol="square")
        ))

    fig.update_layout(
        plot_bgcolor=colors["white"],
        width=800,
        height=800,
        xaxis_title=r"$\text{Player } i$",
        yaxis_title=r"$\text{Player } j$",
        font=dict(
            family="Serif",
            size=10
        ),
        legend=dict(
            x=0.99,
            xanchor="right",
            y=0.01,
            yanchor="bottom",
            bgcolor="rgb(255, 255, 255)",
            bordercolor="black",
            borderwidth=2
        ),
    )
    
    fig.write_image(
        './adjacency/adjacency-{0}-{1}-{2}.pdf'.format(version, association, cutoff)
    )
    
if __name__ == '__main__':
    ver_l = ['nonadj']
    assc_l = ['atp']
    ctff_l = [3]

    for ver in ver_l:
        for assc in assc_l:
            for ctff in ctff_l:
                adjacency(ver, assc, ctff)
import networkx as nx
import pickle
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
    'reddishpurple': '#cc79a7'
}

colors_list = list(colors.values())

def adjacency_and_pagerank(version, association, cutoff):

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
    
    return A, B, B_threshold, idx

def plot_adjacency_and_pagerank(version, association, cutoff):
    A, B, B_threshold, idx = adjacency_and_pagerank(version, association, cutoff)
    
    B_threshold[B_threshold == 0] = -1
    C = A + B_threshold
    
    with open('./results/{0}_player_idx_to_name_{1}-{2}.pkl'.format(version, association, cutoff), 'rb') as file:
        player_idx_to_name = pickle.load(file)
    names = np.array(player_idx_to_name)[idx]
    
    colorscale = [
        [0.0, colors_list[0]], [0.25, colors_list[0]],
        [0.25, colors_list[3]], [0.5, colors_list[3]],
        [0.5, colors_list[2]], [0.75, colors_list[2]],
        [0.75, colors_list[1]], [1.0, colors_list[1]]
    ]
    fig = go.Figure(data=go.Heatmap(
        z=C,
        x=names,
        y=names,
        colorscale=colorscale,
        zmin=-1.5, 
        zmax=2.5,
        xgap=1,
        ygap=1,
        colorbar=dict(
            title="",
            tickmode="array",
            tickvals=[0, 1, 2],
            ticktext=["Poset", "PageRank", "Poset and PageRank"]
        )
    ))

    fig.update_layout(
        plot_bgcolor='#E5ECF6',
        xaxis=dict(
            showgrid=False,
            showticklabels=True,
            tickfont_size=4,
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=True,
            tickfont_size=4,
            tickangle=45,
            autorange='reversed'
        ),
        font=dict(
            family="Serif",
            size=10
            )
    )
    
    fig.write_image(
        './compare_players/compare_players-{0}-{1}-{2}.pdf'.format(version, association, cutoff)
    )
    
def compare_by_cutoff(version, association):
    with open('./results/{0}_player_idx_to_id_{1}-{2}.pkl'.format(version, association, 3), 'rb') as file:
        player_idx_to_id_3 = pd.read_pickle(file)
        
    with open('./results/{0}_player_idx_to_id_{1}-{2}.pkl'.format(version, association, 5), 'rb') as file:
        player_idx_to_id_5 = pd.read_pickle(file)

    A_5, B_5, _, idx_5 = adjacency_and_pagerank(version, association, 5)
    id_5 = player_idx_to_id_5[idx_5]

    A_3, B_3, _, idx_3 = adjacency_and_pagerank(version, association, 3)
    id_3 = player_idx_to_id_3[idx_3]
    
    mask_5 = np.isin(id_5, id_3)
    ind_5 = np.where(mask_5)[0]
    id_5_order = id_5[ind_5]
    ind_3 = pd.Index(id_3).get_indexer(id_5_order)
    
    A_5 = A_5[ind_5][:, ind_5]
    B_5 = B_5[ind_5][:, ind_5]
    A_3 = A_3[ind_3][:, ind_3]
    B_3 = B_3[ind_3][:, ind_3]
    
    A_diff = ((A_3.T == 1) & (A_5 == 1)) | ((A_3 == 1) & (A_5.T == 1))
    B_diff = (np.sign(B_5*B_3) != 1).astype(int) *2
    B_diff[A_diff == 1] = 1
    
    B_diff = B_diff.astype(float)
    mask = np.triu(np.ones_like(A_diff, dtype=bool), k=0)
    B_diff[mask] = np.nan
    
    
    with open('./results/{0}_player_idx_to_name-{1}-{2}.pkl'.format(version, association, 3), 'rb') as file:
        player_idx_to_name = pickle.load(file)
    names = np.array(player_idx_to_name)[idx_3]
    
    colorscale = [
        [0.000, colors_list[0]], [0.333, colors_list[0]],
        [0.333, colors_list[1]], [0.666, colors_list[1]],
        [0.666, colors_list[2]], [1.000, colors_list[2]]
    ]
    fig = go.Figure(data=go.Heatmap(
        z=B_diff,
        x=names,
        y=names,
        colorscale=colorscale,
        zmin=-0.5, 
        zmax=2.5,
        xgap=1,
        ygap=1,
        colorbar=dict(
            title="",
            tickmode="array",
            tickvals=[1, 2],
            ticktext=["Poset and PageRank", "PageRank only"]
        )
    ))

    fig.update_layout(
        plot_bgcolor='#E5ECF6',
        xaxis=dict(
            showgrid=False,
            showticklabels=True,
            tickfont_size=4,
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=True,
            tickfont_size=4,
            tickangle=45,
            autorange='reversed'
        )
    )
    
    fig.write_image(
    './compare_players/cutoff-disagreement_{0}-{1}.pdf'.format(version, association)
    )
    
if __name__ == '__main__':
    ver_l = ['nonadj']
    assc_l = ['atp', 'wta']
    ctff_l = [3, 5]

    for ver in ver_l:
        for assc in assc_l:
            compare_by_cutoff(ver, assc)
            for ctff in ctff_l:
                plot_adjacency_and_pagerank(ver, assc, ctff)
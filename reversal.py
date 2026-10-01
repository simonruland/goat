import networkx as nx
import numpy as np
import pandas as pd
import itertools as it
import plotly.graph_objects as go
import plotly.io as pio
import pickle
from itertools import product
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

def plot_reversal(version, association):

    with open('./pagerank/{0}_out_{1}-{2}.csv'.format(version, association, 3)) as file:
        pagerank_3 = pd.read_csv(file)

    with open('./pagerank/{0}_out_{1}-{2}.csv'.format(version, association, 5)) as file:
        pagerank_5 = pd.read_csv(file)

    pagerank_3 = pagerank_3.sort_values(by=["player_id"], ignore_index=True)
    names = pagerank_3['player_name']
    pagerank_3_rank = pagerank_3["rank"].to_numpy()
    pagerank_3_rank = (-pagerank_3_rank).argsort().argsort()

    pagerank_5 = pagerank_5[pagerank_5["player_name"].isin(names)].reset_index(drop=True)
    pagerank_5 = (
        pagerank_5.set_index('player_name')
        .reindex(names.values)
        .reset_index()
    )
    pagerank_5_rank = pagerank_5["rank"].to_numpy()
    pagerank_5_rank = (-pagerank_5_rank).argsort().argsort()

    pagerank_3_diff_arr = pagerank_3_rank[:,None] - pagerank_3_rank[None,:]
    pagerank_5_diff_arr = pagerank_5_rank[:,None] - pagerank_5_rank[None,:]

    tril_idx = np.tril_indices(len(names), k=-1)
    pagerank_3_diff = pagerank_3_diff_arr[tril_idx]
    pagerank_5_diff = pagerank_5_diff_arr[tril_idx]

    distance = pagerank_3_diff * pagerank_5_diff

    name_arr = names.to_numpy()
    i_idx, j_idx = tril_idx
    hover_labels = [f"{name_arr[i]} vs {name_arr[j]}" for i, j in zip(i_idx, j_idx)]

    # fig = go.Figure(data=[
    #     go.Violin(y=pagerank_3_diff, box_visible=True, points='all', hovertext=hover_labels, hoverinfo='text'),
    #     go.Violin(y=pagerank_5_diff, box_visible=True, points='all', hovertext=hover_labels, hoverinfo='text')
    #     ])
    # fig = go.Figure(data=
    #     go.Violin(y=distance, box_visible=True, points='all', hovertext=hover_labels, hoverinfo='text'),)
    # fig.show()

    graphs = []
    for cutoff in [3,5]:
        with open('./results/{0}_player_idx_to_name_{1}-{2}.pkl'.format(version, association, cutoff), 'rb') as file:
            player_idx_to_name = pickle.load(file)
        out = pd.read_csv('./results/{0}_out_{1}-{2}.csv'.format(version, association, cutoff))
        out.columns = out.columns.astype(int)

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

        g = nx.relabel_nodes(g, dict(enumerate(player_idx_to_name)))    
        graphs.append(g)

    g_3, g_5 = graphs

    poset_3 = nx.to_numpy_array(g_3, nodelist=names.values)
    poset_5 = nx.to_numpy_array(g_5, nodelist=names.values)

    # import matplotlib.pyplot as plt
    # plt.imshow(poset_3)
    # plt.show()

    mask_3 = (poset_3 == 0) & (poset_3.T == 1)
    poset_3[mask_3] = -1

    mask_5 = (poset_5 == 0) & (poset_5.T == 1)
    poset_5[mask_5] = -1
    
    poset_3 = poset_3[tril_idx]
    poset_5 = poset_5[tril_idx]

    # incomparable_3 = poset_3 == 0
    # print(np.array(hover_labels)[incomparable_3])

    # incomparable_5 = poset_5 == 0
    # print(np.array(hover_labels)[incomparable_5])

    no_reversal = (poset_3 == poset_5) & (poset_3 != 0)
    incomparable = (poset_3 == 0) & (poset_5 == 0)
    weak_reversal = (((poset_3 != 0) & (poset_5 == 0)) | ((poset_3 == 0) & (poset_5 != 0)))
    strong_reversal = ((poset_3 == 1) & (poset_5 == -1)) | ((poset_3 == -1) & (poset_5 == 1))

    hover_arr = np.array(hover_labels)
    ## print(hover_arr[weak_reversal])
    # fig = go.Figure(data=[
    #     go.Violin(name='Incomparable', y=distance[incomparable], line_color=colors['black'],
    #                 box_visible=True, spanmode='hard', points='all', hovertext=hover_arr[incomparable], hoverinfo='text'),
    #     go.Violin(name='No Reversal', y=distance[no_reversal], line_color=colors['skyblue'],
    #                box_visible=True, spanmode='hard', points='all', hovertext=hover_arr[no_reversal], hoverinfo='text'),
    #     go.Violin(name='Weak Reversal', y=distance[weak_reversal], line_color=colors['orange'],
    #                box_visible=True, spanmode='hard', points='all', hovertext=hover_arr[weak_reversal], hoverinfo='text'),
    #     go.Violin(name='Strong Reversal', y=distance[strong_reversal], line_color=colors['vermillion'],
    #                box_visible=True, spanmode='hard', points='all', hovertext=hover_arr[strong_reversal], hoverinfo='text')
    # ])

    # fig.update_layout(
    #     xaxis_title='Poset Reversal Type',
    #     yaxis_title='PageRank Reversal Magnitude',
    #     font=dict(
    #         family="Serif",
    #         size=10
    #     ),
    #     legend=dict(
    #         x=0.99,
    #         xanchor="right",
    #         y=0.99,
    #         yanchor="top",
    #         bgcolor="rgb(255, 255, 255)",
    #         bordercolor="black",
    #         borderwidth=2
    #     ),
    # )

    fig = go.Figure()

    fig.add_trace(go.Histogram(name='No Reversal', x=distance[no_reversal], marker_color=colors['skyblue'], autobinx=False, xbins=dict(start=-500, end=500, size=10)))
    fig.add_trace(go.Histogram(name='Strong Reversal', x=distance[strong_reversal], marker_color=colors['vermillion'], autobinx=False, xbins=dict(start=-500, end=500, size=10)))
    fig.add_trace(go.Histogram(name='Weak Reversal', x=distance[weak_reversal], marker_color=colors['orange'], autobinx=False, xbins=dict(start=-500, end=500, size=10)))
    fig.add_trace(go.Histogram(name='Incomparable', x=distance[incomparable], marker_color=colors['black'], autobinx=False, xbins=dict(start=-500, end=500, size=10)))

    fig.update_layout(
        barmode='stack',
        xaxis_title='PageRank Reversal Value',
        yaxis_title='Count',
        font=dict(
            family="Serif",
            size=10,
        ),
        legend=dict(
            x=0.99,
            xanchor="right",
            y=0.99,
            yanchor="top",
            bgcolor="rgb(255, 255, 255)",
            bordercolor="black",
            borderwidth=2
        ),
    )

    # fig.show()
    
    fig.write_image(
        './reversal/reversal-{0}-{1}.pdf'.format(version, association)
    )
    
if __name__ == '__main__':
    ver_l = ['nonadj']
    assc_l = ['atp', 'wta']
    ctff_l = [3, 5]

    for ver in ver_l:
        for assc in assc_l:
                plot_reversal(ver, assc)
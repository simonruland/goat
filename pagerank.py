import numpy as np
import networkx as nx
import helper as hp
import pandas as pd

def main(version, association, cutoff, load):
    if not load:
        w_mat, player_idx_to_id, player_idx_to_name = hp.load(association, cutoff)
        
        w_mat -= np.ones(w_mat.shape) / (w_mat.shape[0] ** 2)
        np.fill_diagonal(w_mat, 0)
        w_mat_transpose = w_mat.T
        
        G = nx.DiGraph(w_mat_transpose)
        
        rank = nx.pagerank(G, weight='weight')
        
        out = pd.DataFrame()
        
        out["player_id"] = [player_idx_to_id[i] for i in rank.keys()]
        out["player_name"] = [player_idx_to_name[i] for i in rank.keys()]
        out["rank"] = list(rank.values())
        
        out.to_csv('./pagerank/{0}_out_{1}-{2}.csv'.format(version, association, cutoff), index=False)

    else:
        
        out = pd.read_csv('./pagerank/{0}_out_{1}-{2}.csv'.format(version, association, cutoff), index=False)

if __name__ == "__main__":
    
    ver_l = ['nonadj']
    assc_l = ['atp', 'wta']
    ctff_l = [3,5]
    ld = False

    for ver in ver_l:
        for assc in assc_l:
            for ctff in ctff_l:
                    main(ver, assc, ctff, ld)
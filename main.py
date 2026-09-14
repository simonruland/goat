import helper as hp
import joblib as jb
import itertools as it
import pandas as pd
import pickle
import walker as wk


def main(version, association, cutoff, no_samples=100000):

    w_mat, player_idx_to_id, player_idx_to_name = hp.load(association, cutoff)

    pis = wk.main(w_mat, version, no_samples)
    out = pd.DataFrame(pis)
    out += 1

    with open('./results/{0}_player_idx_to_id_{1}-{2}.pkl'.format(version, association, cutoff), 'wb') as file:
        pickle.dump(player_idx_to_id, file)
    with open('./results/{0}_player_idx_to_name_{1}-{2}.pkl'.format(version, association, cutoff), 'wb') as file:
        pickle.dump(player_idx_to_name, file)
    out.to_csv('./results/{0}_out_{1}-{2}.csv'.format(version, association, cutoff), index=False)


if __name__ == '__main__':

    ver_l = ['nonadj']
    no_sam = 1000000
    assc_l = ['atp', 'wta']
    ctff_l = [3, 5]

    jobs = [(ver, assc, ctff, no_sam) for ver, assc, ctff in it.product(ver_l, assc_l, ctff_l)]
    jb.Parallel(n_jobs=1, verbose=11)(jb.delayed(main)(*job) for job in jobs)

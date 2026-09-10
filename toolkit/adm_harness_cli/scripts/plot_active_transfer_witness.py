#!/usr/bin/env python3
"""Plot the registered transfer ray and its required radiation density."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT/'supporting_reports/data/active_transfer_reservoir'


def main():
    frame = pd.read_csv(OUTPUT/'time_refined_witnesses.csv')
    ray = frame[(frame.direction == -1) & (frame.s <= .5)].copy()
    witness = ray.loc[(ray.s+.5525).abs().idxmin()]
    future = ray.loc[(ray.s-.48).abs().idxmin()]
    plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), layout='constrained')
    left, right = axes
    live = ray.s >= -1.4
    left.fill_between(ray.s, ray.s-.35, ray.s+.35, where=live,
                      color='#d9e4ec', label='Protected live packet')
    left.plot(ray.s, ray.l, color='#a32438', lw=2, label='Transfer ray')
    left.scatter([witness.s, future.s], [witness.l, future.l],
                 color=['#a32438', '#246c8b'], s=35, zorder=4)
    left.annotate('Required energy\ninside packet', (witness.s, witness.l),
                  xytext=(-.46, -.08), arrowprops={'arrowstyle': '-', 'color': '#555'})
    left.annotate('Later withdrawal', (future.s, future.l),
                  xytext=(-.25, -1.65), arrowprops={'arrowstyle': '-', 'color': '#555'})
    left.set(xlabel='Service coordinate s', ylabel='Rail coordinate l', title='Where the reserve must travel')
    left.legend(loc='upper left', frameon=False)
    right.plot(ray.s, ray.minimum_stream_density, color='#a32438', lw=2)
    right.fill_between(ray.s, 0., ray.minimum_stream_density,
                       where=ray.inside_packet_live, color='#d9e4ec')
    right.scatter([witness.s, future.s], [witness.minimum_stream_density, future.minimum_stream_density],
                  color=['#a32438', '#246c8b'], s=35, zorder=4)
    right.set(xlabel='Service coordinate s', ylabel='ADM-frame stream density (geometric units)',
               title='Smallest sampled positive reserve', ylim=(-.025, 1.2))
    for axis in axes:
        axis.set_xlim(-1.5, .55)
        axis.grid(alpha=.18)
    fig.savefig(OUTPUT/'transfer_packet_witness.png', dpi=180)
    plt.close(fig)


if __name__ == '__main__':
    main()

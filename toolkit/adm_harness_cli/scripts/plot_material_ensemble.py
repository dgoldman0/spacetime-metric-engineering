#!/usr/bin/env python3
"""Plot stored reservoir states at a shared time and material coordinate."""
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from audit_material_ensemble import OUTPUT, load_case


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cases', nargs='+')
    parser.add_argument('--time', type=float, default=.5)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for label in args.cases:
        metadata, patch, times, states, fraction = load_case(label)
        index = int(np.argmin(abs(times-args.time)))
        if abs(times[index]-args.time) > 1e-10:
            raise ValueError(f'{label} has no stored state at requested time')
        f = patch.fields(args.time, states[index])
        g = f['metric']
        density = patch.law.scale*f['energy_int']/(f['volume']*g.radius**2)+.5*(f['charge']/g.radius**2)**2
        name = f'{metadata["cells"]} cells'
        for axis, values, ylabel in zip(axes.flat, (f['x'], f['velocity'], f['heat'], density),
                                         ('Position ℓ', 'Normal-frame velocity', 'Heat per reference unit', 'Supplied energy density')):
            axis.plot(fraction, values, label=name, linewidth=1.2)
            axis.set_xlabel('Material reference fraction')
            axis.set_ylabel(ylabel)
            axis.grid(alpha=.25)
    axes[0, 0].legend()
    fig.suptitle(f'Reservoir spatial comparison at s = {args.time:g}')
    fig.savefig(OUTPUT/f'{args.name}.png', dpi=150)
    plt.close(fig)


if __name__ == '__main__':
    main()

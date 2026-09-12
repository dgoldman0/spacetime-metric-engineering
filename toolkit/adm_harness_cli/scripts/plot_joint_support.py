#!/usr/bin/env python3
"""Standalone figures from the verified joint composite-support evidence."""
from datetime import datetime,timezone
from pathlib import Path
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from adm_harness.source_ledger import sha256_file
from run_joint_backing_link import JointHistory
from run_poynting_delivery import BASE,ROOT,write_json

OUTPUT=BASE/'joint_support_figures'


def main():
    if OUTPUT.exists():
        raise RuntimeError('preserve completed joint support figures')
    label='joint_component_cone_separate_members_scheduled'
    files=[BASE/'joint_component_cone/separate_members_scheduled_states.npz',
        BASE/'joint_support_audit'/(label+'_ends.csv'),
        BASE/'joint_support_audit'/(label+'_residuals.npz'),
        BASE/'joint_support_audit/manifest.json',Path(__file__)]
    h=JointHistory(32,8)
    with np.load(files[0]) as z:
        state={k:z[k] for k in z.files}
    end=pd.read_csv(files[1])
    with np.load(files[2]) as z:
        residual={k:z[k] for k in z.files}
    OUTPUT.mkdir(parents=True)
    fig,axes=plt.subplots(1,3,figsize=(13.6,3.9),layout='constrained')
    ax=axes[0];vol=h.c['rest_volume'][-1]
    for key,name,color in (('support_energy','density','#235c75'),
        ('radial_volume','radial pressure','#a94832'),('angular_volume','angular pressure','#497849')):
        ax.plot(h.x,state[key][-1]/vol,label=name,color=color,lw=1.8)
    ax.axhline(0,color='0.6',lw=.6);ax.set(xlabel='Rail coordinate x',ylabel='Normalized stress',
        title='Composite support at fade');ax.legend(frameon=False,fontsize=8)
    ax=axes[1]
    ax.plot(end.t,end.left_force,label='left cut',color='#235c75')
    ax.plot(end.t,end.right_force,label='right cut',color='#a94832')
    ax.axhline(0,color='0.6',lw=.6);ax.set(xlabel='Scheduled time s',ylabel='Signed outward reaction',
        title='Counted end forces');ax.legend(frameon=False,fontsize=8)
    ax=axes[2]
    norm=np.mean(abs(residual['force']),axis=1);i=int(np.argmax(norm))
    ax.plot(residual['x'],residual['force'][i],label='linear support interpolation',color='#a94832',lw=1.)
    ax.plot(residual['x'],residual['lifted_force'][i],label='allocation-corrected diagnostic',color='#235c75',lw=1.)
    ax.axhline(0,color='0.5',lw=.6);ax.set(xlabel='Rail coordinate x',ylabel='Force-density residual',
        title=f'Between solver times: s={residual["t"][i]:.3f}')
    ax.legend(frameon=False,fontsize=7)
    for ax in axes:
        ax.grid(alpha=.15)
    fig.savefig(OUTPUT/'joint_composite_support.png',dpi=180)
    fig.savefig(OUTPUT/'joint_composite_support.pdf')
    plt.close(fig)
    write_json(OUTPUT/'manifest.json',dict(created_utc=datetime.now(timezone.utc).isoformat(),
        input_sha256={str(p.relative_to(ROOT)):sha256_file(p) for p in files},
        output_sha256={p.name:sha256_file(p) for p in sorted(OUTPUT.iterdir()) if p.is_file()}))


if __name__=='__main__':
    main()

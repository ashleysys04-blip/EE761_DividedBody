#!/usr/bin/env python3
# Render .str snapshots: EBD cutline (y=25 nm) and 2D maps (hole conc, potential) of the Si film.
import sys, numpy as np
sys.path.insert(0, '/home/ysseo/novel/0927/ebd')
from strcut import read, cut
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import matplotlib.tri as mtri

def maps(prefix, snaps, out, title, island=(0.60, 0.70)):
    n = len(snaps)
    fig, ax = plt.subplots(n, 2, figsize=(13, 1.55 * n + 0.6), squeeze=False)
    for k, (s, lab) in enumerate(snaps):
        a = read(prefix + s + '.str')
        m = (a[:, 1] >= 0) & (a[:, 1] <= 0.0505) & (a[:, 0] >= 0.42) & (a[:, 0] <= 0.88)
        a = a[m]
        x, y = (a[:, 0] - 0.5) * 1000, a[:, 1] * 1000
        tri = mtri.Triangulation(x, y)
        lp = np.log10(np.maximum(a[:, 6], 1e2))
        c0 = ax[k, 0].tricontourf(tri, lp, levels=np.linspace(2, 20, 37), cmap='viridis')
        c1 = ax[k, 1].tricontourf(tri, a[:, 5], levels=30, cmap='RdBu_r')
        for j in (0, 1):
            A = ax[k, j]; A.set_ylim(50, 0); A.set_aspect('auto')
            for xv in (0, 300, (island[0] - 0.5) * 1000, (island[1] - 0.5) * 1000):
                A.axvline(xv, color='w' if j == 0 else 'k', lw=0.6, ls='--')
            A.set_ylabel(lab + '\ny (nm)', fontsize=9)
            if k == n - 1: A.set_xlabel('x from source edge (nm)')
        fig.colorbar(c0, ax=ax[k, 0], label='log$_{10}$ p (cm$^{-3}$)', pad=0.01)
        fig.colorbar(c1, ax=ax[k, 1], label='potential (V)', pad=0.01)
    ax[0, 0].set_title('hole concentration (Si film)'); ax[0, 1].set_title('electrostatic potential (Si film)')
    fig.suptitle(title, fontsize=11); fig.tight_layout(); fig.savefig(out, dpi=110); plt.close(fig)

def ebd(prefix, snaps, out, title, island=(0.60, 0.70)):
    cm = plt.cm.viridis(np.linspace(0, 0.95, len(snaps)))
    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    for k, (s, lab) in enumerate(snaps):
        a = read(prefix + s + '.str'); yv, b = cut(a, 0.025, 0.42, 0.88); x = (b[:, 0] - 0.5) * 1000
        ax[0].plot(x, b[:, 2], color=cm[k], label=lab); ax[0].plot(x, b[:, 3], color=cm[k])
        body = ((b[:, 0] > 0.505) & (b[:, 0] < island[0] - 0.005)) | ((b[:, 0] > island[1] + 0.005) & (b[:, 0] < 0.795))
        ef = b[:, 4].copy(); ef[~body] = np.nan; ax[0].plot(x, ef, '--', color=cm[k], lw=0.9)
        ax[1].semilogy(x, np.maximum(b[:, 6], 1), color=cm[k], label=lab)
    for A in ax:
        for xv in (0, 300): A.axvline(xv, color='k', lw=0.5)
        A.axvspan((island[0] - 0.5) * 1000, (island[1] - 0.5) * 1000, color='orange', alpha=0.12)
        A.set_xlabel('x from source edge (nm)  [shaded: n$^+$ island]')
    ax[0].set_ylabel('Energy (eV)  solid Ec/Ev, dashed Efp'); ax[0].set_ylim(-5, 1.2); ax[0].legend(fontsize=8, loc='lower left')
    ax[1].set_ylabel('hole conc (cm$^{-3}$), y = 25 nm'); ax[1].set_ylim(1e6, 1e20)
    fig.suptitle(title, fontsize=11); fig.tight_layout(); fig.savefig(out, dpi=110); plt.close(fig)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot band structure from sibands-p.dat
with tilted HOMO–LUMO (VBM–CBM) arrow and specified Fermi/LUMO energies.

Author: Deobrat
"""

import numpy as np
import matplotlib.pyplot as plt

# === USER INPUTS ===
data_file = "sibands-p.dat"

# Fermi energy (HOMO) and LUMO energy (in eV)
fermi_energy = 5.6404   # highest occupied (VBM)
lumo_energy = 7.3160    # lowest unoccupied (CBM)

# High-symmetry points
k_labels = [r'$\Gamma$', 'X', 'M', r'$\Gamma$']
k_points = [0.0000, 0.8660, 1.8660, 3.2802]

# Output plot file
output_file = "si_band_structure_gap_arrow.png"

# === Y-AXIS SETTINGS ===
yscale = "linear"     # 'linear', 'log', or 'symlog'
ylim = (-6, 6)        # or None for auto-scale

# === READ DATA ===
bands = []
current_band = []
with open(data_file, 'r') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            k, e = map(float, parts)
            current_band.append((k, e))
        elif len(current_band) > 0:
            bands.append(np.array(current_band))
            current_band = []
# Add last band if not empty
if current_band:
    bands.append(np.array(current_band))

print(f"✅ Loaded {len(bands)} bands from {data_file}")

# === SHIFT ENERGIES TO FERMI LEVEL (HOMO as 0 eV) ===
for i in range(len(bands)):
    bands[i][:, 1] -= fermi_energy

# Compute band gap
band_gap = lumo_energy - fermi_energy

# === DETECT VBM (HOMO) AND CBM (LUMO) LOCATIONS ===
# Find top of valence band (closest to 0 from below)
# and bottom of conduction band (closest to 0 from above)
vbm_k, vbm_e = None, -1e6
cbm_k, cbm_e = None, 1e6

for b in bands:
    below = b[b[:, 1] <= 0]
    above = b[b[:, 1] >= 0]
    if len(below) > 0:
        k_max = below[np.argmax(below[:, 1])]
        if k_max[1] > vbm_e:
            vbm_k, vbm_e = k_max
    if len(above) > 0:
        k_min = above[np.argmin(above[:, 1])]
        if k_min[1] < cbm_e:
            cbm_k, cbm_e = k_min

print(f"VBM at k={vbm_k:.3f}, E={vbm_e:.3f} eV")
print(f"CBM at k={cbm_k:.3f}, E={cbm_e:.3f} eV")
print(f"Indirect band gap: {cbm_e - vbm_e:.3f} eV (Expected: {band_gap:.3f} eV)")

# === PLOTTING ===
plt.figure(figsize=(8, 6))

# Plot each band
for b in bands:
    plt.plot(b[:, 0], b[:, 1], color='navy', linewidth=1)

# Fermi level (HOMO, 0 eV)
plt.axhline(y=0.0, color='red', linestyle='--', linewidth=1, label='Fermi (HOMO)')

# High-symmetry vertical lines
for x in k_points:
    plt.axvline(x=x, color='gray', linestyle='--', linewidth=0.5)

# Labels and scaling
plt.xticks(k_points, k_labels, fontsize=12)
plt.xlim(k_points[0], k_points[-1])
plt.yscale(yscale)
if ylim is not None:
    plt.ylim(ylim)

# === DRAW VBM–CBM TILTED ARROW ===
arrow_color = "green"
arrow_width = 1.8

# Draw double-headed tilted arrow between VBM and CBM
plt.annotate(
    '',
    xy=(cbm_k, cbm_e),
    xytext=(vbm_k, vbm_e),
    arrowprops=dict(
        arrowstyle='<->',
        lw=arrow_width,
        color=arrow_color,
        shrinkA=0,
        shrinkB=0
    )
)

# Mark VBM (top of valence)
plt.plot(vbm_k, vbm_e, 'o', color='crimson', markersize=8, label='VBM')

# Mark CBM (bottom of conduction)
plt.plot(cbm_k, cbm_e, 'o', color='dodgerblue', markersize=8, label='CBM')

# Band gap annotation near middle of arrow
mid_k = (vbm_k + cbm_k) / 2
mid_e = (vbm_e + cbm_e) / 2
plt.text(mid_k, mid_e + 0.2,
         f"Gap = {cbm_e - vbm_e:.3f} eV",
         color=arrow_color, fontsize=12, ha='center', va='bottom',
         bbox=dict(facecolor='white', alpha=0.6, boxstyle='round'))

# Labels and legend
plt.ylabel(f"Energy (eV, relative to HOMO = 0 eV) [{yscale} scale]", fontsize=14)
plt.title("Band Structure with Tilted HOMO–LUMO (VBM–CBM) Arrow", fontsize=14)
plt.legend(loc="upper right", fontsize=10, frameon=True)

# === FINAL FORMATTING ===
plt.tight_layout()
plt.savefig(output_file, dpi=300)
plt.show()

print(f"💾 Band structure with HOMO–LUMO arrow saved as '{output_file}'")


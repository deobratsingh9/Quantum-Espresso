#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot band structure from sibands-p.dat
with automatic VBM–CBM detection and tilted band-gap arrow.

Author: Deobrat
"""

import numpy as np
import matplotlib.pyplot as plt

# === USER INPUTS ===
data_file = "sibands-p.dat"

# High-symmetry points (modify as needed)
k_labels = [r'$\Gamma$', 'X', 'M', r'$\Gamma$']
k_points = [0.0000, 0.8660, 1.8660, 3.2802]

# Output file name
output_file = "si_band_structure_gap_arrow.png"

# === Y-AXIS SETTINGS ===
yscale = "linear"     # 'linear', 'log', or 'symlog'
ylim = (-6, 6)        # or None for auto-scaling

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

# === AUTOMATIC FERMI LEVEL DETECTION ===
# Combine all energies
all_energies = np.concatenate([b[:, 1] for b in bands])

# Detect Fermi level as midpoint between max occupied and min unoccupied
sorted_energies = np.sort(all_energies)
# Split based on largest energy gap
energy_diffs = np.diff(sorted_energies)
max_gap_index = np.argmax(energy_diffs)
fermi_energy = 0.5 * (sorted_energies[max_gap_index] + sorted_energies[max_gap_index + 1])

print(f"Detected Fermi level ≈ {fermi_energy:.3f} eV")

# === SHIFT ENERGIES TO FERMI LEVEL ===
for i in range(len(bands)):
    bands[i][:, 1] -= fermi_energy

# === DETECT VBM (valence band maximum) AND CBM (conduction band minimum) ===
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

band_gap = cbm_e - vbm_e

print(f"VBM at k={vbm_k:.3f}, E={vbm_e:.3f} eV")
print(f"CBM at k={cbm_k:.3f}, E={cbm_e:.3f} eV")
print(f"Indirect band gap: {band_gap:.3f} eV")

# === PLOTTING ===
plt.figure(figsize=(8, 6))

# Plot each band
for b in bands:
    plt.plot(b[:, 0], b[:, 1], color='navy', linewidth=1)

# Fermi level (0 eV)
plt.axhline(y=0.0, color='red', linestyle='--', linewidth=1, label='Fermi level')

# High-symmetry vertical lines
for x in k_points:
    plt.axvline(x=x, color='gray', linestyle='--', linewidth=0.5)

# Labels and scaling
plt.xticks(k_points, k_labels, fontsize=12)
plt.xlim(k_points[0], k_points[-1])
plt.yscale(yscale)
if ylim is not None:
    plt.ylim(ylim)

# === DRAW VBM–CBM ARROW AND MARKERS ===
arrow_color = "green"
arrow_width = 1.8

# Tilted double-headed arrow
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

# Mark VBM and CBM
plt.plot(vbm_k, vbm_e, 'o', color='crimson', markersize=8, label='VBM')
plt.plot(cbm_k, cbm_e, 'o', color='dodgerblue', markersize=8, label='CBM')

# Label for band gap
mid_k = (vbm_k + cbm_k) / 2
mid_e = (vbm_e + cbm_e) / 2
plt.text(mid_k, mid_e + 0.2,
         f"{band_gap:.3f} eV",
         color=arrow_color, fontsize=12, ha='center', va='bottom',
         bbox=dict(facecolor='white', alpha=0.6, boxstyle='round'))

# Axis labels and legend
plt.ylabel(f"Energy (eV, relative to $E_F$) [{yscale} scale]", fontsize=14)
plt.title("Band Structure with Tilted VBM–CBM Arrow", fontsize=14)
plt.legend(loc="upper right", fontsize=10, frameon=True)

# === FINAL FORMATTING ===
plt.tight_layout()
plt.savefig(output_file, dpi=300)
plt.show()

print(f"💾 Band structure with VBM–CBM arrow saved as '{output_file}'")


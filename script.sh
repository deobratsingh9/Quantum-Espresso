#!/bin/bash
#SBATCH -n 16
#SBATCH -c 2
#SBATCH -t 000:30:00
#SBATCH -J silicon
#SBATCH -A naiss2025-5-112

module load QuantumESPRESSO/7.2-nsc1-intel-2018b-eb
export OMP_NUM_THREADS=2
mpprun pw.x -input scf.in
mpprun bands.x -input bands.in
#mpprun plotband.x -input plotband.in

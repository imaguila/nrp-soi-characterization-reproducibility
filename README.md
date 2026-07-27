
# Reproducibility Package

This repository contains the data exports and analysis scripts used to reproduce the descriptive SOI characterization reported in the paper:

"From Pareto Fronts to Decision Spaces: A Method-Agnostic Workflow for Post-Optimization Decision Support in the Next Release Problem"

## Scope

This package does not include the source code of the interactive prototype. The prototype is a research vehicle and is available online as a demonstration. This repository only contains the exported data and scripts required to reproduce the tables and figures reported in the case-based assessment.

## Contents

- `data/`: exported WordProc subsets and saved SOIs.
- `scripts/compara.py`: script used to compute SOI metrics, pairwise similarities, consensus support, and figures.
- `outputs/tables/`: generated CSV tables.
- `outputs/figures/`: generated figures used in the manuscript.
- `workflow_parameters.md`: parameters used in the WordProc walkthrough.

## Reproduced artifacts

Running the script reproduces:

- Traceable narrowing table.
- Structural characterization of SOIs.
- Pairwise Jaccard and overlap matrices.
- Requirement inclusion frequency heatmap.
- Solution membership matrix across base SOIs.

## How to run

```bash
pip install -r requirements.txt
python scripts/compara.py

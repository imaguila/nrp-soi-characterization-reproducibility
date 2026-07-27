# NRP SOI Characterization Reproducibility Package

This repository contains the reproducibility package associated with the manuscript:

**From Pareto Fronts to Decision Spaces: A Method-Agnostic Workflow for Post-Optimization Decision Support in the Next Release Problem**

The package provides the exported data and analysis script used to reproduce the descriptive characterization of Solutions of Interest (SOIs) reported in the case-based assessment of the paper.

## Scope

This repository does **not** include the source code of the interactive prototype. The prototype is a research demonstrator and is not distributed as open-source software in this package.

The purpose of this repository is to reproduce the quantitative characterization reported in the manuscript from exported CSV files. In particular, the package supports reproduction of:

- the traceable narrowing table,
- the structural characterization of SOIs,
- pairwise SOI similarity matrices,
- consensus support by solution,
- requirement inclusion frequencies,
- solution membership across the base SOIs,
- generated figures used in the descriptive characterization.

## Repository Structure

```text
nrp-soi-characterization-reproducibility/
├── data/
│   ├── framed.csv
│   ├── domain.csv
│   ├── efficiency.csv
│   ├── hdbscan.csv
│   ├── kmediods.csv
│   ├── topsis.csv
│   ├── weight.csv
│   ├── con50.csv
│   ├── con75.csv
│   ├── con90.csv
│   └── fullParetoFronts/
│       ├── motoroladataset.txt
│       ├── motorolasol.txt
│       ├── mslitesol.txt
│       ├── ralicreqdataset.txt
│       ├── ralicreqsol.txt
│       ├── ralicSreqdataset.txt
│       ├── ralicSreqsol.txt
│       ├── req100dataset.txt
│       ├── req100frente.txt
│       ├── themedataset.txt
│       ├── themesol.txt
│       ├── wordprocdataset.txt
│       └── wordprocsol.txt
├── output/
│   ├── tables/
│   └── figures/
├── script/
│   └── compara.py
├── README.md
├── requirements.txt
├── workflow_parameters.md
├── DATA_LICENSE.md
├── LICENSE
└── CITATION.cff
```

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
```
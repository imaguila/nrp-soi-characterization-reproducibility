# Workflow Parameters Used in the WordProc Case-Based Assessment

This document reports the parameters used to generate the exported SOIs and consensus subsets included in this reproducibility package. The purpose is to make the descriptive characterization reported in the manuscript reproducible from the exported CSV files.
The source code of the interactive prototype is not included in this package. The package contains the exported data and the analysis script needed to reproduce the SOI-level tables and figures reported in the paper.
---
## 1. Dataset

- Instance: WordProc 50-requirement instance.
- Application domain: word-processing software release planning.
- Stakeholders: 4 weighted stakeholders.
- Original requirements: 50.
- Functional dependencies processed: 81.
- Independent requirement blocks after dependency processing: 42.
- Pareto-optimal front size: 407 non-dominated solutions.
- Objective functions available in the exported dataset:
    - satisfaction
    - effort
    - time
The exported SOI files use binary requirement-selection columns named `req_1`, `req_2`, ..., `req_42`.

---

# 2. Dataset Sources

The folder `data/fullParetoFronts/` contains benchmark-related files used by the prototype to initialize or derive NRP instances. These files are included for traceability and contextual documentation.

For the WordProc case used in the manuscript, the relevant files are:

```text
data/fullParetoFronts/wordprocdataset.txt
data/fullParetoFronts/wordprocsol.txt
```

The descriptive SOI characterization reported in the manuscript is not computed directly from these raw benchmark files. It is computed from the exported SOI CSV files located directly in `data/`.

---

## 3. Semantic Enrichment

The following base attributes were available and used to compute derived quality indicators:
    - satisfaction
    - effort
    - time

The derived indicators used in the walkthrough include:
    - productivity
    - opportunity
    - scope
    - response
    - squandering

Stakeholder coverage variables are included when available as:
    - stcov_cv1
    - stcov_cv2
    - stcov_cv3
    - stcov_cv4

---

## 4. Context Framing

The full Pareto front contains 407 non-dominated solutions.
The framed subset was obtained by applying the following contextual restriction:
    - Effort upper bound: 425.10
    - Interpretation: approximately 30% of the total effort budget
    - Resulting framed subset size: 49 solutions
    - Exported file: `data/framed.csv`

The framed subset is used as the reference baseline for the descriptive characterization.

---

## 5. SOI Exports Included in the Package

The following exported CSV files correspond to the SOIs used in the manuscript:

```text
data/framed.csv
data/domain.csv
data/efficiency.csv
data/hdbscan.csv
data/kmediods.csv
data/topsis.csv
data/weight.csv
data/con50.csv
data/con75.csv
data/con90.csv
```
The file `data/framed.csv` represents the contextualized decision space after applying the effort restriction. The remaining files correspond to lens-derived SOIs or consensus-derived SOIs.

---

## 6. Preference-Oriented Lenses
### 6.1 TOPSIS

Exported file: `data/topsis.csv`

Scoring method: TOPSIS

Metrics to maximize:
- productivity
- scope

Metrics to minimize:
- response
- squandering

Retained subset: top-N = 10 solutions

### 6.2 Weighted Sum

Exported file: `data/weight.csv`

Scoring method: Weighted Sum

Metrics to maximize:
- productivity
- scope

Metrics to minimize:
- response
- squandering

Retained subset: top-N = 10 solutions

---

## 7. Diversity-Oriented Lenses
### 7.1 HDBSCAN

Exported file: `data/hdbscan.csv`

Method: HDBSCAN

Purpose: identify dense structural groups and noise solutions within the framed subset.

Exported SOI size used in the descriptive characterization: 40 solutions

### 7.2 K-Medoids

Exported file: `data/kmediods.csv`

Method: PAM K-Medoids

Cluster selection: silhouette-driven configuration

Purpose: identify representative diversity-oriented groups within the framed subset.

Exported SOI size used in the descriptive characterization: 40 solutions

---

## 8. Efficiency-Oriented Lens

Exported file: `data/efficiency.csv`

Benefit metric: scope

Cost metric: squandering

Retained subset: top-N = 10 solutions

Purpose: identify solutions with favorable benefit-cost behavior under the selected interpretation.

---

## 9. Domain-Specific Lens

Exported file: `data/domain.csv`

Method: repeated top-N matching across selected quality indicators.

Purpose: identify solutions that repeatedly appear among the best-ranked alternatives according to selected domain-specific indicators.

High-match group size used in the walkthrough: 12 solutions
If the exact selected indicators are needed, they should be documented here according to the configuration used in the prototype.

---

## 10. Consensus-Based Combination

Consensus was computed using the following six base SOIs:
```text
domain
efficiency
hdbscan
kmediods
topsis
weight
```

The framed subset is not used as a vote in the consensus computation because it represents the contextualized baseline rather than a lens-derived SOI.

The already-combined consensus files `con50.csv`, `con75.csv`, and `con90.csv` are also not used as inputs to recompute consensus, in order to avoid circularity.

For each solution, the consensus score is computed as:

```text
consensus_score = number of base SOIs containing the solution / number of base SOIs
```

The following thresholds were used:


|Threshold	 |Exported file|	Resulting size|	Interpretation|
|---|---|---|---|
|0.50	|`data/con50.csv`	|17|	broad consensus pool|
|0.75	|`data/con75.csv`	|7	|compact consensus core|
|0.90	|`data/con90.csv`	|4	|strict consensus core|

The strict consensus core for `tau = 0.90` contains the following solution IDs:

```text
43, 44, 48, 49
```
---
## 11. Descriptive Metrics Reproduced by `compara.py`
The script `script/compara.py` computes the following descriptive metrics.

### 11.1 Set-Level Metrics
- size
- selectivity_vs_framed
- unique_solution_count_excluding_framed


### 11.2 Requirement-Level Metrics
- active_req_count
- core_req_count
- core_req_ratio
- req_density
- variable_req_count
- req_variability

### 11.3 Pairwise SOI Similarity Metrics
- Jaccard similarity
- overlap coefficient
- directional containment
### 11.4 Consensus Metrics
- consensus_score
- support_count
- support_names

membership in consensus thresholds 0.50, 0.75, and 0.90
---

## 12. Generated Output Files

Running the analysis script produces the following table outputs in `output/tables/`:

```text
output/tables/out_soi_summary.csv
output/tables/out_soi_metrics_latex.tex
output/tables/out_pairwise_jaccard.csv
output/tables/out_pairwise_overlap.csv
output/tables/out_pairwise_containment.csv
output/tables/out_consensus_by_solution.csv
output/tables/out_consensus_sizes.csv
output/tables/out_consensus_sizes_latex.tex
output/tables/out_requirement_frequency_by_soi.csv
```
If figure generation is enabled, the script also produces the following files in `output/figures/`:

```text
output/figures/fig_pairwise_jaccard.png
output/figures/fig_pairwise_overlap.png
output/figures/fig_soi_summary_bars.png
output/figures/fig_requirement_frequency_heatmap.png
output/figures/fig_solution_consensus_membership.png
```
The figures are derived artifacts. They can be regenerated from the exported CSV files and the script.
---
## 13. Reproduction Command
From the root folder of the reproducibility package:

```bash
pip install -r requirements.txt
python script/compara.py
```
The default configuration expects exported SOI CSV files in `data/` and writes outputs to `output/`.
If custom paths are needed, use:

```bash
python script/compara.py --data-dir data --out-dir output
```
To generate only table outputs and skip figures:

```bash
python script/compara.py --no-figures
```
---
## 14. Scope of the Reproducibility Package

This package is intended to reproduce the descriptive SOI characterization reported in the manuscript. It does not reproduce the full interactive session inside the prototype.
The package supports reproduction of:
- the traceable narrowing table,
- the structural characterization table,
- pairwise SOI similarity matrices,
- consensus support by solution,
- requirement inclusion frequencies,
- solution membership across base SOIs,
- figures derived from these outputs.
- The package does not include:
- the source code of the interactive prototype,
- the Streamlit application implementation,
- UI state management code,
- exploratory development scripts not used in the manuscript.

---

## 15. Relationship Between Raw Benchmark Files and Exported SOIs
The files in `data/fullParetoFronts/` are included to document the broader benchmark context and the original input material used by the prototype.
The files directly used by the reproducibility script are the exported SOI CSV files located in `data/`.


In other words:

```text
data/fullParetoFronts/     -> benchmark-context files
data/*.csv                 -> exported SOIs used for reproducibility
script/compara.py          -> analysis script
output/                    -> generated tables and figures
```
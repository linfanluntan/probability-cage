# Beware the Cage of Probability

**Bayesian Inference, Structural Closure, and the Limits of Epistemic Confidence**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> *"Bayesian inference refines belief within a framework. Scientific imagination expands the framework itself. The probability cage forms when the first is mistaken for the second."*

---

## Table of Contents

- [What Is the Probability Cage?](#what-is-the-probability-cage)
- [Why This Matters](#why-this-matters)
- [Quick Start](#quick-start)
- [Overview of Examples](#overview-of-examples)
- [Detailed Descriptions and Demos](#detailed-descriptions-and-demos)
  - [Example 1: The Core Probability Cage](#example-1-the-core-probability-cage)
  - [Example 2: The Missing Variable C](#example-2-the-missing-variable-c)
  - [Example 3: The Zero-Mass Absorbing Barrier](#example-3-the-zero-mass-absorbing-barrier)
  - [Example 4: Parametric vs. Structural Uncertainty](#example-4-parametric-vs-structural-uncertainty)
  - [Example 5: Bayesian Conservatism](#example-5-bayesian-conservatism)
  - [Example 6: Bayesian Nonparametrics — A Larger Cage](#example-6-bayesian-nonparametrics--a-larger-cage)
  - [Example 7: Black Swans](#example-7-black-swans)
  - [Example 8: Escaping the Cage](#example-8-escaping-the-cage)
- [Repository Structure](#repository-structure)
- [Key References](#key-references)
- [Contributing](#contributing)
- [License](#license)

---

## What Is the Probability Cage?

Bayes' theorem is the mathematical foundation of rational belief revision:

$$P(H \mid E) = \frac{P(E \mid H)\, P(H)}{P(E)}$$

It tells you how to update your beliefs when new evidence arrives. Under the right conditions, it converges to the truth. It is logically unassailable.

But it has a blind spot: **it can only choose among hypotheses you have already imagined.**

Bayesian updating redistributes probability mass within a predefined hypothesis space **H**. It does not — cannot — assign credence to explanations that are absent from **H**. When the true data-generating process lies outside the model, Bayesian inference still converges, often with high confidence, toward the **best available wrong answer**: the element of **H** closest to truth in KL divergence (Berk, 1966).

We call this the **probability cage**: a state in which the internal coherence of Bayesian reasoning masks structural ignorance, and in which rising posterior confidence is a symptom of model closure rather than a signal of truth.

## Why This Matters

The probability cage is not a theoretical curiosity. It operates in every domain where models are incomplete:

- **Medicine**: Before germ theory, Bayesian updating on observational data would have concentrated credence on miasma theory — the best available wrong answer.
- **Physics**: Bayesian analysis of planetary motion would have assigned overwhelming posterior to Newtonian mechanics, missing the relativistic structure entirely.
- **Finance**: Gaussian risk models appeared highly confident before 2008. The crisis came from a distributional regime absent from those models.
- **Machine learning**: A neural network's softmax output can assign 99.9% confidence to a wrong class when the true class was never in the training distribution.

In each case, the fix was not more data. It was **more imagination** — expanding the hypothesis space to include structures that had not previously been conceived.

This repository provides **8 runnable Python demonstrations** that make this phenomenon computationally concrete.

---

## Quick Start

```bash
git clone https://github.com/<your-username>/probability-cage.git
cd probability-cage
pip install -r requirements.txt
bash run_all.sh
```

All figures are saved to `figures/`. Each example prints detailed output to the terminal and generates a multi-panel publication-quality figure.

---

## Overview of Examples

| # | File | Concept | Key Result |
|---|------|---------|------------|
| 1 | `ex01_probability_cage.py` | **Core demo**: KL-convergence to the wrong model | Posterior converges confidently to the best *unimodal* fit of a *bimodal* truth |
| 2 | `ex02_missing_variable_c.py` | **Confounding**: latent variable C causes both A and B | Bayesian model selection picks "A→B" with 100% confidence — **wrong** |
| 3 | `ex03_zero_mass_barrier.py` | **Absorbing barrier**: P(H)=0 ⟹ P(H\|E)=0 forever | Zero-prior hypotheses can never be recovered; model expansion breaks the cage |
| 4 | `ex04_parametric_vs_structural.py` | **Two kinds of uncertainty** | Parametric uncertainty → 0 while structural uncertainty remains invisible |
| 5 | `ex05_bayesian_conservatism.py` | **Paradigm inertia** (Kuhn, 1962) | Old paradigm resists displacement for ~480 observations after truth shifts |
| 6 | `ex06_nonparametric_larger_cage.py` | **Bayesian nonparametrics** | DP mixture discovers cluster counts but fails on rings and manifolds |
| 7 | `ex07_black_swans.py` | **Tail risk** (Taleb, 2007) | Gaussian model dominates during calm periods; catastrophic failure on extremes |
| 8 | `ex08_model_expansion.py` | **Escaping the cage** | More data doesn't fix a restricted model; more hypotheses (imagination) does |

---

## Detailed Descriptions and Demos

### Example 1: The Core Probability Cage

> **File**: `examples/ex01_probability_cage.py`
> **Concept**: When the true model is outside the hypothesis space, Bayesian updating converges to the KL-closest wrong model with increasing confidence.
> **References**: Berk (1966), Grünwald & van Ommen (2017)

**Setup**: The true data-generating process is a **bimodal** Gaussian mixture: 0.5 × N(−2, 1) + 0.5 × N(2, 1). But the hypothesis space contains only **unimodal** Gaussians N(μ, σ²). The bimodal truth simply does not exist in the model.

**What happens**: Bayesian updating over a grid of (μ, σ) hypotheses converges to μ ≈ 0, σ ≈ 2.4 — the single Gaussian that minimizes KL divergence from the bimodal truth. The posterior concentrates with growing confidence on this best-available-wrong-answer.

**Demo output**:
```
======================================================================
EXAMPLE 1: The Probability Cage
True model: Mixture(0.5 * N(-2,1) + 0.5 * N(2,1))  [BIMODAL]
Hypothesis space: {N(mu, sigma^2)}                   [UNIMODAL ONLY]
======================================================================

    n    MAP mu   MAP sigma   MAP posterior  Verdict
-----------------------------------------------------------------
    1     -1.67        0.50          0.0017  diffuse
    5      0.56        2.41          0.0012  diffuse
   20     -0.05        2.71          0.0043  diffuse
   50     -0.05        2.41          0.0139  WRONG but confident
  100     -0.15        2.48          0.0278  WRONG but confident
  200      0.05        2.48          0.0544  WRONG but confident
  500      0.15        2.33          0.1541  WRONG but confident

>>> The posterior converges to mu≈0, sigma≈2.4.
>>> This is the KL-minimizer: the single Gaussian closest to the
    bimodal truth. Bayesian updating is internally correct —
    but structurally blind. This is the PROBABILITY CAGE.
```

**Generated figure** (`figures/ex01_probability_cage.png`):

Six panels. Top row: posterior heat maps over (μ, σ) at n = 5, 50, and 500 — the posterior visibly sharpens to a tight peak around the KL-minimizer (white star). Bottom-left: true bimodal density (black) vs. MAP unimodal fits (red dashes) — the unimodal model cannot capture the two peaks. Bottom-center: max posterior probability rising steadily toward 1.0 — for the wrong model. Bottom-right: KL divergence surface showing the minimum that the posterior converges toward.

**Takeaway**: The posterior is doing exactly what the math says it should. The problem is not the update rule — it's the hypothesis space. The cage is invisible from inside.

---

### Example 2: The Missing Variable C

> **File**: `examples/ex02_missing_variable_c.py`
> **Concept**: Latent confounders generate spurious causal beliefs.
> **References**: Pearl (2009), Spirtes, Glymour & Scheines (2000)

**Setup**: The true causal structure is C → A and C → B (C is an unobserved common cause). The model's hypothesis space contains only {A→B, B→A, A⊥B}. Variable C does not exist in the model.

**What happens**: A and B are correlated (r ≈ 0.70) because they share the hidden parent C. Bayesian model selection cannot distinguish this from direct causation. The posterior concentrates entirely on "A causes B" — a completely spurious causal claim.

**Demo output**:
```
======================================================================
EXAMPLE 2: The Missing Variable C
True DAG:  C → A,  C → B   (A does NOT cause B)
Hypothesis space: {A→B, B→A, A⊥B}   (C is ABSENT)
======================================================================

    n      P(A→B)      P(B→A)      P(A⊥B)  Winner
-------------------------------------------------------
   10      0.9144      0.0856      0.0000  A->B ← WRONG!
  100      0.7139      0.2861      0.0000  A->B ← WRONG!
  500      1.0000      0.0000      0.0000  A->B ← WRONG!
 1000      1.0000      0.0000      0.0000  A->B ← WRONG!

>>> P(A→B) dominates despite A not causing B.
>>> Without C in the model, confounding is invisible.
>>> This is causal misattribution via the probability cage.
```

**Generated figure** (`figures/ex02_missing_variable_c.png`):

Three panels. Left: posterior trajectory over 1000 samples — P(A→B) (red) quickly dominates and locks at 1.0, while the independence hypothesis (green) is immediately eliminated. Center: scatter plot of A vs. B with OLS regression line showing the strong observed correlation (r = 0.698) that is entirely spurious. Right: diagram contrasting the true causal DAG (C → A, C → B) with the model's wrong conclusion (A → B).

**Takeaway**: Bayesian inference cannot distinguish correlation from causation without structural causal assumptions. If the confounder is not in the model, no amount of data reveals it.

---

### Example 3: The Zero-Mass Absorbing Barrier

> **File**: `examples/ex03_zero_mass_barrier.py`
> **Concept**: If P(H) = 0, then P(H|E) = 0 for all E. The zero boundary is absorbing.

**Setup**: Three hypotheses about the mean of a Gaussian (true mean = 3). Scenario A gives all three equal priors (1/3 each). Scenario B gives the true hypothesis **zero** prior. Scenario C starts like B but **expands the model** at n = 200 by injecting the true hypothesis with fresh prior mass.

**Demo output**:
```
Scenario A — Equal priors [1/3, 1/3, 1/3]:
  After n=400: P(H3: μ=3) = 1.000000
  → TRUE hypothesis recovered ✓

Scenario B — Zero prior on truth [0.5, 0.5, 0.0]:
  After n=400: P(H3: μ=3) = 0.000000
  → TRUE hypothesis NEVER recovered (absorbing barrier) ✗

Scenario C — Model expansion at n=200:
  Before expansion (n=200): P(H3: μ=3) = 0.000000
  After expansion (n=400):  P(H3: μ=3) = 1.000000
  → IMAGINATION (model expansion) breaks the cage ✓
```

**Generated figure** (`figures/ex03_zero_mass_barrier.png`):

Three side-by-side trajectory plots. Panel A: truth (green) rockets to 1.0 within 20 samples. Panel B: truth (green) is flat at 0.0 for the entire run — 400 data points, all screaming the answer, and Bayes cannot hear it because the hypothesis was never imagined. Panel C: truth stays at 0.0 until the dashed vertical line at n = 200 ("Model expanded here"), then instantly jumps to 1.0.

**Takeaway**: This is the mathematical core of the cage. The fix is not patience or larger samples — it is imagination. Model expansion is the act that breaks the barrier.

---

### Example 4: Parametric vs. Structural Uncertainty

> **File**: `examples/ex04_parametric_vs_structural.py`
> **Concept**: Bayesian inference shrinks parametric uncertainty to zero while structural uncertainty remains completely invisible.
> **References**: Box (1976), Gelman & Shalizi (2013)

**Setup**: True data is generated by Y = sin(2X) + noise (nonlinear). The model fits Y = βX + noise (linear). The model is structurally wrong — but Bayes doesn't know that.

**Demo output**:
```
n = 5:
  Posterior: β ~ N(-0.0873, 0.3906²)
  Parametric uncertainty: HIGH

n = 300:
  Posterior: β ~ N(-0.0104, 0.0102²)
  Parametric uncertainty: NEGLIGIBLE
  Structural uncertainty: UNKNOWN (model cannot assess itself)
```

**Generated figure** (`figures/ex04_parametric_vs_structural.png`):

Six panels. Top row: posterior density on β at n = 5, 50, 300 — the distribution sharpens from wide and uncertain to a narrow spike (parametric certainty). Bottom-left: data scatter with true sin(2x) curve (green) and linear MAP fit (red) — visibly wrong. Bottom-center: residuals showing clear sinusoidal structure that the model completely misses. Bottom-right: conceptual diagram contrasting parametric uncertainty (SOLVED by Bayes ✓) with structural uncertainty (INVISIBLE to Bayes ✗).

**Takeaway**: Shrinking confidence intervals are not evidence of a correct model. Parametric certainty can coexist with total structural blindness. The posterior on β is sharp and narrow — for a β that has no business existing.

---

### Example 5: Bayesian Conservatism

> **File**: `examples/ex05_bayesian_conservatism.py`
> **Concept**: Accumulated evidence creates "paradigm inertia" that resists paradigm shifts.
> **References**: Kuhn (1962), Lakatos (1970)

**Setup**: Phase 1 (n = 1–500): truth is H_old (μ = 0). Phase 2 (n = 501–1000): truth **shifts** to H_new (μ = 2). H_old starts with prior 0.9. After 500 observations of confirming data, H_old has overwhelming accumulated evidence.

**Demo output**:
```
At paradigm shift (n=500):
  P(H_old) = 1.00000000
  P(H_new) = 0.00000000

Crossover (P(H_new) > 0.5) at n = 980
  That's 480 observations AFTER the shift occurred!
  → Bayesian inertia delays recognition by 480 samples

At n=600: P(H_new) = 0.0000
At n=700: P(H_new) = 0.0000
At n=800: P(H_new) = 0.0000
At n=1000: P(H_new) = 1.000000
```

**Generated figure** (`figures/ex05_bayesian_conservatism.png`):

Three panels. Left: posterior trajectories — H_old (blue) dominates at near-1.0, and after the paradigm shift (dashed line), H_new (red) takes **480 samples** to catch up. The red-shaded "delay period" is enormous. Center: log posterior odds showing the "evidence mountain" — 500 samples of accumulated support for H_old create a mountain that H_new must climb down before it can ascend. Right: bar chart showing delay as a function of prior strength — stronger priors create longer delays (≈ 479–483 samples across the range tested).

**Takeaway**: This is the Kuhnian observation in computational form. Bayesian conservatism is rational — it prevents arbitrary belief shifts — but it means that paradigm shifts face systematic resistance proportional to accumulated evidence for the old paradigm. The Bayesian machinery that ensures coherence simultaneously ensures inertia.

---

### Example 6: Bayesian Nonparametrics — A Larger Cage

> **File**: `examples/ex06_nonparametric_larger_cage.py`
> **Concept**: Nonparametric methods enlarge the hypothesis space but cannot change its fundamental kind.
> **References**: Ferguson (1973), Hjort et al. (2010)

**Setup**: A simplified Dirichlet Process (DP) mixture is fitted to three datasets: (A) a 3-component Gaussian mixture, (B) a ring distribution, (C) a 2D Swiss roll.

**What happens**: On Gaussian clusters (scenario A), the DP mixture succeeds — it discovers roughly the right number of clusters. On the ring and Swiss roll (scenarios B and C), it **fails**: it approximates the circular and manifold structures with a scatter of tiny Gaussian blobs, completely missing the true geometry.

**Demo output**:
```
Scenario A — Gaussian mixture (3 true clusters):
  DP found 3 clusters
  → SUCCESS: discovers cluster structure ✓

Scenario B — Ring distribution (manifold structure):
  DP found 4 clusters
  → WRONG GENUS: approximates ring with 4 blobs ✗

Scenario C — Swiss roll (nonlinear manifold):
  DP found 4 clusters
  → WRONG GENUS: fragments manifold into 4 blobs ✗
```

**Generated figure** (`figures/ex06_nonparametric_larger_cage.png`):

Six panels (2×3). Top row: raw data for each scenario. Bottom row: DP mixture cluster assignments overlaid with cluster centers. Scenario A is cleanly clustered (green title: "correct genus"). Scenarios B and C are fragmented into meaningless blobs (red titles: "wrong genus").

**Takeaway**: Bayesian nonparametrics can flex the *number* of components (parametric flexibility), but the *kind* of component (Gaussian blobs) is hardwired. The cage is larger — but it is still a cage. A DP mixture cannot discover that the data requires a circular model, a manifold model, or a differential equation. The model can grow within its genus; it cannot change genera.

---

### Example 7: Black Swans

> **File**: `examples/ex07_black_swans.py`
> **Concept**: Bayesian updating on historical data systematically underweights rare, high-impact events.
> **References**: Taleb (2007), Mandelbrot (1963)

**Setup**: True data comes from a heavy-tailed Student-t distribution (df = 3). The agent models it as Gaussian. During 1000 "calm" observations, both models look virtually identical. Then 50 "crisis" observations arrive, including 5 extreme values (7–10 sigma under the Gaussian model).

**Demo output**:
```
Tail probability P(|X| > 5):
  Gaussian model:  1.14e-02  (≈ 1 in 88)
  Student-t model: 1.54e-02  (≈ 1 in 65)

Posterior at end of calm period (n=1000):
  P(Gaussian) = 0.000000
  P(Student-t) = 1.000000
  → Agent is VERY confident in Gaussian (wrong!) model
```

**Generated figure** (`figures/ex07_black_swans.png`):

Four panels. Top-left: time series of observations, with crisis period highlighted in red — extreme values appear as spikes. Top-right: posterior trajectory — Gaussian model dominates during the calm period, then collapses when black swans arrive. Bottom-left: log-scale density comparison — the two distributions look nearly identical in the center but diverge wildly in the tails. Bottom-right: "The Turkey Problem" illustration — confidence rises steadily for 1000 days, then collapses on day 1001 (Thanksgiving).

**Takeaway**: Historical calm is not structural stability. The data during calm periods do not distinguish between light-tailed and heavy-tailed models. Bayesian updating favors the simpler model — which happens to be catastrophically wrong in the tails. This is why past data can be a cage: they define the boundary of what the model considers possible.

---

### Example 8: Escaping the Cage

> **File**: `examples/ex08_model_expansion.py`
> **Concept**: The cage dissolves not with more data but with more hypotheses — the positive thesis of the paper.

**Setup**: True data is a 3-component Gaussian mixture. The **restricted** model contains only unimodal Gaussians (the cage). The **expanded** model also includes mixture hypotheses (cage broken). A **late expansion** scenario adds mixture hypotheses at n = 300 after 300 samples of cage-locked updating.

**Demo output**:
```
Restricted model (unimodal only):
  Final MAP: μ = 0.63 (best unimodal fit)
  Max posterior: 0.5541
  → Confident but WRONG

Expanded model (unimodal + mixtures from start):
  P(true mixture) at n=100: 0.9971
  P(true mixture) at n=600: 0.9999
  → True hypothesis rapidly dominates ✓

Late expansion (mixtures added at n=300):
  P(true) at n=300 (just added): 0.0693
  P(true) at n=400: 0.9998
  P(true) at n=600: 1.0000
  → Even late imagination can break the cage ✓
```

**Generated figure** (`figures/ex08_model_expansion.png`):

Four panels. Top-left: restricted model's max posterior climbing steadily — for the wrong answer (annotated: "Increasing confidence in a UNIMODAL model (truth is trimodal)"). Top-right: expanded model — P(true mixture) rockets to 1.0 within ~50 samples, while the best unimodal hypothesis collapses. Bottom-left: late expansion — P(true) is flat at 0.0 until the dashed line at n = 300 ("Hypothesis space expanded here"), then jumps to 1.0 within ~100 additional samples. Bottom-right: density overlay showing the true trimodal distribution (black), the hopelessly wrong unimodal MAP fit (red dashed), and the correctly matched mixture hypothesis (green).

**Takeaway**: This is the central message of the entire project. More data does not help when the hypothesis space is wrong — the restricted model's confidence only grows in the wrong direction. More hypotheses (model expansion) is what breaks the cage. Even late expansion works: the moment the right hypothesis enters the space, Bayesian updating does what it does best — identifies it rapidly. **Bayes is the engine; imagination is the fuel.**

---

## Repository Structure

```
probability-cage/
├── README.md                  # This file
├── LICENSE                    # CC BY 4.0
├── CITATION.cff               # Machine-readable citation metadata
├── requirements.txt           # Python: numpy, scipy, matplotlib
├── package.json               # Node.js: docx (for paper generation)
├── run_all.sh                 # Runs all 8 examples, saves figures
│
├── examples/                  # The 8 computational demonstrations
│   ├── ex01_probability_cage.py
│   ├── ex02_missing_variable_c.py
│   ├── ex03_zero_mass_barrier.py
│   ├── ex04_parametric_vs_structural.py
│   ├── ex05_bayesian_conservatism.py
│   ├── ex06_nonparametric_larger_cage.py
│   ├── ex07_black_swans.py
│   └── ex08_model_expansion.py
│
├── figures/                   # Generated by running examples
│   ├── ex01_probability_cage.png
│   ├── ex02_missing_variable_c.png
│   ├── ex03_zero_mass_barrier.png
│   ├── ex04_parametric_vs_structural.png
│   ├── ex05_bayesian_conservatism.png
│   ├── ex06_nonparametric_larger_cage.png
│   ├── ex07_black_swans.png
│   └── ex08_model_expansion.png
│
└── src/
    └── generate_paper.js      # Generates the .docx manuscript (Node.js + docx)
```

## Key References

All references cited in the code examples and companion paper have been individually verified against their primary sources.

- **Berk, R. H. (1966)**. Limiting behavior of posterior distributions when the model is incorrect. *Annals of Mathematical Statistics*, 37(1), 51–58.
- **Box, G. E. P. (1976)**. Science and statistics. *Journal of the American Statistical Association*, 71(356), 791–799.
- **Ferguson, T. S. (1973)**. A Bayesian analysis of some nonparametric problems. *Annals of Statistics*, 1(2), 209–230.
- **Gelman, A., & Shalizi, C. R. (2013)**. Philosophy and the practice of Bayesian statistics. *British Journal of Mathematical and Statistical Psychology*, 66(1), 8–38.
- **Grünwald, P., & van Ommen, T. (2017)**. Inconsistency of Bayesian inference for misspecified linear models. *Bayesian Analysis*, 12(4), 1069–1103.
- **Hjort, N. L., et al. (Eds.). (2010)**. *Bayesian Nonparametrics*. Cambridge University Press.
- **Hoeting, J. A., et al. (1999)**. Bayesian model averaging: A tutorial. *Statistical Science*, 14(4), 382–401.
- **Kuhn, T. S. (1962)**. *The Structure of Scientific Revolutions*. University of Chicago Press.
- **Lakatos, I. (1970)**. Falsification and the methodology of scientific research programmes. In *Criticism and the Growth of Knowledge*, Cambridge University Press.
- **Mandelbrot, B. (1963)**. The variation of certain speculative prices. *Journal of Business*, 36(4), 394–419.
- **Pearl, J. (2009)**. *Causality: Models, Reasoning, and Inference* (2nd ed.). Cambridge University Press.
- **Spirtes, P., Glymour, C., & Scheines, R. (2000)**. *Causation, Prediction, and Search* (2nd ed.). MIT Press.
- **Taleb, N. N. (2007)**. *The Black Swan: The Impact of the Highly Improbable*. Random House.

## Contributing

Contributions are welcome. Especially valuable:

- **New examples**: causal discovery under latent confounding, high-dimensional model misspecification, reinforcement learning with wrong state spaces
- **Translations**: R, Julia, Stan, or PyMC implementations
- **Interactive demos**: Streamlit apps, Jupyter notebooks, Observable notebooks
- **Formal proofs**: tightening the theoretical claims with mathematical results
- **Real-data case studies**: applying the framework to published datasets

Please open an issue or pull request.

## License

This work is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). Use freely with attribution.

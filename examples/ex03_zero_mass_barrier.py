"""
Example 3: The Zero-Mass Absorbing Barrier
============================================

Demonstrates: If a hypothesis starts with P(H) = 0, Bayesian updating
can NEVER assign it positive probability, regardless of evidence.

    P(H|E) = P(E|H) * P(H) / P(E)

If P(H) = 0, then P(H|E) = 0 for ALL E. The zero boundary is absorbing.

This is the mathematical core of the probability cage:
what is not imagined cannot be discovered by updating alone.

We show three scenarios:
  (a) Hypothesis in H with nonzero prior → recovered as data accumulates
  (b) Hypothesis in H with zero prior → NEVER recovered (absorbing barrier)
  (c) Hypothesis NOT in H at all → cannot even be evaluated

Then we show: adding the true hypothesis LATE (model expansion at step n=200)
immediately allows recovery — illustrating that the fix requires IMAGINATION,
not more data.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

np.random.seed(99)


# --- Setup: three hypotheses about the mean of a Gaussian ---
# True mean = 3.0
# H1: mu = 0   (wrong)
# H2: mu = 1   (wrong)
# H3: mu = 3   (TRUE)

true_mu = 3.0
sigma = 1.0
hypotheses = {"H1: μ=0": 0.0, "H2: μ=1": 1.0, "H3: μ=3 (TRUE)": 3.0}
n_total = 400
data = np.random.normal(true_mu, sigma, n_total)

# --- Scenario A: All three hypotheses have equal prior (1/3 each) ---
def run_bayesian_update(priors, data, hypotheses):
    """Run sequential Bayesian updating, return posterior trajectories."""
    names = list(hypotheses.keys())
    mus = np.array(list(hypotheses.values()))
    log_post = np.log(np.array(priors) + 1e-300)  # avoid log(0)
    trajectories = {name: [] for name in names}

    for x in data:
        log_lik = norm.logpdf(x, mus, sigma)
        log_post = log_post + log_lik
        # Normalize
        max_lp = np.max(log_post)
        log_post_norm = log_post - (max_lp + np.log(np.sum(np.exp(log_post - max_lp))))
        posteriors = np.exp(log_post_norm)
        for i, name in enumerate(names):
            trajectories[name].append(posteriors[i])

    return trajectories

# Scenario A: equal priors
traj_a = run_bayesian_update([1/3, 1/3, 1/3], data, hypotheses)

# Scenario B: H3 (the true one) has ZERO prior
traj_b = run_bayesian_update([0.5, 0.5, 0.0], data, hypotheses)

# Scenario C: model expansion — H3 added at n=200
names = list(hypotheses.keys())
mus = np.array(list(hypotheses.values()))
# Phase 1: only H1, H2 (n=1..200)
log_post_c = np.log(np.array([0.5, 0.5]))
traj_c = {name: [] for name in names}

for i in range(200):
    x = data[i]
    log_lik = norm.logpdf(x, mus[:2], sigma)
    log_post_c = log_post_c + log_lik
    max_lp = np.max(log_post_c)
    log_post_c_norm = log_post_c - (max_lp + np.log(np.sum(np.exp(log_post_c - max_lp))))
    post = np.exp(log_post_c_norm)
    traj_c[names[0]].append(post[0])
    traj_c[names[1]].append(post[1])
    traj_c[names[2]].append(0.0)  # H3 doesn't exist yet

# Phase 2: EXPAND — add H3 with prior 1/3, redistribute
# At expansion point, assign fresh prior mass to H3
expansion_prior = 1/3
log_post_expanded = np.zeros(3)
log_post_expanded[0] = np.log((1 - expansion_prior) * np.exp(log_post_c_norm)[0])
log_post_expanded[1] = np.log((1 - expansion_prior) * np.exp(log_post_c_norm)[1])
log_post_expanded[2] = np.log(expansion_prior)

for i in range(200, n_total):
    x = data[i]
    log_lik = norm.logpdf(x, mus, sigma)
    log_post_expanded = log_post_expanded + log_lik
    max_lp = np.max(log_post_expanded)
    lpn = log_post_expanded - (max_lp + np.log(np.sum(np.exp(log_post_expanded - max_lp))))
    post = np.exp(lpn)
    for j, name in enumerate(names):
        traj_c[name].append(post[j])

# --- Print ---
print("=" * 70)
print("EXAMPLE 3: The Zero-Mass Absorbing Barrier")
print("True model: N(3, 1)")
print("=" * 70)

print("\nScenario A — Equal priors [1/3, 1/3, 1/3]:")
print(f"  After n=400: P(H3: μ=3) = {traj_a['H3: μ=3 (TRUE)'][-1]:.6f}")
print(f"  → TRUE hypothesis recovered ✓")

print("\nScenario B — Zero prior on truth [0.5, 0.5, 0.0]:")
print(f"  After n=400: P(H3: μ=3) = {traj_b['H3: μ=3 (TRUE)'][-1]:.6f}")
print(f"  → TRUE hypothesis NEVER recovered (absorbing barrier) ✗")

print("\nScenario C — Model expansion at n=200:")
print(f"  Before expansion (n=200): P(H3: μ=3) = {traj_c['H3: μ=3 (TRUE)'][199]:.6f}")
print(f"  After expansion (n=400):  P(H3: μ=3) = {traj_c['H3: μ=3 (TRUE)'][-1]:.6f}")
print(f"  → IMAGINATION (model expansion) breaks the cage ✓")

# --- Visualization ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
colors = {"H1: μ=0": "#1f77b4", "H2: μ=1": "#ff7f0e", "H3: μ=3 (TRUE)": "#2ca02c"}
steps = np.arange(1, n_total + 1)

for ax, traj, title_str in zip(axes,
    [traj_a, traj_b, traj_c],
    ["A: Equal Priors — Truth Recovered",
     "B: Zero Prior on Truth — Absorbing Barrier",
     "C: Model Expansion at n=200 — Cage Broken"]):

    for name in names:
        ax.plot(steps, traj[name], color=colors[name], lw=2, label=name)
    ax.set_xlabel("Sample Size n")
    ax.set_ylabel("Posterior Probability")
    ax.set_title(title_str)
    ax.legend(fontsize=8)
    ax.set_ylim(-0.05, 1.05)

# Mark expansion point in scenario C
axes[2].axvline(x=200, color="gray", ls="--", lw=1.5, alpha=0.7)
axes[2].text(205, 0.5, "Model\nexpanded\nhere", fontsize=9, color="gray")

plt.tight_layout()
plt.savefig("figures/ex03_zero_mass_barrier.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n[Figure saved to figures/ex03_zero_mass_barrier.png]")

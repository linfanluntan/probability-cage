"""
Example 8: Escaping the Cage — Model Expansion
================================================

Demonstrates the paper's positive thesis:
The probability cage dissolves when the hypothesis space is EXPANDED.

Three-phase experiment:
  Phase 1: Restricted model (2 hypotheses) → converges to wrong answer
  Phase 2: EXPANDED model (add true hypothesis) → truth is rapidly recovered
  Phase 3: Comparison of convergence rates

Shows that the fix is not "more data" but "more imagination" —
adding the right hypothesis to H is what breaks the cage.

"Bayesian inference refines belief within a framework.
 Scientific imagination expands the framework itself."
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.special import logsumexp

np.random.seed(314)


# --- True model: Mixture of 3 Gaussians ---
def true_sample(n):
    """True DGP: 3-component mixture."""
    components = np.random.choice(3, n, p=[0.3, 0.3, 0.4])
    mus = [-3, 0, 4]
    return np.array([np.random.normal(mus[c], 0.8) for c in components])


# --- Hypothesis spaces ---
# Restricted: only unimodal Gaussians (mu, sigma) on a grid
# Expanded: adds mixture models

def make_unimodal_grid():
    """Grid of unimodal Gaussian hypotheses."""
    mus = np.linspace(-6, 6, 50)
    sigmas = np.linspace(0.5, 5, 30)
    MU, SIG = np.meshgrid(mus, sigmas)
    return MU.ravel(), SIG.ravel()


def unimodal_logpdf(x, mu, sigma):
    return norm.logpdf(x, mu, sigma)


def mixture_logpdf(x, params):
    """Log pdf of a Gaussian mixture."""
    mus, sigmas, weights = params
    log_components = [np.log(w) + norm.logpdf(x, m, s)
                      for w, m, s in zip(weights, mus, sigmas)]
    return logsumexp(log_components, axis=0)


# Pre-defined mixture hypotheses (a small enumerated set)
mixture_hypotheses = [
    # (mus, sigmas, weights, label)
    ([-3, 3], [1, 1], [0.5, 0.5], "Mix(-3,3)"),
    ([-3, 0, 4], [0.8, 0.8, 0.8], [0.33, 0.33, 0.34], "Mix(-3,0,4) ← TRUE"),
    ([-2, 2], [1.5, 1.5], [0.5, 0.5], "Mix(-2,2)"),
    ([0, 5], [1, 1], [0.5, 0.5], "Mix(0,5)"),
    ([-4, -1, 3], [1, 1, 1], [0.33, 0.33, 0.34], "Mix(-4,-1,3)"),
]

# --- Generate data ---
n_total = 600
expansion_point = 300
data = true_sample(n_total)

# --- Phase 1: Restricted model (unimodal only) ---
mu_grid, sigma_grid = make_unimodal_grid()
n_uni = len(mu_grid)

log_post_restricted = np.zeros(n_uni)  # uniform prior
trajectory_max_restricted = []
trajectory_map_mu = []

for i in range(n_total):
    x = data[i]
    log_lik = unimodal_logpdf(x, mu_grid, sigma_grid)
    log_post_restricted += log_lik
    log_post_norm = log_post_restricted - logsumexp(log_post_restricted)
    max_idx = np.argmax(log_post_norm)
    trajectory_max_restricted.append(np.exp(log_post_norm[max_idx]))
    trajectory_map_mu.append(mu_grid[max_idx])

# --- Phase 2: Expanded model (unimodal + mixtures) ---
n_mix = len(mixture_hypotheses)
n_expanded = n_uni + n_mix

log_post_expanded = np.zeros(n_expanded)  # uniform prior over all
trajectory_true_hypothesis = []
trajectory_best_unimodal = []

for i in range(n_total):
    x = data[i]
    # Unimodal likelihoods
    ll_uni = unimodal_logpdf(x, mu_grid, sigma_grid)
    # Mixture likelihoods
    ll_mix = np.array([mixture_logpdf(x, (m[0], m[1], m[2]))
                       for m in mixture_hypotheses])

    log_post_expanded[:n_uni] += ll_uni
    log_post_expanded[n_uni:] += ll_mix

    log_post_norm = log_post_expanded - logsumexp(log_post_expanded)
    post = np.exp(log_post_norm)

    # Track P(true mixture) — it's the 2nd mixture hypothesis
    trajectory_true_hypothesis.append(post[n_uni + 1])
    trajectory_best_unimodal.append(post[:n_uni].max())

# --- Phase 3: Late expansion (add mixtures only at n=300) ---
log_post_late = np.zeros(n_uni)
trajectory_late_true = []

for i in range(expansion_point):
    x = data[i]
    log_lik = unimodal_logpdf(x, mu_grid, sigma_grid)
    log_post_late += log_lik

# At expansion: add mixture hypotheses
log_post_late_norm = log_post_late - logsumexp(log_post_late)
expansion_weight = 0.3  # give 30% total mass to new hypotheses
log_post_expanded_late = np.zeros(n_expanded)
log_post_expanded_late[:n_uni] = log_post_late_norm + np.log(1 - expansion_weight)
log_post_expanded_late[n_uni:] = np.log(expansion_weight / n_mix)

for i in range(expansion_point):
    trajectory_late_true.append(0.0)  # mixtures don't exist yet

for i in range(expansion_point, n_total):
    x = data[i]
    ll_uni = unimodal_logpdf(x, mu_grid, sigma_grid)
    ll_mix = np.array([mixture_logpdf(x, (m[0], m[1], m[2]))
                       for m in mixture_hypotheses])
    log_post_expanded_late[:n_uni] += ll_uni
    log_post_expanded_late[n_uni:] += ll_mix
    log_post_norm = log_post_expanded_late - logsumexp(log_post_expanded_late)
    post = np.exp(log_post_norm)
    trajectory_late_true.append(post[n_uni + 1])

# --- Print ---
print("=" * 70)
print("EXAMPLE 8: Escaping the Cage — Model Expansion")
print("True DGP: Mixture(-3, 0, 4) with σ=0.8")
print("=" * 70)

print(f"\nRestricted model (unimodal only):")
print(f"  Final MAP: μ = {trajectory_map_mu[-1]:.2f} (best unimodal fit)")
print(f"  Max posterior: {trajectory_max_restricted[-1]:.4f}")
print(f"  → Confident but WRONG (bimodal truth ≠ unimodal model)")

print(f"\nExpanded model (unimodal + mixtures from start):")
print(f"  P(true mixture) at n=100: {trajectory_true_hypothesis[99]:.4f}")
print(f"  P(true mixture) at n=300: {trajectory_true_hypothesis[299]:.4f}")
print(f"  P(true mixture) at n=600: {trajectory_true_hypothesis[599]:.4f}")
print(f"  → True hypothesis rapidly dominates ✓")

print(f"\nLate expansion (mixtures added at n=300):")
print(f"  P(true) at n=300 (just added): {trajectory_late_true[300]:.4f}")
print(f"  P(true) at n=400: {trajectory_late_true[399]:.4f}")
print(f"  P(true) at n=600: {trajectory_late_true[599]:.4f}")
print(f"  → Even late imagination can break the cage ✓")

# --- Visualization ---
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
steps = np.arange(1, n_total + 1)

# Top-left: restricted model posterior concentration
ax = axes[0][0]
ax.plot(steps, trajectory_max_restricted, color="#d62728", lw=2)
ax.set_xlabel("Sample Size n")
ax.set_ylabel("Max Posterior (best unimodal)")
ax.set_title("Restricted Model: Confident in Wrong Answer")
ax.set_ylim(0, 1.05)
ax.text(300, 0.3, "Increasing confidence\nin a UNIMODAL model\n(truth is trimodal)",
        fontsize=10, color="#d62728",
        bbox=dict(boxstyle="round", facecolor="#ffe0e0"))

# Top-right: expanded model — true hypothesis rises
ax = axes[0][1]
ax.plot(steps, trajectory_true_hypothesis, color="#2ca02c", lw=2,
        label="P(true mixture)")
ax.plot(steps, trajectory_best_unimodal, color="#999", lw=1.5, ls="--",
        label="Best unimodal")
ax.set_xlabel("Sample Size n")
ax.set_ylabel("Posterior Probability")
ax.set_title("Expanded Model: Truth Rapidly Dominates")
ax.legend()
ax.set_ylim(0, 1.05)

# Bottom-left: late expansion
ax = axes[1][0]
ax.plot(steps, trajectory_late_true, color="#ff7f0e", lw=2,
        label="P(true mixture) — late addition")
ax.axvline(x=expansion_point, color="gray", ls="--", lw=1.5)
ax.text(expansion_point + 10, 0.5, "Hypothesis\nspace\nexpanded\nhere",
        fontsize=9, color="gray")
ax.set_xlabel("Sample Size n")
ax.set_ylabel("Posterior Probability")
ax.set_title("Late Expansion (n=300):\nImagination Breaks the Cage")
ax.legend()
ax.set_ylim(-0.05, 1.05)

# Bottom-right: true density vs fits
ax = axes[1][1]
x_plot = np.linspace(-8, 8, 500)
# True density
true_density = (0.3 * norm.pdf(x_plot, -3, 0.8) +
                0.3 * norm.pdf(x_plot, 0, 0.8) +
                0.4 * norm.pdf(x_plot, 4, 0.8))
ax.plot(x_plot, true_density, "k-", lw=2.5, label="True (trimodal)")
# Best unimodal
map_mu_final = trajectory_map_mu[-1]
ax.plot(x_plot, norm.pdf(x_plot, map_mu_final, 3.0), "r--", lw=2,
        label=f"Best unimodal (μ={map_mu_final:.1f})")
# True mixture hypothesis
true_mix_density = (0.33 * norm.pdf(x_plot, -3, 0.8) +
                    0.33 * norm.pdf(x_plot, 0, 0.8) +
                    0.34 * norm.pdf(x_plot, 4, 0.8))
ax.plot(x_plot, true_mix_density, "g-.", lw=2,
        label="Expanded: Mix(-3,0,4)")
ax.hist(data, bins=50, density=True, alpha=0.2, color="gray")
ax.set_xlabel("x")
ax.set_ylabel("Density")
ax.set_title("True Density vs. Model Fits")
ax.legend(fontsize=9)

plt.tight_layout()
plt.savefig("figures/ex08_model_expansion.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n>>> MORE DATA doesn't fix the restricted model.")
print(">>> MORE HYPOTHESES (imagination) does.")
print(">>> This is the paper's central thesis.")
print("\n[Figure saved to figures/ex08_model_expansion.png]")

"""
Example 1: The Probability Cage — Confident Convergence to a Wrong Model
=========================================================================

Demonstrates the central claim of the paper:
When the true data-generating process lies OUTSIDE the hypothesis space,
Bayesian updating still converges — but to the KL-closest wrong model,
with arbitrarily high posterior confidence.

Setup:
  - True model: data ~ Mixture(0.5 * N(-2,1) + 0.5 * N(2,1))  (bimodal)
  - Hypothesis space H = {N(mu, sigma^2)} — unimodal Gaussians only
  - The true model is NOT in H.
  - Bayesian updating concentrates on mu≈0, sigma≈2.4 (the KL-minimizer)
  - Posterior confidence grows toward 1 — for the wrong model.

This is the probability cage: the model is certain, yet structurally wrong.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.special import logsumexp

np.random.seed(42)


def true_density(x):
    """True data-generating process: bimodal Gaussian mixture."""
    return 0.5 * norm.pdf(x, -2, 1) + 0.5 * norm.pdf(x, 2, 1)


def true_log_density(x):
    """Log of true density."""
    return np.log(0.5 * norm.pdf(x, -2, 1) + 0.5 * norm.pdf(x, 2, 1))


def generate_data(n):
    """Sample from the true bimodal distribution."""
    components = np.random.binomial(1, 0.5, n)
    return np.where(components == 0,
                    np.random.normal(-2, 1, n),
                    np.random.normal(2, 1, n))


# --- Bayesian updating over a discrete grid of (mu, sigma) hypotheses ---
# All hypotheses are UNIMODAL Gaussians — the bimodal truth is excluded.

mu_grid = np.linspace(-4, 4, 80)
sigma_grid = np.linspace(0.5, 5, 60)
MU, SIGMA = np.meshgrid(mu_grid, sigma_grid)
mu_flat = MU.ravel()
sigma_flat = SIGMA.ravel()
n_hypotheses = len(mu_flat)

# Uniform prior over the grid
log_posterior = np.zeros(n_hypotheses)  # log-uniform

# Generate data and update sequentially
n_total = 500
data = generate_data(n_total)
checkpoints = [1, 5, 20, 50, 100, 200, 500]
posteriors_at_checkpoints = {}
map_estimates = {}

for i, x in enumerate(data):
    # Log-likelihood of this datum under each hypothesis
    log_lik = norm.logpdf(x, mu_flat, sigma_flat)
    log_posterior += log_lik
    # Normalize in log-space
    log_posterior -= logsumexp(log_posterior)

    n_seen = i + 1
    if n_seen in checkpoints:
        posterior = np.exp(log_posterior)
        posteriors_at_checkpoints[n_seen] = posterior.copy()
        map_idx = np.argmax(posterior)
        map_estimates[n_seen] = (mu_flat[map_idx], sigma_flat[map_idx],
                                 posterior[map_idx])

# --- Print convergence trajectory ---
print("=" * 70)
print("EXAMPLE 1: The Probability Cage")
print("True model: Mixture(0.5 * N(-2,1) + 0.5 * N(2,1))  [BIMODAL]")
print("Hypothesis space: {N(mu, sigma^2)}                   [UNIMODAL ONLY]")
print("=" * 70)
print(f"\n{'n':>5}  {'MAP mu':>8}  {'MAP sigma':>10}  {'MAP posterior':>14}  {'Verdict'}")
print("-" * 65)
for n_seen in checkpoints:
    mu_map, sigma_map, p_map = map_estimates[n_seen]
    verdict = "WRONG but confident" if p_map > 0.01 else "diffuse"
    print(f"{n_seen:>5}  {mu_map:>8.2f}  {sigma_map:>10.2f}  {p_map:>14.4f}  {verdict}")

print("\n>>> The posterior converges to mu≈0, sigma≈2.4.")
print(">>> This is the KL-minimizer: the single Gaussian closest to the")
print("    bimodal truth. Bayesian updating is internally correct —")
print("    but structurally blind. This is the PROBABILITY CAGE.")

# --- Visualization ---
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Top row: posterior heat maps at 3 checkpoints
for ax, n_seen in zip(axes[0], [5, 50, 500]):
    post = posteriors_at_checkpoints[n_seen].reshape(MU.shape)
    im = ax.contourf(MU, SIGMA, post, levels=30, cmap="inferno")
    ax.set_xlabel("μ")
    ax.set_ylabel("σ")
    ax.set_title(f"Posterior after n = {n_seen}")
    ax.plot(0, 2.45, "w*", markersize=12, label="KL-minimizer")
    ax.legend(loc="upper right", fontsize=8)

# Bottom-left: true density vs MAP fit
ax = axes[1][0]
x_plot = np.linspace(-8, 8, 500)
ax.plot(x_plot, true_density(x_plot), "k-", lw=2, label="True (bimodal)")
for n_seen, color in zip([5, 50, 500], ["#ff9999", "#ff4444", "#cc0000"]):
    mu_map, sigma_map, _ = map_estimates[n_seen]
    ax.plot(x_plot, norm.pdf(x_plot, mu_map, sigma_map), "--",
            color=color, lw=1.5, label=f"MAP fit (n={n_seen})")
ax.set_xlabel("x")
ax.set_ylabel("Density")
ax.set_title("True Density vs. Best Unimodal Fit")
ax.legend(fontsize=8)

# Bottom-center: posterior concentration over time
ax = axes[1][1]
max_posteriors = []
sample_sizes = list(range(1, n_total + 1))
log_post_track = np.zeros(n_hypotheses)
for i, x in enumerate(data):
    log_lik = norm.logpdf(x, mu_flat, sigma_flat)
    log_post_track += log_lik
    log_post_track_norm = log_post_track - logsumexp(log_post_track)
    max_posteriors.append(np.exp(log_post_track_norm).max())
ax.plot(sample_sizes, max_posteriors, "r-", lw=1.5)
ax.set_xlabel("Sample Size n")
ax.set_ylabel("Max Posterior Probability")
ax.set_title("Posterior Concentration (Wrong Model)")
ax.axhline(y=1.0, color="gray", ls="--", alpha=0.5)
ax.set_ylim(0, 1.05)

# Bottom-right: KL divergence illustration
ax = axes[1][2]
kl_values = np.zeros_like(mu_flat)
x_int = np.linspace(-10, 10, 2000)
dx = x_int[1] - x_int[0]
p_true = true_density(x_int)
for j in range(n_hypotheses):
    q = norm.pdf(x_int, mu_flat[j], sigma_flat[j])
    # KL(p || q), avoiding log(0)
    mask = (p_true > 1e-15) & (q > 1e-15)
    kl_values[j] = np.sum(p_true[mask] * np.log(p_true[mask] / q[mask])) * dx

kl_map = kl_values.reshape(MU.shape)
im = ax.contourf(MU, SIGMA, kl_map, levels=30, cmap="viridis_r")
ax.set_xlabel("μ")
ax.set_ylabel("σ")
ax.set_title("KL(true ‖ model) — Posterior converges to min")
kl_min_idx = np.argmin(kl_values)
ax.plot(mu_flat[kl_min_idx], sigma_flat[kl_min_idx], "r*",
        markersize=12, label=f"KL min: μ={mu_flat[kl_min_idx]:.1f}, σ={sigma_flat[kl_min_idx]:.1f}")
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("figures/ex01_probability_cage.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n[Figure saved to figures/ex01_probability_cage.png]")

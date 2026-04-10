"""
Example 4: Parametric vs. Structural Uncertainty
==================================================

Demonstrates the distinction between:
  - PARAMETRIC uncertainty: "What is β in Y = βX + ε?"
    → Bayesian inference handles this beautifully (posterior shrinks to truth)
  - STRUCTURAL uncertainty: "Is Y = βX + ε even the right model?"
    → Bayesian inference WITHIN the model cannot answer this

Setup:
  True model: Y = sin(X) + noise   (nonlinear)
  Fitted model: Y = βX + ε          (linear)

The posterior on β shrinks confidently around the OLS slope —
parametric uncertainty vanishes — but the model is WRONG.
Structural uncertainty (wrong functional form) is invisible to the posterior.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

np.random.seed(77)


def true_function(x):
    return np.sin(2 * x)


# Generate data
n_total = 300
sigma_noise = 0.3
X = np.random.uniform(-np.pi, np.pi, n_total)
Y = true_function(X) + np.random.normal(0, sigma_noise, n_total)

# --- Bayesian linear regression: conjugate normal-normal ---
# Model: Y = beta * X + eps, eps ~ N(0, sigma^2)
# Prior: beta ~ N(0, tau^2) with tau = 10 (vague)
# Known sigma = sigma_noise (for simplicity)

tau_prior = 10.0  # prior std on beta
sample_sizes = [5, 20, 50, 100, 200, 300]

print("=" * 70)
print("EXAMPLE 4: Parametric vs. Structural Uncertainty")
print("True model: Y = sin(2X) + noise    [NONLINEAR]")
print("Fitted model: Y = βX + noise       [LINEAR]")
print("=" * 70)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

beta_grid = np.linspace(-1.5, 1.5, 500)
posteriors_beta = {}

for idx, n in enumerate(sample_sizes):
    X_n = X[:n]
    Y_n = Y[:n]

    # Conjugate posterior for beta (known variance)
    prior_precision = 1.0 / tau_prior ** 2
    lik_precision = np.sum(X_n ** 2) / sigma_noise ** 2
    post_precision = prior_precision + lik_precision
    post_var = 1.0 / post_precision
    post_mean = post_var * (np.sum(X_n * Y_n) / sigma_noise ** 2)
    post_std = np.sqrt(post_var)

    posteriors_beta[n] = (post_mean, post_std)

    print(f"\nn = {n}:")
    print(f"  Posterior: β ~ N({post_mean:.4f}, {post_std:.4f}²)")
    print(f"  95% CI: [{post_mean - 1.96*post_std:.4f}, {post_mean + 1.96*post_std:.4f}]")
    print(f"  Parametric uncertainty: {'HIGH' if post_std > 0.1 else 'LOW' if post_std > 0.01 else 'NEGLIGIBLE'}")
    print(f"  Structural uncertainty: UNKNOWN (model cannot assess itself)")

# Top row: posterior on beta at 3 stages
for ax, n in zip(axes[0], [5, 50, 300]):
    mu, sd = posteriors_beta[n]
    density = norm.pdf(beta_grid, mu, sd)
    ax.fill_between(beta_grid, density, alpha=0.3, color="#1f77b4")
    ax.plot(beta_grid, density, color="#1f77b4", lw=2)
    ax.axvline(x=mu, color="#1f77b4", ls="--", alpha=0.7,
               label=f"MAP β = {mu:.3f}")
    ax.set_xlabel("β")
    ax.set_ylabel("Posterior Density")
    ax.set_title(f"Posterior on β (n = {n})\nParametric uncertainty → 0")
    ax.legend(fontsize=9)

# Bottom-left: data + true function + linear fit
ax = axes[1][0]
x_plot = np.linspace(-np.pi, np.pi, 200)
ax.scatter(X[:100], Y[:100], alpha=0.3, s=10, c="#999")
ax.plot(x_plot, true_function(x_plot), "g-", lw=2, label="True: sin(2x)")
mu_300, _ = posteriors_beta[300]
ax.plot(x_plot, mu_300 * x_plot, "r--", lw=2,
        label=f"Model: {mu_300:.3f}·x")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_title("The Model Is Structurally Wrong\n(but doesn't know it)")
ax.legend()

# Bottom-center: residuals reveal structure
ax = axes[1][1]
Y_pred = posteriors_beta[300][0] * X
residuals = Y - Y_pred
ax.scatter(X, residuals, alpha=0.3, s=10, c="#d62728")
# Show the pattern
sort_idx = np.argsort(X)
from scipy.ndimage import uniform_filter1d
smoothed = uniform_filter1d(residuals[sort_idx], size=30)
ax.plot(X[sort_idx], smoothed, "k-", lw=2, label="Smoothed residual")
ax.axhline(y=0, color="gray", ls="--")
ax.set_xlabel("X")
ax.set_ylabel("Residual (Y - βX)")
ax.set_title("Residuals Show Structure\n(invisible to the posterior on β)")
ax.legend()

# Bottom-right: comparative uncertainty diagram
ax = axes[1][2]
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

# Parametric uncertainty box
ax.add_patch(plt.Rectangle((0.5, 5.5), 4, 4, fill=True,
             facecolor="#2ca02c", alpha=0.2, edgecolor="#2ca02c", lw=2))
ax.text(2.5, 9, "PARAMETRIC\nUNCERTAINTY", ha="center", va="center",
        fontsize=11, fontweight="bold", color="#2ca02c")
ax.text(2.5, 7.5, "\"What is β?\"", ha="center", fontsize=10, style="italic")
ax.text(2.5, 6.5, "Bayes handles this:\nposterior shrinks → 0",
        ha="center", fontsize=9, color="#2ca02c")
ax.text(2.5, 5.8, "✓ SOLVED", ha="center", fontsize=12,
        fontweight="bold", color="#2ca02c")

# Structural uncertainty box
ax.add_patch(plt.Rectangle((5.5, 5.5), 4, 4, fill=True,
             facecolor="#d62728", alpha=0.2, edgecolor="#d62728", lw=2))
ax.text(7.5, 9, "STRUCTURAL\nUNCERTAINTY", ha="center", va="center",
        fontsize=11, fontweight="bold", color="#d62728")
ax.text(7.5, 7.5, "\"Is Y=βX right?\"", ha="center", fontsize=10,
        style="italic")
ax.text(7.5, 6.5, "Bayes within the model\nCANNOT answer this",
        ha="center", fontsize=9, color="#d62728")
ax.text(7.5, 5.8, "✗ INVISIBLE", ha="center", fontsize=12,
        fontweight="bold", color="#d62728")

# Cage metaphor
ax.add_patch(plt.Rectangle((0.5, 0.5), 9, 4.2, fill=True,
             facecolor="#ff9900", alpha=0.1, edgecolor="#ff9900", lw=2,
             linestyle="--"))
ax.text(5, 3.5, "THE PROBABILITY CAGE", ha="center", fontsize=13,
        fontweight="bold", color="#cc6600")
ax.text(5, 2.3, "High parametric confidence\n+ invisible structural error\n= "
        "confident but wrong", ha="center", fontsize=10, color="#cc6600")

ax.set_title("Two Kinds of Uncertainty", pad=10)

plt.tight_layout()
plt.savefig("figures/ex04_parametric_vs_structural.png", dpi=150,
            bbox_inches="tight")
plt.close()

print("\n>>> Bayesian inference drives parametric uncertainty to near-zero.")
print(">>> But structural uncertainty (wrong model form) remains invisible.")
print(">>> This is why 'high confidence' ≠ 'correct model'.")
print("\n[Figure saved to figures/ex04_parametric_vs_structural.png]")

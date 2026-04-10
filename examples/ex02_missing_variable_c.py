"""
Example 2: The Missing Variable C — Confounding and Causal Misattribution
==========================================================================

Demonstrates: When an unobserved confounder C causes both A and B,
Bayesian updating in a model that only sees A and B will converge
to the false belief that A causes B.

True causal structure:    C → A,  C → B   (A and B are NOT causally linked)
Model's hypothesis space: {A→B,  B→A,  A⊥B}

The posterior concentrates on "A→B" with increasing confidence,
even though the true relationship is confounded.

Pearl (2009): "Bayesian updating cannot distinguish correlation from
causation without structural causal assumptions."
"""

import numpy as np
import matplotlib.pyplot as plt

np.random.seed(123)


def generate_confounded_data(n):
    """
    True DAG:  C → A,  C → B
    C ~ N(0, 1)
    A = 0.8*C + noise
    B = 0.7*C + noise
    A does NOT cause B. But they are correlated (r ≈ 0.56).
    """
    C = np.random.normal(0, 1, n)
    A = 0.8 * C + np.random.normal(0, 0.5, n)
    B = 0.7 * C + np.random.normal(0, 0.5, n)
    return A, B, C


def log_likelihood_causal(A, B, model):
    """
    Compute log-likelihood under three competing models:
    - 'A->B': B = beta*A + noise,  fit by OLS
    - 'B->A': A = beta*B + noise,  fit by OLS
    - 'indep': A ~ N(mu_a, s_a^2), B ~ N(mu_b, s_b^2) independently
    """
    from scipy.stats import norm as sp_norm

    n = len(A)
    if model == "A->B":
        # B = beta*A + eps, OLS fit
        beta = np.sum(A * B) / np.sum(A ** 2)
        residuals = B - beta * A
        sigma = np.std(residuals)
        if sigma < 1e-10:
            sigma = 1e-10
        ll = np.sum(sp_norm.logpdf(residuals, 0, sigma))
    elif model == "B->A":
        beta = np.sum(A * B) / np.sum(B ** 2)
        residuals = A - beta * B
        sigma = np.std(residuals)
        if sigma < 1e-10:
            sigma = 1e-10
        ll = np.sum(sp_norm.logpdf(residuals, 0, sigma))
    elif model == "indep":
        ll = (np.sum(sp_norm.logpdf(A, np.mean(A), np.std(A))) +
              np.sum(sp_norm.logpdf(B, np.mean(B), np.std(B))))
    else:
        raise ValueError(f"Unknown model: {model}")
    return ll


# --- Sequential Bayesian model comparison ---
models = ["A->B", "B->A", "indep"]
n_total = 1000
A_all, B_all, C_all = generate_confounded_data(n_total)

# Track posterior evolution
checkpoints = np.arange(10, n_total + 1, 10)
posterior_history = {m: [] for m in models}

for n in checkpoints:
    A_n = A_all[:n]
    B_n = B_all[:n]

    log_liks = {m: log_likelihood_causal(A_n, B_n, m) for m in models}

    # Uniform prior → posterior ∝ likelihood
    max_ll = max(log_liks.values())
    posteriors = {m: np.exp(log_liks[m] - max_ll) for m in models}
    total = sum(posteriors.values())
    posteriors = {m: posteriors[m] / total for m in models}

    for m in models:
        posterior_history[m].append(posteriors[m])

# --- Print results ---
print("=" * 70)
print("EXAMPLE 2: The Missing Variable C")
print("True DAG:  C → A,  C → B   (A does NOT cause B)")
print("Hypothesis space: {A→B, B→A, A⊥B}   (C is ABSENT)")
print("=" * 70)
print(f"\n{'n':>5}  {'P(A→B)':>10}  {'P(B→A)':>10}  {'P(A⊥B)':>10}  Winner")
print("-" * 55)
for idx, n in enumerate(checkpoints):
    if n in [10, 50, 100, 200, 500, 1000]:
        row_idx = list(checkpoints).index(n)
        pa = posterior_history["A->B"][row_idx]
        pb = posterior_history["B->A"][row_idx]
        pi = posterior_history["indep"][row_idx]
        winner = max(models, key=lambda m: posterior_history[m][row_idx])
        flag = " ← WRONG!" if winner != "indep" else ""
        print(f"{n:>5}  {pa:>10.4f}  {pb:>10.4f}  {pi:>10.4f}  {winner}{flag}")

print("\n>>> P(A→B) dominates despite A not causing B.")
print(">>> Without C in the model, confounding is invisible.")
print(">>> This is causal misattribution via the probability cage.")

# --- Visualization ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Left: Posterior evolution
ax = axes[0]
colors = {"A->B": "#d62728", "B->A": "#1f77b4", "indep": "#2ca02c"}
labels = {"A->B": "P(A→B) [WRONG]", "B->A": "P(B→A)", "indep": "P(A⊥B)"}
for m in models:
    ax.plot(checkpoints, posterior_history[m], color=colors[m],
            lw=2, label=labels[m])
ax.set_xlabel("Sample Size n")
ax.set_ylabel("Posterior Probability")
ax.set_title("Bayesian Model Selection\n(Confounder C is missing)")
ax.legend()
ax.set_ylim(-0.05, 1.05)
ax.axhline(y=0.5, color="gray", ls="--", alpha=0.3)

# Center: Scatter showing correlation
ax = axes[1]
ax.scatter(A_all[:200], B_all[:200], alpha=0.4, s=10, c="#333")
# Regression line
beta = np.polyfit(A_all[:200], B_all[:200], 1)
x_line = np.linspace(A_all[:200].min(), A_all[:200].max(), 100)
ax.plot(x_line, np.polyval(beta, x_line), "r-", lw=2,
        label=f"OLS: B = {beta[0]:.2f}A + {beta[1]:.2f}")
ax.set_xlabel("A")
ax.set_ylabel("B")
ax.set_title("Observed: A and B appear correlated\n(but neither causes the other)")
r = np.corrcoef(A_all[:200], B_all[:200])[0, 1]
ax.text(0.05, 0.95, f"r = {r:.3f}", transform=ax.transAxes,
        fontsize=12, va="top")
ax.legend(fontsize=9)

# Right: The true DAG vs what the model sees
ax = axes[2]
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("True Causal Structure vs. Model's View")

# True DAG
ax.text(5, 9.2, "TRUTH (unknown to model)", ha="center", fontsize=11,
        fontweight="bold", color="#2ca02c")
# C node
ax.add_patch(plt.Circle((5, 7.5), 0.6, fill=True, color="#2ca02c", alpha=0.3))
ax.text(5, 7.5, "C", ha="center", va="center", fontsize=14, fontweight="bold")
# A node
ax.add_patch(plt.Circle((3, 5.5), 0.6, fill=True, color="#aaa", alpha=0.3))
ax.text(3, 5.5, "A", ha="center", va="center", fontsize=14)
# B node
ax.add_patch(plt.Circle((7, 5.5), 0.6, fill=True, color="#aaa", alpha=0.3))
ax.text(7, 5.5, "B", ha="center", va="center", fontsize=14)
# Arrows C→A, C→B
ax.annotate("", xy=(3.45, 5.95), xytext=(4.55, 7.05),
            arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=2))
ax.annotate("", xy=(6.55, 5.95), xytext=(5.45, 7.05),
            arrowprops=dict(arrowstyle="->", color="#2ca02c", lw=2))

# Model's (wrong) conclusion
ax.text(5, 3.8, "MODEL'S CONCLUSION (wrong)", ha="center", fontsize=11,
        fontweight="bold", color="#d62728")
# A node
ax.add_patch(plt.Circle((3, 2), 0.6, fill=True, color="#aaa", alpha=0.3))
ax.text(3, 2, "A", ha="center", va="center", fontsize=14)
# B node
ax.add_patch(plt.Circle((7, 2), 0.6, fill=True, color="#aaa", alpha=0.3))
ax.text(7, 2, "B", ha="center", va="center", fontsize=14)
# Wrong arrow A→B
ax.annotate("", xy=(6.4, 2), xytext=(3.6, 2),
            arrowprops=dict(arrowstyle="->", color="#d62728", lw=3))
ax.text(5, 1.5, "A → B ???", ha="center", fontsize=12, color="#d62728",
        fontweight="bold")

plt.tight_layout()
plt.savefig("figures/ex02_missing_variable_c.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n[Figure saved to figures/ex02_missing_variable_c.png]")

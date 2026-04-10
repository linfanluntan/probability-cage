"""
Example 5: Bayesian Conservatism — Paradigm Lock-In
=====================================================

Demonstrates: Bayesian updating naturally strengthens established hypotheses
and marginalizes novel ones, even when the novel hypothesis is closer to truth.

Scenario: "Scientific paradigm shift"
  - Phase 1 (n=1..500):   True DGP is H_old (established theory works)
  - Phase 2 (n=501..1000): True DGP SHIFTS to H_new (paradigm shift!)
  - H_old has accumulated 500 data points of evidence
  - H_new starts as a low-prior underdog

Question: How long does it take Bayesian updating to "discover" the shift?
Answer: A LONG time — the accumulated posterior mass on H_old creates inertia.

This models the Kuhnian observation that paradigm shifts are resisted
because the old paradigm has overwhelming accumulated evidence.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

np.random.seed(2024)


# --- Setup ---
# H_old: data ~ N(0, 1)
# H_new: data ~ N(2, 1)
# Phase 1 (n=1..500): truth is H_old
# Phase 2 (n=501..1000): truth SHIFTS to H_new

n_phase1 = 500
n_phase2 = 500
n_total = n_phase1 + n_phase2

# Generate data
data_phase1 = np.random.normal(0, 1, n_phase1)   # from H_old
data_phase2 = np.random.normal(2, 1, n_phase2)   # from H_new (paradigm shift!)
data = np.concatenate([data_phase1, data_phase2])

# Hypotheses
mu_old, mu_new = 0.0, 2.0
sigma = 1.0

# Prior: H_old is established (prior 0.9), H_new is speculative (prior 0.1)
prior_old = 0.9
prior_new = 0.1

# --- Bayesian updating ---
log_post_old = np.log(prior_old)
log_post_new = np.log(prior_new)

trajectory_old = []
trajectory_new = []

for i, x in enumerate(data):
    ll_old = norm.logpdf(x, mu_old, sigma)
    ll_new = norm.logpdf(x, mu_new, sigma)

    log_post_old += ll_old
    log_post_new += ll_new

    # Normalize
    max_lp = max(log_post_old, log_post_new)
    denom = max_lp + np.log(np.exp(log_post_old - max_lp) +
                             np.exp(log_post_new - max_lp))
    p_old = np.exp(log_post_old - denom)
    p_new = np.exp(log_post_new - denom)

    trajectory_old.append(p_old)
    trajectory_new.append(p_new)

# Find crossover point
crossover = None
for i in range(n_phase1, n_total):
    if trajectory_new[i] > 0.5:
        crossover = i + 1
        break

# --- Print results ---
print("=" * 70)
print("EXAMPLE 5: Bayesian Conservatism — Paradigm Lock-In")
print("Phase 1 (n=1–500):    Truth = H_old (μ=0)")
print("Phase 2 (n=501–1000): Truth = H_new (μ=2)  ← PARADIGM SHIFT")
print("Prior: P(H_old) = 0.9,  P(H_new) = 0.1")
print("=" * 70)

print(f"\nAt paradigm shift (n=500):")
print(f"  P(H_old) = {trajectory_old[499]:.8f}")
print(f"  P(H_new) = {trajectory_new[499]:.8f}")
print(f"  → H_old has overwhelming accumulated evidence")

if crossover:
    delay = crossover - n_phase1
    print(f"\nCrossover (P(H_new) > 0.5) at n = {crossover}")
    print(f"  That's {delay} observations AFTER the shift occurred!")
    print(f"  → Bayesian inertia delays recognition by {delay} samples")
else:
    print(f"\nH_new never reaches >50% — the old paradigm is too entrenched!")

print(f"\nAt n=600: P(H_new) = {trajectory_new[599]:.4f}")
print(f"At n=700: P(H_new) = {trajectory_new[699]:.4f}")
print(f"At n=800: P(H_new) = {trajectory_new[799]:.4f}")
print(f"At n=1000: P(H_new) = {trajectory_new[999]:.6f}")

print("\n>>> Accumulated evidence creates 'paradigm inertia'.")
print(">>> The old theory resists replacement even after it becomes wrong.")
print(">>> This is Bayesian conservatism — rational within the framework,")
print("    but an obstacle to paradigm shifts (Kuhn, 1962).")

# --- Visualization ---
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
steps = np.arange(1, n_total + 1)

# Left: posterior trajectories
ax = axes[0]
ax.plot(steps, trajectory_old, color="#1f77b4", lw=2, label="P(H_old: μ=0)")
ax.plot(steps, trajectory_new, color="#d62728", lw=2, label="P(H_new: μ=2)")
ax.axvline(x=500, color="black", ls="--", lw=1.5, alpha=0.7)
ax.text(505, 0.85, "← Paradigm shift\n    (truth changes)", fontsize=9)
if crossover:
    ax.axvline(x=crossover, color="gray", ls=":", lw=1)
    ax.text(crossover + 5, 0.5, f"Crossover\nn={crossover}", fontsize=8,
            color="gray")
ax.fill_betweenx([0, 1], 500, 500 + (crossover - 500 if crossover else 500),
                 alpha=0.1, color="#d62728", label="Delay period")
ax.set_xlabel("Sample Size n")
ax.set_ylabel("Posterior Probability")
ax.set_title("Bayesian Conservatism:\nOld Paradigm Resists Displacement")
ax.legend(fontsize=8, loc="center right")
ax.set_ylim(-0.05, 1.05)

# Center: log posterior odds
ax = axes[1]
log_odds = np.array([np.log(trajectory_old[i] / max(trajectory_new[i], 1e-300))
                     for i in range(n_total)])
ax.plot(steps, log_odds, color="#333", lw=1.5)
ax.axhline(y=0, color="gray", ls="--", alpha=0.5)
ax.axvline(x=500, color="black", ls="--", lw=1.5, alpha=0.7)
ax.fill_between(steps[:500], log_odds[:500], alpha=0.15, color="#1f77b4",
                label="Evidence accumulates FOR H_old")
ax.fill_between(steps[500:], log_odds[500:], alpha=0.15, color="#d62728",
                label="Evidence accumulates FOR H_new")
ax.set_xlabel("Sample Size n")
ax.set_ylabel("Log Posterior Odds: log P(H_old)/P(H_new)")
ax.set_title("Log Odds: 'Evidence Mountain'\nMust Be Climbed Before Shift")
ax.legend(fontsize=8)

# Right: delay as function of prior strength
ax = axes[2]
prior_olds_test = [0.5, 0.7, 0.9, 0.95, 0.99, 0.999]
delays = []

for po in prior_olds_test:
    lpo = np.log(po)
    lpn = np.log(1 - po)
    cross = None
    for i, x in enumerate(data):
        lpo += norm.logpdf(x, mu_old, sigma)
        lpn += norm.logpdf(x, mu_new, sigma)
        mx = max(lpo, lpn)
        d = mx + np.log(np.exp(lpo - mx) + np.exp(lpn - mx))
        pn = np.exp(lpn - d)
        if i >= n_phase1 and pn > 0.5:
            cross = i + 1
            break
    delays.append(cross - n_phase1 if cross else n_phase2)

ax.bar(range(len(prior_olds_test)),
       delays,
       color=["#66b3ff", "#4499ee", "#2277cc", "#1155aa", "#003388", "#001155"],
       edgecolor="white")
ax.set_xticks(range(len(prior_olds_test)))
ax.set_xticklabels([f"{p}" for p in prior_olds_test])
ax.set_xlabel("Prior P(H_old)")
ax.set_ylabel("Delay (samples after shift)")
ax.set_title("Stronger Prior = Longer Delay\nBefore Paradigm Shift Recognized")

for i, d in enumerate(delays):
    ax.text(i, d + 3, str(d), ha="center", fontsize=10, fontweight="bold")

plt.tight_layout()
plt.savefig("figures/ex05_bayesian_conservatism.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("\n[Figure saved to figures/ex05_bayesian_conservatism.png]")

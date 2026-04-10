"""
Example 7: Black Swans — Tail Risk and the Illusion of Stability
==================================================================

Demonstrates: When rare, high-impact events are absent from historical data,
Bayesian updating produces overconfident beliefs about system stability.

Scenario: Modeling financial returns
  - True model: heavy-tailed (Student-t, df=3 → occasional extreme events)
  - Agent's model: Gaussian (light-tailed → extreme events are "impossible")
  - For 95% of observations, both models look identical
  - But the Gaussian model dramatically underestimates tail risk

After 1000 calm observations, the Bayesian agent is VERY confident
in the Gaussian model — then a "black swan" arrives.

"The turkey is fed for 1000 days and becomes more and more confident
 that the farmer loves it — until Thanksgiving." — Taleb (2007)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, t as student_t

np.random.seed(2008)  # the year of the financial crisis


# --- True DGP: Student-t with df=3 (heavy tails) ---
true_df = 3
true_scale = 1.0

# Gaussian model (agent's model)
# Both have similar center behavior but wildly different tails

n_calm = 1000    # calm period
n_crisis = 50    # crisis period with tail events

# Generate calm data (most draws from t(3) look Gaussian-ish)
data_calm = student_t.rvs(df=true_df, scale=true_scale, size=n_calm)
# Force a crisis: last 50 points include extreme events
data_crisis = student_t.rvs(df=true_df, scale=true_scale, size=n_crisis)
# Inject some truly extreme values (7-10 sigma events)
data_crisis[:5] = np.array([-8.5, 7.2, -6.1, 9.3, -7.8])

data = np.concatenate([data_calm, data_crisis])
n_total = len(data)

# --- Bayesian model comparison: Gaussian vs Student-t ---
# We compare two models by cumulative log-likelihood

cumul_ll_gaussian = np.zeros(n_total)
cumul_ll_studentt = np.zeros(n_total)

# For Gaussian, we use sigma = estimated from first 100 points
sigma_est = np.std(data[:100])

for i in range(n_total):
    cumul_ll_gaussian[i] = (cumul_ll_gaussian[i-1] if i > 0 else 0) + \
                            norm.logpdf(data[i], 0, sigma_est)
    cumul_ll_studentt[i] = (cumul_ll_studentt[i-1] if i > 0 else 0) + \
                            student_t.logpdf(data[i], df=true_df, scale=true_scale)

# Posterior (equal priors)
log_post_gauss = cumul_ll_gaussian
log_post_studt = cumul_ll_studentt

posterior_gaussian = np.zeros(n_total)
posterior_studentt = np.zeros(n_total)

for i in range(n_total):
    mx = max(log_post_gauss[i], log_post_studt[i])
    denom = mx + np.log(np.exp(log_post_gauss[i] - mx) +
                         np.exp(log_post_studt[i] - mx))
    posterior_gaussian[i] = np.exp(log_post_gauss[i] - denom)
    posterior_studentt[i] = np.exp(log_post_studt[i] - denom)

# --- Tail probability comparison ---
# P(|X| > 5) under each model
threshold = 5
p_tail_gaussian = 2 * norm.sf(threshold, 0, sigma_est)
p_tail_studentt = 2 * student_t.sf(threshold, df=true_df, scale=true_scale)

# Count actual exceedances
n_exceed = np.sum(np.abs(data) > threshold)

print("=" * 70)
print("EXAMPLE 7: Black Swans — Tail Risk and Stability Illusion")
print(f"True model: Student-t(df={true_df})   [HEAVY TAILS]")
print(f"Agent model: Gaussian(σ={sigma_est:.2f})   [LIGHT TAILS]")
print("=" * 70)

print(f"\nTail probability P(|X| > {threshold}):")
print(f"  Gaussian model:  {p_tail_gaussian:.2e}  (≈ 1 in {1/p_tail_gaussian:.0f})")
print(f"  Student-t model: {p_tail_studentt:.2e}  (≈ 1 in {1/p_tail_studentt:.0f})")
print(f"  Ratio: Student-t is {p_tail_studentt/p_tail_gaussian:.0f}× more likely to see extremes")
print(f"\n  Actual |X|>{threshold} events in data: {n_exceed}")

print(f"\nPosterior at end of calm period (n={n_calm}):")
print(f"  P(Gaussian) = {posterior_gaussian[n_calm-1]:.6f}")
print(f"  P(Student-t) = {posterior_studentt[n_calm-1]:.6f}")
print(f"  → Agent is VERY confident in Gaussian (wrong!) model")

print(f"\nPosterior after crisis (n={n_total}):")
print(f"  P(Gaussian) = {posterior_gaussian[-1]:.6f}")
print(f"  P(Student-t) = {posterior_studentt[-1]:.6f}")
if posterior_studentt[-1] > 0.5:
    print(f"  → Crisis eventually corrects the belief (but damage is done)")
else:
    print(f"  → Gaussian model STILL dominates despite extreme events!")

print("\n>>> During calm periods, Gaussian and heavy-tailed models look the same.")
print(">>> Bayesian updating concentrates on the simpler Gaussian model.")
print(">>> Tail risk is systematically underestimated — until catastrophe.")

# --- Visualization ---
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Top-left: data with crisis highlighted
ax = axes[0][0]
ax.plot(range(1, n_total + 1), data, "k-", lw=0.3, alpha=0.5)
ax.scatter(range(n_calm + 1, n_total + 1), data[n_calm:],
           c="#d62728", s=5, alpha=0.7, zorder=5)
ax.axvline(x=n_calm, color="red", ls="--", lw=1.5, alpha=0.7)
ax.text(n_calm + 10, max(data) * 0.9, "← Crisis begins", color="red",
        fontsize=10)
ax.axhline(y=threshold, color="orange", ls=":", alpha=0.5)
ax.axhline(y=-threshold, color="orange", ls=":", alpha=0.5)
ax.set_xlabel("Observation")
ax.set_ylabel("Value")
ax.set_title("Data: 1000 Calm + 50 Crisis Observations")

# Top-right: posterior evolution
ax = axes[0][1]
steps = np.arange(1, n_total + 1)
ax.plot(steps, posterior_gaussian, color="#1f77b4", lw=2, label="P(Gaussian)")
ax.plot(steps, posterior_studentt, color="#d62728", lw=2, label="P(Student-t)")
ax.axvline(x=n_calm, color="red", ls="--", lw=1.5, alpha=0.7)
ax.set_xlabel("Sample Size n")
ax.set_ylabel("Posterior Probability")
ax.set_title("Model Posterior: Gaussian Dominates\nUntil Black Swans Arrive")
ax.legend()
ax.set_ylim(-0.05, 1.05)

# Bottom-left: density comparison (log scale to show tails)
ax = axes[1][0]
x_plot = np.linspace(-10, 10, 1000)
ax.semilogy(x_plot, norm.pdf(x_plot, 0, sigma_est), "#1f77b4", lw=2,
            label="Gaussian")
ax.semilogy(x_plot, student_t.pdf(x_plot, df=true_df, scale=true_scale),
            "#d62728", lw=2, label="Student-t(df=3)")
ax.axvline(x=threshold, color="orange", ls=":", alpha=0.5)
ax.axvline(x=-threshold, color="orange", ls=":", alpha=0.5)
ax.fill_between(x_plot[x_plot > threshold],
                norm.pdf(x_plot[x_plot > threshold], 0, sigma_est),
                alpha=0.3, color="#1f77b4")
ax.fill_between(x_plot[x_plot > threshold],
                student_t.pdf(x_plot[x_plot > threshold], df=true_df,
                              scale=true_scale),
                alpha=0.3, color="#d62728")
ax.set_xlabel("x")
ax.set_ylabel("Density (log scale)")
ax.set_title("Density: Nearly Identical Center,\nWildly Different Tails")
ax.legend()
ax.set_ylim(1e-8, 1)

# Bottom-right: "Turkey problem" illustration
ax = axes[1][1]
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")
ax.set_title("The Turkey Problem (Taleb, 2007)", fontsize=12)

# Confidence trajectory
days = np.linspace(0.5, 8.5, 100)
confidence = 1 - np.exp(-days * 0.5)
ax.plot(days[:90], confidence[:90] * 8 + 1, "b-", lw=3)
ax.plot(days[89:91], [confidence[89] * 8 + 1, 1], "r-", lw=3)
ax.text(4, 8.5, "Turkey's confidence\nin farmer's benevolence",
        ha="center", fontsize=10, color="#1f77b4")
ax.text(8.5, 0.5, "Day\n1001", ha="center", fontsize=10,
        color="#d62728", fontweight="bold")
ax.annotate("Thanksgiving", xy=(8.5, 1.5), fontsize=11,
            color="#d62728", fontweight="bold", ha="center")
ax.text(5, 5, "\"1000 days of evidence\ncannot predict day 1001\nif the model is wrong\"",
        ha="center", fontsize=10, style="italic",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

plt.tight_layout()
plt.savefig("figures/ex07_black_swans.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n[Figure saved to figures/ex07_black_swans.png]")

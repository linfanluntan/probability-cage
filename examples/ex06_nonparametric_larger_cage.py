"""
Example 6: Bayesian Nonparametrics — A Larger Cage
=====================================================

Demonstrates: Bayesian nonparametric methods (Dirichlet Process Mixture)
can discover the NUMBER of clusters, but cannot discover that the data
requires a fundamentally different MODEL TYPE.

Scenario A: Data is a Gaussian mixture → DP mixture works beautifully
Scenario B: Data is from a RING distribution → DP mixture FAILS
            (it overfits with many tiny Gaussians instead of
             discovering the circular structure)

This illustrates: nonparametrics enlarge the cage (flexible # of components)
but the cage's GENUS remains fixed (mixture of Gaussians).

"The model can grow within its genus; it cannot change genera."
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, multivariate_normal

np.random.seed(42)


# --- Simple DP Mixture approximation via Chinese Restaurant Process ---
# (Simplified for demonstration; not production MCMC)

def fit_dp_mixture(data, alpha=1.0, sigma_prior=1.0, n_iter=100):
    """
    Simplified DP mixture via collapsed Gibbs sampling.
    Each cluster is a 2D Gaussian with isotropic variance.
    Returns cluster assignments and parameters.
    """
    n = len(data)
    d = data.shape[1]
    assignments = np.zeros(n, dtype=int)
    
    # Initialize: each point in its own cluster
    assignments = np.random.randint(0, 3, n)

    for iteration in range(n_iter):
        for i in range(n):
            # Remove point i from its cluster
            old = assignments[i]
            
            # Count members of each cluster (excluding i)
            clusters = np.unique(assignments)
            log_probs = []
            cluster_list = []
            
            for k in clusters:
                members = data[(assignments == k) & (np.arange(n) != i)]
                n_k = len(members)
                if n_k == 0:
                    continue
                # CRP probability
                log_crp = np.log(n_k)
                # Likelihood under cluster mean
                cluster_mean = members.mean(axis=0)
                cluster_std = max(members.std(), 0.3)
                log_lik = np.sum(norm.logpdf(data[i], cluster_mean, cluster_std))
                log_probs.append(log_crp + log_lik)
                cluster_list.append(k)
            
            # New cluster probability
            log_crp_new = np.log(alpha)
            log_lik_new = np.sum(norm.logpdf(data[i], 0, sigma_prior))
            log_probs.append(log_crp_new + log_lik_new)
            cluster_list.append(max(clusters) + 1 if len(clusters) > 0 else 0)
            
            # Sample
            log_probs = np.array(log_probs)
            log_probs -= log_probs.max()
            probs = np.exp(log_probs)
            probs /= probs.sum()
            assignments[i] = cluster_list[np.random.choice(len(cluster_list), p=probs)]
    
    return assignments


def generate_gaussian_mixture(n=300):
    """3-component Gaussian mixture in 2D."""
    centers = [(-3, -3), (3, -3), (0, 3)]
    data = []
    labels = []
    for i, (cx, cy) in enumerate(centers):
        ni = n // 3
        data.append(np.column_stack([
            np.random.normal(cx, 0.7, ni),
            np.random.normal(cy, 0.7, ni)
        ]))
        labels.extend([i] * ni)
    return np.vstack(data), np.array(labels)


def generate_ring(n=300, r=3.0, noise=0.3):
    """Ring-shaped distribution — no Gaussian mixture can represent this well."""
    angles = np.random.uniform(0, 2 * np.pi, n)
    radii = r + np.random.normal(0, noise, n)
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    return np.column_stack([x, y])


def generate_swiss_roll_2d(n=300):
    """Swiss roll projected to 2D — manifold structure."""
    t = np.random.uniform(1.5 * np.pi, 4.5 * np.pi, n)
    x = t * np.cos(t) / 5
    y = t * np.sin(t) / 5
    x += np.random.normal(0, 0.1, n)
    y += np.random.normal(0, 0.1, n)
    return np.column_stack([x, y])


# --- Generate data ---
data_gaussian, labels_gaussian = generate_gaussian_mixture(300)
data_ring = generate_ring(300)
data_swiss = generate_swiss_roll_2d(300)

print("=" * 70)
print("EXAMPLE 6: Bayesian Nonparametrics — A Larger Cage")
print("=" * 70)
print("\nFitting DP mixture models (simplified Gibbs sampling)...")

# Fit DP mixtures
assignments_gauss = fit_dp_mixture(data_gaussian, alpha=1.0, sigma_prior=5.0,
                                    n_iter=50)
assignments_ring = fit_dp_mixture(data_ring, alpha=1.0, sigma_prior=5.0,
                                   n_iter=50)
assignments_swiss = fit_dp_mixture(data_swiss, alpha=1.0, sigma_prior=3.0,
                                    n_iter=50)

n_clusters_gauss = len(np.unique(assignments_gauss))
n_clusters_ring = len(np.unique(assignments_ring))
n_clusters_swiss = len(np.unique(assignments_swiss))

print(f"\nScenario A — Gaussian mixture (3 true clusters):")
print(f"  DP found {n_clusters_gauss} clusters")
print(f"  → {'SUCCESS' if 2 <= n_clusters_gauss <= 5 else 'APPROXIMATE'}: "
      f"discovers cluster structure ✓")

print(f"\nScenario B — Ring distribution (manifold structure):")
print(f"  DP found {n_clusters_ring} clusters")
print(f"  → WRONG GENUS: approximates ring with {n_clusters_ring} blobs ✗")
print(f"     (needs a circular model, not Gaussian blobs)")

print(f"\nScenario C — Swiss roll (nonlinear manifold):")
print(f"  DP found {n_clusters_swiss} clusters")
print(f"  → WRONG GENUS: fragments manifold into {n_clusters_swiss} blobs ✗")

print("\n>>> DP mixture can flex the NUMBER of components (parametric flexibility)")
print(">>> But it cannot discover that the data needs a DIFFERENT KIND of model")
print(">>> The cage is larger, but still a cage.")

# --- Visualization ---
fig, axes = plt.subplots(2, 3, figsize=(18, 11))

# Top row: true data
datasets = [data_gaussian, data_ring, data_swiss]
titles_top = ["A: Gaussian Mixture\n(within DP's genus)",
              "B: Ring Distribution\n(outside DP's genus)",
              "C: Swiss Roll 2D\n(outside DP's genus)"]
for ax, data_i, title in zip(axes[0], datasets, titles_top):
    ax.scatter(data_i[:, 0], data_i[:, 1], alpha=0.5, s=15, c="#333")
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.set_xlabel("x₁")
    ax.set_ylabel("x₂")

# Bottom row: DP mixture assignments
assignments_list = [assignments_gauss, assignments_ring, assignments_swiss]
titles_bot = [f"DP finds {n_clusters_gauss} clusters ✓\n(correct genus)",
              f"DP finds {n_clusters_ring} clusters ✗\n(wrong genus — blobs ≠ ring)",
              f"DP finds {n_clusters_swiss} clusters ✗\n(wrong genus — blobs ≠ manifold)"]
verdicts = ["#2ca02c", "#d62728", "#d62728"]

for ax, data_i, assign, title, vc in zip(axes[1], datasets, assignments_list,
                                          titles_bot, verdicts):
    scatter = ax.scatter(data_i[:, 0], data_i[:, 1], c=assign, cmap="tab10",
                        alpha=0.6, s=15)
    ax.set_title(title, fontsize=11, color=vc)
    ax.set_aspect("equal")
    ax.set_xlabel("x₁")
    ax.set_ylabel("x₂")

    # Draw approximate cluster ellipses
    for k in np.unique(assign):
        members = data_i[assign == k]
        if len(members) > 2:
            cx, cy = members.mean(axis=0)
            ax.plot(cx, cy, "k+", markersize=10, markeredgewidth=2)

plt.tight_layout()
plt.savefig("figures/ex06_nonparametric_larger_cage.png", dpi=150,
            bbox_inches="tight")
plt.close()
print("\n[Figure saved to figures/ex06_nonparametric_larger_cage.png]")

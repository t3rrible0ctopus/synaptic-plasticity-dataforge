"""
Automated checks for the Hebbian memory model.

Run with: python test_model.py

These aren't fancy — no pytest dependency, just plain asserts — but they
turn "I eyeballed some printed numbers once" into something you can
re-run instantly and point to during the live defense if a judge asks
"how do you know this actually works?"
"""

from hebbian_core import HebbianMemory
from experiments import (
    run_preset, run_neuron_pool_sweep, VOCAB, PRESETS,
    fit_bump_by_grid_search,
)

PASS = "PASS"
FAIL = "FAIL"
results = []


def check(name: str, condition: bool, detail: str = ""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


# ---------------------------------------------------------------------
# 1. Basic sanity: an untouched network has zero association everywhere.
# ---------------------------------------------------------------------
mem = HebbianMemory(n_neurons=30, decay=0.08, learning_rate=0.4)
initial_strength = mem.association_strength(VOCAB["cat"], VOCAB["meow"])
check(
    "Fresh network has zero association before any input",
    initial_strength == 0.0,
    f"got {initial_strength}",
)

# ---------------------------------------------------------------------
# 2. The core claim: learning raises association, interference lowers it.
# ---------------------------------------------------------------------
data = run_preset("learn_then_forget")
curve = [s["associations"]["cat-meow"] for s in data["steps"]]
peak = max(curve)
final = curve[-1]

check(
    "Repeated pairing raises cat-meow association above zero",
    peak > 5.0,
    f"peak={peak:.2f}",
)
check(
    "Association decays after interference (core claim)",
    final < peak,
    f"peak={peak:.2f}, final={final:.2f}",
)

# ---------------------------------------------------------------------
# 3. Control case: without interference, association should NOT drop
#    the same way — this is what proves the drop above is caused by
#    interference specifically, not passive time-based decay alone.
# ---------------------------------------------------------------------
control_data = run_preset("reinforced_control")
control_curve = [s["associations"]["cat-meow"] for s in control_data["steps"]]
control_final = control_curve[-1]
control_peak = max(control_curve)

check(
    "Control (no interference) stays near its peak, unlike the interference case",
    control_final > 0.85 * control_peak,
    f"peak={control_peak:.2f}, final={control_final:.2f} "
    f"({control_final / control_peak:.0%} retained)",
)

interference_retention = final / peak
control_retention = control_final / control_peak
check(
    "Interference causes MORE forgetting than the no-interference control",
    interference_retention < control_retention,
    f"interference retained {interference_retention:.0%}, "
    f"control retained {control_retention:.0%}",
)

# ---------------------------------------------------------------------
# 4. Competing associations: neither pair gets a "protected slot".
# ---------------------------------------------------------------------
comp_data = run_preset("competing_associations")
cat_meow_curve = [s["associations"]["cat-meow"] for s in comp_data["steps"]]
dog_bark_curve = [s["associations"]["dog-bark"] for s in comp_data["steps"]]

check(
    "Both competing pairs are learned (both reach a real peak)",
    max(cat_meow_curve) > 5.0 and max(dog_bark_curve) > 5.0,
    f"cat-meow peak={max(cat_meow_curve):.2f}, dog-bark peak={max(dog_bark_curve):.2f}",
)
check(
    "Both competing pairs degrade under shared interference",
    cat_meow_curve[-1] < max(cat_meow_curve) and dog_bark_curve[-1] < max(dog_bark_curve),
)

# ---------------------------------------------------------------------
# 5. Theoretical model validation: should fit well at normal neuron count.
# ---------------------------------------------------------------------
actual = [s["associations"]["cat-meow"] for s in data["steps"]]
bump, predicted = fit_bump_by_grid_search(
    actual, data["sequence"], ("cat", "meow"), data["params"]["decay"]
)
mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)
check(
    "Simple theoretical model tracks the real simulation reasonably well at n_neurons=30",
    mse < 5.0,
    f"MSE={mse:.2f}",
)

# ---------------------------------------------------------------------
# 6. Neuron pool sweep: shrinking the pool should make the theory WORSE
#    (this is the "collision" story — the divergence is real, not a fluke).
# ---------------------------------------------------------------------
sweep = run_neuron_pool_sweep()
mse_by_n = {r["n_neurons"]: r["theory_mse"] for r in sweep["sweep"]}
smallest_n = min(mse_by_n)
largest_n = max(mse_by_n)

check(
    "Smallest neuron pool has worse theory-fit than the largest pool",
    mse_by_n[smallest_n] > mse_by_n[largest_n],
    f"n={smallest_n} -> MSE={mse_by_n[smallest_n]:.2f}, "
    f"n={largest_n} -> MSE={mse_by_n[largest_n]:.2f}",
)
check(
    "Theory-fit error is roughly monotonic-ish across the sweep "
    "(smallest pool is the single worst)",
    mse_by_n[smallest_n] == max(mse_by_n.values()),
)

# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------
n_fail = sum(1 for status, _, _ in results if status == FAIL)
print(f"\n{len(results) - n_fail}/{len(results)} checks passed.")
if n_fail:
    print(f"{n_fail} FAILED — fix before demo day.")
    raise SystemExit(1)
else:
    print("All checks passed — the claim holds under these parameters.")
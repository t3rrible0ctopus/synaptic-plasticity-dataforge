"""
Presets and experiments built on top of hebbian_core.HebbianMemory.

This is what Division 2 (frontend) and Division 3 (research/writing) should
actually pull data from — it wraps the raw model with readable words instead
of bare integer IDs, and produces per-step association-strength time series
that are far more useful for a live chart than a single before/after number.
"""

import json
from hebbian_core import HebbianMemory

# --- Vocabulary -------------------------------------------------------
# Small, readable word set. IDs are arbitrary but fixed, since
# activation_for_symbol() is a deterministic function of the ID.
VOCAB = {
    "cat": 1, "meow": 2,          # a "real" pair we want the network to learn
    "dog": 3, "bark": 4,          # a second, competing pair
    "car": 10, "tree": 11, "cloud": 12, "phone": 13,
    "shoe": 14, "lamp": 15, "rain": 16, "book": 17,  # interference/filler
}
NAME_BY_ID = {v: k for k, v in VOCAB.items()}


def words_to_ids(words: list[str]) -> list[int]:
    return [VOCAB[w] for w in words]


# --- Presets ------------------------------------------------------------
# Each preset is a (name, description, word_sequence, tracked_pairs) tuple.
# tracked_pairs: list of (word_a, word_b) whose association strength we log
# at every single step, so the frontend can plot a live curve, not just
# a before/after snapshot.

PRESETS = {
    "learn_then_forget": {
        "description": (
            "cat/meow are paired repeatedly (learning), then a run of "
            "unrelated filler words plays (interference). Watch the cat-meow "
            "association rise, then decay."
        ),
        "sequence": ["cat", "meow"] * 6 + ["car", "tree", "cloud", "phone",
                                            "shoe", "lamp", "rain", "book"],
        "tracked_pairs": [("cat", "meow")],
    },
    "reinforced_control": {
        "description": (
            "CONTROL CASE: cat/meow are paired continuously with no "
            "interference at all. This isolates decay-from-disuse vs "
            "decay-from-interference -- association should stay high here, "
            "which is what makes the first preset's drop meaningful rather "
            "than just 'everything decays no matter what'."
        ),
        "sequence": ["cat", "meow"] * 14,
        "tracked_pairs": [("cat", "meow")],
    },
    "competing_associations": {
        "description": (
            "Two separate pairs (cat/meow and dog/bark) are each learned, "
            "then filler interference plays. Shows that multiple "
            "associations can coexist in the same synapse matrix, and both "
            "degrade under interference -- there's no dedicated 'slot' "
            "protecting either one."
        ),
        "sequence": (["cat", "meow"] * 4 + ["dog", "bark"] * 4
                     + ["car", "tree", "cloud", "phone", "shoe", "lamp"]),
        "tracked_pairs": [("cat", "meow"), ("dog", "bark")],
    },
}


def theoretical_expected_curve(sequence: list[str], pair: tuple[str, str],
                                decay: float, bump: float) -> list[float]:
    """
    A simplified closed-form APPROXIMATION of expected association strength
    over time, for the "truth beside estimate" comparison the design
    standards ask for.

    Model: strength decays by `decay` fraction every step, and jumps up by
    a fixed `bump` on any step where the pair actually co-occurs adjacently
    in the sequence (word[i] and word[i-1] are the two tracked words, in
    either order). This is a deliberately simple textbook-style model --
    real Hebbian dynamics (which involve a decaying multi-step trace, not
    just adjacent pairs) are messier. Comparing this simple curve against
    the real simulation is itself part of the lesson: where they diverge
    tells you something real about the mechanism.
    """
    a, b = pair
    strength = 0.0
    curve = []
    for i, word in enumerate(sequence):
        reinforced = i > 0 and {sequence[i - 1], word} == {a, b}
        if reinforced:
            strength = strength * (1 - decay) + bump
        else:
            strength = strength * (1 - decay)
        curve.append(strength)
    return curve


def fit_bump_by_grid_search(actual: list[float], sequence: list[str],
                             pair: tuple[str, str], decay: float) -> tuple[float, list[float]]:
    """
    Finds the bump size that makes the simple theoretical curve best match
    the actual simulated curve (least squares), searched over a coarse
    grid. This keeps the comparison honest: we're not hand-picking a bump
    to make them look identical, we're finding the single best-fit
    constant and then showing wherever it still doesn't track.
    """
    best_bump, best_mse, best_curve = None, float("inf"), None
    for bump in [x * 0.5 for x in range(1, 41)]:  # 0.5 .. 20.0
        curve = theoretical_expected_curve(sequence, pair, decay, bump)
        mse = sum((a - c) ** 2 for a, c in zip(actual, curve)) / len(actual)
        if mse < best_mse:
            best_bump, best_mse, best_curve = bump, mse, curve
    return best_bump, best_curve


def validate_theoretical_model(preset_name: str, pair: tuple[str, str]):
    """
    Runs a preset, fits the simple theoretical model to it, and prints
    actual vs. predicted side by side so you can see exactly where the
    simple model tracks reality and where it doesn't.
    """
    data = run_preset(preset_name)
    pair_key = f"{pair[0]}-{pair[1]}"
    actual = [s["associations"][pair_key] for s in data["steps"]]
    decay = data["params"]["decay"]

    bump, predicted = fit_bump_by_grid_search(actual, data["sequence"], pair, decay)

    print(f"\n=== Validating theoretical model: {preset_name} ({pair_key}) ===")
    print(f"Best-fit bump = {bump:.2f} (decay = {decay}, taken from actual model params)")
    print(f"{'step':>4} {'symbol':>8} {'actual':>10} {'predicted':>10} {'gap':>8}")
    for i, (sym, act, pred) in enumerate(zip(data["sequence"], actual, predicted)):
        gap = act - pred
        flag = "  <-- diverges" if abs(gap) > 5 else ""
        print(f"{i:>4} {sym:>8} {act:>10.3f} {pred:>10.3f} {gap:>8.3f}{flag}")

    mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)
    print(f"\nMSE: {mse:.3f}")
    return actual, predicted


def run_preset(name: str, n_neurons: int = 30, decay: float = 0.08,
               learning_rate: float = 0.4) -> dict:
    """
    Runs one preset through the model, logging association strength for
    every tracked pair at every single step (not just before/after).
    Returns a dict ready to serialize to JSON for the frontend.
    """
    preset = PRESETS[name]
    mem = HebbianMemory(n_neurons=n_neurons, decay=decay, learning_rate=learning_rate)

    ids = words_to_ids(preset["sequence"])
    steps_log = []

    for i, symbol_id in enumerate(ids):
        mem.step(symbol_id)
        assoc_snapshot = {
            f"{a}-{b}": mem.association_strength(VOCAB[a], VOCAB[b])
            for (a, b) in preset["tracked_pairs"]
        }
        steps_log.append({
            "step": i,
            "symbol": NAME_BY_ID[symbol_id],
            "associations": assoc_snapshot,
        })

    return {
        "name": name,
        "description": preset["description"],
        "sequence": preset["sequence"],
        "tracked_pairs": [f"{a}-{b}" for (a, b) in preset["tracked_pairs"]],
        "steps": steps_log,
        "params": {"n_neurons": n_neurons, "decay": decay, "learning_rate": learning_rate},
    }


def run_neuron_pool_sweep(preset_name: str = "learn_then_forget",
                           pair: tuple[str, str] = ("cat", "meow"),
                           neuron_counts: list[int] = None) -> dict:
    """
    Runs the same preset across a range of neuron-pool sizes, and for each
    one, fits the simple theoretical model and records how well it tracks
    reality (MSE). This is precomputed on purpose -- per the design
    standards, expensive results should be computed ahead of time and
    shipped as data, so a frontend slider can respond in under a second
    by just looking up the nearest precomputed value instead of re-running
    the simulation live.

    Tells the story: small neuron pools cause representation collisions
    between UNRELATED words, which makes the simple "each association is
    independent" theory increasingly wrong -- a second, distinct
    falsifiable moment beyond the basic learn/forget effect.
    """
    if neuron_counts is None:
        neuron_counts = [6, 8, 10, 15, 20, 30, 50, 80]

    preset = PRESETS[preset_name]
    pair_key = f"{pair[0]}-{pair[1]}"
    results = []

    for n in neuron_counts:
        data = run_preset(preset_name, n_neurons=n)
        actual = [s["associations"][pair_key] for s in data["steps"]]
        bump, predicted = fit_bump_by_grid_search(
            actual, data["sequence"], pair, data["params"]["decay"]
        )
        mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)
        results.append({
            "n_neurons": n,
            "sparsity": 3,
            "pct_active": round(3 / n * 100, 1),
            "final_association": actual[-1],
            "peak_association": max(actual),
            "theory_mse": round(mse, 3),
            "curve": actual,  # full curve too, in case frontend wants to plot it
        })

    return {
        "preset": preset_name,
        "pair": pair_key,
        "description": (
            "Same learn-then-interfere sequence run across different "
            "neuron pool sizes. As the pool shrinks, unrelated words "
            "increasingly share neurons by chance, and the simple "
            "theoretical prediction gets worse (higher theory_mse) even "
            "though the real Hebbian mechanism keeps working correctly."
        ),
        "sweep": results,
    }



def run_all_presets_and_export(path: str = "presets_export.json"):
    all_data = {name: run_preset(name) for name in PRESETS}
    with open(path, "w") as f:
        json.dump(all_data, f, indent=2)
    return all_data


def print_summary(all_data: dict):
    for name, data in all_data.items():
        print(f"\n=== {name} ===")
        print(data["description"])
        for pair in data["tracked_pairs"]:
            values = [s["associations"][pair] for s in data["steps"]]
            print(f"  {pair}: start={values[0]:.3f}  peak={max(values):.3f}  "
                  f"end={values[-1]:.3f}")


if __name__ == "__main__":
    data = run_all_presets_and_export()
    print_summary(data)
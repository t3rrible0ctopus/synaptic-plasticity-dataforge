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


def theoretical_expected_curve(n_steps: int, lr: float, decay: float,
                                trace_decay: float, reinforce_every: int | None) -> list[float]:
    """
    A simple closed-form APPROXIMATION of expected association strength
    over time, for the "truth beside estimate" comparison the design
    standards ask for. This is intentionally a simplified model (assumes
    a fixed per-reinforcement bump and constant per-step decay) -- label
    it clearly as an approximation in the UI, not as ground truth.

    reinforce_every: if the pair is reinforced every step, pass 1.
                      if reinforced every other step (interleaved with
                      something else), pass 2. Pass None once
                      reinforcement stops (pure decay phase).
    """
    strength = 0.0
    curve = []
    bump = lr * trace_decay  # rough per-reinforcement increment
    for step in range(n_steps):
        if reinforce_every is not None and step % reinforce_every == 0:
            strength = strength * (1 - decay) + bump
        else:
            strength = strength * (1 - decay)
        curve.append(strength)
    return curve


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
"""
Toy Hebbian Synaptic Plasticity model.

CLAIM THIS DEMO TESTS:
"A network can retain information about which items recently co-occurred
using only synapse-strength changes, without a dedicated memory slot per
item — but this memory degrades and can be overwritten as the sequence
continues (interference)."

This is a deliberately tiny, illustrative toy model. It is NOT a
reproduction of BDH and is not claimed to be. It exists to make the
*mechanism* (Hebbian strengthening + decay as a form of working memory)
concrete and manipulable, before connecting it to the real BDH mechanism
(see bdh_module.md / your README for the primary-source mapping).
"""

import numpy as np
import json


class HebbianMemory:
    def __init__(self, n_neurons: int, decay: float = 0.05, learning_rate: float = 0.3, seed: int = 0):
        """
        n_neurons: size of the toy neuron population
        decay: how fast synapse strength fades per step when NOT reinforced
               (this is what makes the memory "short-term")
        learning_rate: how much a co-activation strengthens a synapse
        """
        self.n = n_neurons
        self.decay = decay
        self.lr = learning_rate
        self.rng = np.random.default_rng(seed)

        # Synapse weight matrix: W[i, j] = strength of connection from neuron i -> j
        # Starts at zero: no prior associations.
        self.W = np.zeros((n_neurons, n_neurons))

        # Recent-activity trace: a short-lived echo of which neurons fired
        # recently. This is what lets Hebbian learning link things that fire
        # CLOSE IN TIME (like symbol A then symbol B), not just in the exact
        # same instant -- which is what "fire together, wire together"
        # actually means for a sequence of discrete tokens.
        self.trace = np.zeros(n_neurons)
        self.trace_decay = 0.5  # how fast the recent-activity echo fades

        # History of full weight matrices, one snapshot per processed token.
        # This is what the frontend visualization will read.
        self.history = []

    def activation_for_symbol(self, symbol_id: int, sparsity: int = 3) -> np.ndarray:
        """
        Maps an input symbol to a sparse activation pattern over neurons.
        Sparse + non-negative activation mirrors BDH's own reported property
        (~5% of neurons active at once) — this is an intentional design choice,
        not an arbitrary implementation detail.
        """
        rng = np.random.default_rng(symbol_id)  # deterministic per symbol
        active_idx = rng.choice(self.n, size=sparsity, replace=False)
        a = np.zeros(self.n)
        a[active_idx] = 1.0
        return a

    def step(self, symbol_id: int) -> np.ndarray:
        """
        Process one input token/symbol:
        1. Compute which neurons activate for this symbol.
        2. Apply Hebbian update: co-active neuron pairs get a stronger synapse.
        3. Apply decay to ALL synapses (this is what causes forgetting).
        """
        a = self.activation_for_symbol(symbol_id)

        # Hebbian update: links the CURRENT activation to the recent trace
        # (echo of what fired a step or two ago). This is what lets
        # "A then B" become an association, not just "A and B at the exact
        # same instant".
        hebbian_update = np.outer(self.trace, a) * self.lr
        hebbian_update = hebbian_update + hebbian_update.T  # symmetric association
        np.fill_diagonal(hebbian_update, 0)  # no self-synapses

        self.W = self.W * (1 - self.decay) + hebbian_update

        # Update the trace: fade old activity, add in what just fired.
        self.trace = self.trace * self.trace_decay + a

        self.history.append(self.W.copy())
        return a

    def run_sequence(self, symbol_ids: list[int]):
        for s in symbol_ids:
            self.step(s)

    def association_strength(self, symbol_a: int, symbol_b: int) -> float:
        """
        Query: how strongly does the network currently associate symbol_a
        with symbol_b? This is the 'recall' test — computed purely from
        current synapse state, no separate memory lookup table involved.
        """
        act_a = self.activation_for_symbol(symbol_a)
        act_b = self.activation_for_symbol(symbol_b)
        # Strength = how much A's active neurons connect into B's active neurons
        return float(act_a @ self.W @ act_b)

    def export_history(self, path: str):
        """Dump weight history as JSON for the frontend to visualize."""
        data = {
            "n_neurons": self.n,
            "decay": self.decay,
            "learning_rate": self.lr,
            "history": [w.tolist() for w in self.history],
        }
        with open(path, "w") as f:
            json.dump(data, f)


def demo_forgetting_experiment():
    """
    This is the core falsifiable test:
    - Show symbols A and B together repeatedly -> association should strengthen.
    - Then show a bunch of UNRELATED symbols (interference).
    - Show association between A and B has decayed / been partially overwritten.

    If association_strength(A, B) does NOT decay after interference,
    the claim as stated would be falsified for this toy model.
    """
    mem = HebbianMemory(n_neurons=30, decay=0.08, learning_rate=0.4)

    SYMBOL_A, SYMBOL_B = 1, 2
    INTERFERENCE_SYMBOLS = [10, 11, 12, 13, 14, 15, 16, 17]

    print("Phase 1: Repeatedly co-present A and B")
    for _ in range(6):
        mem.step(SYMBOL_A)
        mem.step(SYMBOL_B)
    strength_after_learning = mem.association_strength(SYMBOL_A, SYMBOL_B)
    print(f"  A-B association strength: {strength_after_learning:.4f}")

    print("Phase 2: Present unrelated interference symbols")
    for s in INTERFERENCE_SYMBOLS:
        mem.step(s)
    strength_after_interference = mem.association_strength(SYMBOL_A, SYMBOL_B)
    print(f"  A-B association strength: {strength_after_interference:.4f}")

    print()
    if strength_after_interference < strength_after_learning:
        print("CLAIM SUPPORTED: association decayed after interference.")
    else:
        print("CLAIM NOT SUPPORTED with these parameters — try increasing decay "
              "or the number of interference steps.")

    mem.export_history("weight_history.json")
    print("\nExported weight_history.json for frontend visualization.")

    return mem


if __name__ == "__main__":
    demo_forgetting_experiment()
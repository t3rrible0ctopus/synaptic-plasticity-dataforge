# Model Notes — for README / BDH module / one-page summary

Handoff doc from Division 1 (core model) to Division 3 (writing/research).
Everything here is defensible — these are the actual mechanics, not
marketing language.

## The one-sentence claim

"A network can retain information about which items recently co-occurred
using only synapse-strength changes, without a dedicated memory slot per
item — but this memory degrades and can be overwritten as the sequence
continues (interference)."

## How the toy model works (mechanism, plain language)

- **Neurons, not tokens.** Each input word is mapped to a small, fixed
  set of "active" neurons out of a larger pool (e.g. 3 active out of 30).
  This is deliberately sparse and non-negative — mirrors BDH's own
  reported property of ~5% neuron activity, not an arbitrary choice.
- **No lookup table.** There is no dictionary anywhere in the model that
  stores "cat is linked to meow." The only thing that exists is a grid of
  connection strengths between neurons (the synapse matrix). Memory of
  the cat–meow relationship is *entirely* encoded as elevated numbers in
  that grid, in the same neurons that light up for "cat" and "meow."
- **Learning rule (Hebbian):** whenever a word's neurons fire shortly
  after another word's neurons fired, the connection between those two
  neuron groups is strengthened. This is implemented via a short "recent
  activity trace" so it captures "A then B," not just "A and B at the
  exact same instant."
- **Forgetting rule (decay):** on *every single step*, all connections in
  the grid shrink slightly, whether relevant to what just happened or
  not. This is what makes memory "short-term" — nothing is permanent
  unless it keeps getting reinforced.
- **Querying memory:** to check "does the network still associate cat
  with meow," we don't look anything up in a table — we literally measure
  how strongly cat's neurons are currently wired into meow's neurons.
  Same mechanism for storage and recall.

## What we tested and found (real numbers, from actual runs)

| Preset | What it isolates | Result |
|---|---|---|
| `learn_then_forget` | Base effect | Association rose to ~34.5 after repeated pairing, dropped to ~18.8 after 8 unrelated interference words |
| `reinforced_control` | Rules out "it just decays regardless" | Stayed flat around ~53 with continuous reinforcement and zero interference |
| `competing_associations` | Rules out "there's a protected memory slot" | Two independently-learned pairs (cat–meow, dog–bark) both degraded under shared interference — same synapse grid, no dedicated storage for either |

**Why the control matters:** without it, a skeptical judge could argue
the association strength just naturally fades with time regardless of
what happens. The control shows that reinforcement without interference
holds steady — the drop in the main preset is specifically caused by
*interference*, not passive decay alone.

## Theoretical validation (the "truth beside estimate" piece)

We built a simple textbook-style formula (fixed strength "bump" on
reinforcement, fixed percentage decay every step) and compared it
against the real simulation.

- With a normal-size neuron pool (30 neurons, 3 active per word), the
  simple formula predicts the real simulation closely (mean squared
  error ≈ 1.4–1.9). Unrelated words essentially never share neurons by
  chance, so each association behaves independently, matching the simple
  theory.
- Shrinking the neuron pool to 8 (same sparsity of 3 active per word)
  causes real neuron overlap between *unrelated* words. Prediction error
  jumps roughly 15–18x (MSE ≈ 24.8 vs ≈ 1.4). This is the moment the
  simple theory breaks down, because it doesn't account for
  representation collisions — but the real Hebbian model still behaves
  correctly, it's just that reality is richer than the simple formula.

This second result is worth foregrounding in the artifact: it's a live,
honest demonstration of where a simplified mental model diverges from
what's actually happening — exactly the kind of "gap is the lesson"
moment the design standards ask for.

## Known limitations / things NOT to overclaim

- This is a hand-designed toy with ~30 neurons, not a trained model —
  the neuron-to-word mapping is randomly assigned, not learned from data.
- It illustrates the *mechanism* (Hebbian strengthening + decay as
  memory), not BDH's actual scale, training process, or exact equations.
- The "trace" mechanism is a simplification of how BDH implements
  short-term synaptic memory during inference — cite the primary source
  for the real formulation rather than presenting this as equivalent.
- Sparsity is fixed per word by construction here; in a real trained
  system sparsity emerges from training, it isn't hardcoded.

## For the BDH module specifically

Point to: attention reformulated as synaptic memory, updated as the
model reads (Dragon Hatchling paper); the ~5% active-neuron sparsity
statistic; and BDH-CQ's description of contextual memory in terms of
fast-weight / linear-attention views, with state accumulating additively
per demonstration. Say plainly that this toy model is inspired by and
illustrates that mechanism at a tiny scale — not a reproduction of it.
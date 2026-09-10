# Synaptic Plasticity DataForge

## Synaptic Plasticity as Short-Term Memory

A small interactive and experimental model demonstrating how **changes in synaptic strength can act as a form of short-term associative memory**.

The project asks:

> **Can a network remember which items recently occurred together by changing the strength of connections between neurons, without maintaining a separate memory slot for every association?**

The model uses a deliberately small Hebbian memory system so that learning, recall, forgetting, interference, and representation capacity can be observed directly.

This project was developed for the **DataForge 2026 Pathway Track**.

---

## Table of Contents

* [Project Overview](#project-overview)
* [Central Claim](#central-claim)
* [Learning Objectives](#learning-objectives)
* [How the Model Works](#how-the-model-works)
* [Model Architecture](#model-architecture)
* [Hebbian Learning](#hebbian-learning)
* [Short-Term Memory and Decay](#short-term-memory-and-decay)
* [Vocabulary and Representations](#vocabulary-and-representations)
* [Experiments](#experiments)
* [Experimental Results](#experimental-results)
* [Theoretical Comparison](#theoretical-comparison)
* [Neuron Pool Sweep](#neuron-pool-sweep)
* [Interactive Frontend](#interactive-frontend)
* [Repository Structure](#repository-structure)
* [Installation](#installation)
* [Running the Model](#running-the-model)
* [Running the Experiments](#running-the-experiments)
* [Changing Model Parameters](#changing-model-parameters)
* [Output Data](#output-data)
* [Understanding the Results](#understanding-the-results)
* [Relation to BDH and BDH-CQ](#relation-to-bdh-and-bdh-cq)
* [Limitations](#limitations)
* [Reproducibility](#reproducibility)
* [AI Assistance and Provenance](#ai-assistance-and-provenance)
* [References](#references)

---

# Project Overview

Synaptic plasticity describes the ability of connections between neurons to change as a result of neural activity.

In this project, those changing connections are treated as a **temporary memory substrate**.

Instead of storing an association such as:

```text
cat → meow
```

inside a separate lookup table, the model strengthens connections between the neurons activated by `cat` and the neurons activated by `meow`.

Repeated co-occurrence increases the relevant synaptic strength.

Later activity can weaken the association through decay and interference.

The resulting system demonstrates three important behaviors:

1. **Learning** — repeated co-occurrence strengthens an association.
2. **Recall** — the association is measured from the current synaptic state.
3. **Forgetting/interference** — later activity can weaken a previously learned association.

The important idea is that the memory is represented by the **current values of the synaptic weight matrix**, rather than by a separate memory slot.

---

# Central Claim

The central claim of the project is:

> **A network can retain information about recently co-occurring items through changes in synaptic strength, without allocating a separate memory slot for every association, but the same mutable state that enables rapid learning also makes the memory vulnerable to interference.**

The experiments are designed so that this claim can be tested directly.

A learner can observe an association increase during repeated reinforcement and then decrease when unrelated activity is introduced.

---

# Learning Objectives

After interacting with the project, a learner should be able to:

* Explain what synaptic plasticity means computationally.
* Describe how Hebbian updates can strengthen an association.
* Explain why changing synaptic weights can function as short-term memory.
* Distinguish learning from forgetting and interference.
* Explain why continued reinforcement can preserve an association.
* Understand why smaller neuron pools create more representation collisions.
* Compare the simplified synaptic-memory mechanism with conventional context-based memory.
* Explain how the concept relates to the memory mechanism described in BDH.
* Identify the major limitations of the simplified model.

---

# How the Model Works

The overall process is:

```text
Input word
    ↓
Fixed sparse neuron representation
    ↓
Recent activity trace
    ↓
Hebbian synaptic update
    ↓
Synaptic weight matrix
    ↓
Association strength
    ↓
Learning / recall / forgetting
```

For example:

```text
cat → meow
```

activates one group of neurons for `cat` and another group for `meow`.

Repeatedly presenting:

```text
cat
meow
cat
meow
cat
meow
```

strengthens the connections between the corresponding neuron groups.

If the network subsequently receives unrelated inputs:

```text
car
tree
cloud
phone
shoe
lamp
rain
book
```

the previously learned association becomes weaker.

The association is therefore not stored as:

```text
memory["cat"] = "meow"
```

Instead, it is represented by the changing values of the synaptic matrix.

---

# Model Architecture

The core memory mechanism is implemented in:

```text
hebbian_core.py
```

The model contains:

* A fixed neuron pool.
* A synaptic weight matrix.
* Sparse neuron activation.
* A recent-activity trace.
* Hebbian strengthening.
* Continuous weight decay.
* Association-strength measurement.
* Optional weight-history export.

The standard configuration is:

| Parameter               | Default |
| ----------------------- | ------: |
| Number of neurons       |      30 |
| Active neurons per word |       3 |
| Decay                   |    0.08 |
| Learning rate           |     0.4 |

Therefore, the standard representation is:

```text
30 total neurons
       ↓
3 active neurons for each word
```

The sparse representation is intentional. It makes the model small enough that the state and its changes can be inspected directly.

It is also conceptually related to the sparse activity discussed in the project's BDH context, but **it should not be interpreted as an exact implementation of BDH**.

---

# Hebbian Learning

The learning mechanism follows the basic Hebbian idea:

> Neurons that are repeatedly active together strengthen their connections.

The model does not require two word representations to be active at exactly the same instant.

Instead, the first activation contributes to a short recent-activity trace.

Conceptually:

```text
A activates neurons
        ↓
recent activity trace
        ↓
B activates neurons
        ↓
connections A → B strengthened
```

This allows the model to represent an ordered relationship:

```text
A → B
```

rather than only simultaneous activation:

```text
A + B
```

The recent-activity trace is intentionally simplified and exists to make the short-term association mechanism visible.

---

# Short-Term Memory and Decay

The memory is temporary because synaptic weights continuously decay.

Conceptually:

```text
old weight
    ↓
decay
    ↓
smaller weight
```

If an association continues to receive reinforcement:

```text
reinforcement + decay
        ↓
association remains strong
```

If reinforcement stops:

```text
decay
   ↓
weaker synaptic connection
   ↓
lower association strength
```

This creates the central trade-off of the project:

```text
Synaptic plasticity
        ↓
Rapid adaptation
        ↓
Temporary memory
        ↓
But also
        ↓
Interference + limited capacity
```

---

# Vocabulary and Representations

The experiment layer is implemented in:

```text
experiments.py
```

The current vocabulary includes:

| Word    | Symbol ID | Purpose                    |
| ------- | --------: | -------------------------- |
| `cat`   |         1 | First learned association  |
| `meow`  |         2 | First learned association  |
| `dog`   |         3 | Second learned association |
| `bark`  |         4 | Second learned association |
| `car`   |        10 | Interference               |
| `tree`  |        11 | Interference               |
| `cloud` |        12 | Interference               |
| `phone` |        13 | Interference               |
| `shoe`  |        14 | Interference               |
| `lamp`  |        15 | Interference               |
| `rain`  |        16 | Interference               |
| `book`  |        17 | Interference               |

The mapping is **fixed and hand-designed**.

The model does not learn semantic word representations.

The words simply provide readable labels for predetermined neuron representations.

---

# Experiments

The repository currently contains three main experimental presets.

## 1. `learn_then_forget`

This is the main experiment.

### Learning phase

The model repeatedly receives:

```text
cat → meow
cat → meow
cat → meow
cat → meow
cat → meow
cat → meow
```

### Interference phase

It then receives:

```text
car
tree
cloud
phone
shoe
lamp
rain
book
```

The expected behavior is:

```text
Association strength
        ↑
        │        /\
        │       /  \
        │      /    \
        │_____/      \________
        │
        └──────────────────────→ time
             learning   interference
```

The experiment records the association strength **at every step**, allowing the entire learning and forgetting trajectory to be visualized.

---

## 2. `reinforced_control`

This is the control experiment.

The model continues receiving:

```text
cat → meow
cat → meow
cat → meow
...
```

without introducing unrelated interference.

The purpose is to distinguish:

* natural decay over time

from:

* weakening caused by interference.

If the association remains high under continued reinforcement, then the decrease in the main experiment cannot simply be attributed to the passage of additional processing steps.

---

## 3. `competing_associations`

This experiment stores two associations in the same synaptic matrix:

```text
cat → meow
```

and:

```text
dog → bark
```

Both associations share the same network.

There are no dedicated slots such as:

```text
Memory Slot 1 = cat/meow
Memory Slot 2 = dog/bark
```

Instead:

```text
              Shared Synaptic Matrix
        ┌─────────────────────────────┐
cat ───→│                             │←── meow
dog ───→│       shared weights        │←── bark
        │                             │
        └─────────────────────────────┘
```

Later activity can therefore affect both associations.

This experiment demonstrates the trade-off between flexible synaptic memory and interference.

---

# Experimental Results

The exported experiments show the following behavior.

## Learning and interference

For the `cat–meow` association:

```text
After learning:       ~34.5
After interference:   ~18.8
```

The association becomes substantially weaker after unrelated activity.

## Reinforced control

With continued reinforcement and no unrelated interference:

```text
Association: ~53
```

The association remains strong.

This provides a control against interpreting the decrease in the main experiment as simple time-based decay.

## Competing associations

Both:

```text
cat–meow
dog–bark
```

can coexist in the same synaptic matrix.

Both can subsequently weaken when interference is introduced.

These results demonstrate that memory and interference arise from the same changing synaptic state.

---

# Theoretical Comparison

The repository includes a simplified mathematical model for comparison with the actual simulation.

The theoretical model assumes:

1. Association strength decays by a fixed percentage at every step.
2. A fixed reinforcement amount is added when the tracked pair occurs.
3. The pair is considered reinforced when the two words occur adjacently.

Conceptually:

```text
If pair occurs:

strength =
    strength × (1 - decay) + bump
```

Otherwise:

```text
strength =
    strength × (1 - decay)
```

This is intentionally simpler than the actual Hebbian simulation.

The real model contains a multi-step activity trace, whereas the theoretical approximation uses a simpler adjacent-pair rule.

The purpose of the comparison is therefore **not** to claim that the equation exactly describes the neural model.

Instead, it asks:

> How closely can a simple mathematical approximation describe the behavior of the full simulation?

The reinforcement "bump" is fitted using a coarse grid search from:

```text
0.5 → 20.0
```

with increments of:

```text
0.5
```

The best value is selected using mean squared error.

---

# Neuron Pool Sweep

The project also investigates how the size of the neuron pool affects the accuracy of the simplified theory.

The default sweep includes:

```text
6
8
10
15
20
30
50
80
```

neurons.

The number of active neurons per word remains sparse.

### Larger neuron pool

With more neurons:

```text
Word A → neurons 1, 4, 9
Word B → neurons 12, 17, 25
```

there is less chance that unrelated representations overlap.

### Smaller neuron pool

With fewer neurons:

```text
Word A → neurons 1, 4, 6
Word B → neurons 1, 5, 6
```

different words are more likely to share neurons.

These **representation collisions** create additional interactions that the simplified theoretical model does not explicitly account for.

---

# Neuron Pool Results

The reported comparison is approximately:

```text
30 neurons
MSE ≈ 1.4
```

versus:

```text
8 neurons
MSE ≈ 24.8
```

Therefore, reducing the neuron pool substantially increases the difference between the theoretical approximation and the actual simulation.

This does **not** mean that the Hebbian memory mechanism stops working.

Instead, it demonstrates that the simplified independent-association theory becomes less accurate when representations overlap.

---

# Interactive Frontend

The repository also contains a browser-based frontend:

```text
index.html
style.css
app.js
```

The frontend is designed to expose the model's behavior visually rather than only presenting final numerical results.

The exported experiment data can be used to display:

* Association-strength trajectories.
* Learning behavior.
* Interference and forgetting.
* Reinforced control behavior.
* Competing associations.
* Neuron-pool sweep results.

The Python experiment layer produces JSON-compatible data specifically so that the results can be consumed by a visualization/frontend layer.

---

# Repository Structure

```text
synaptic-plasticity-dataforge/
│
├── README.md
├── MODEL_NOTES.md
│
├── hebbian_core.py
├── experiments.py
├── test-model.py
│
├── index.html
├── app.js
├── style.css
│
├── presets_export.json
├── neuron_sweep_export.json
│
├── requirements.txt
└── .gitignore
```

### `hebbian_core.py`

Core memory mechanism.

Responsible for:

* Neuron representation.
* Synaptic weight matrix.
* Activity trace.
* Hebbian updates.
* Weight decay.
* Association-strength calculation.
* Weight-history export.
* Basic forgetting demonstration.

### `experiments.py`

Higher-level experiment layer.

Responsible for:

* Vocabulary.
* Experiment presets.
* Running experiments.
* Tracking association strengths.
* Per-step result generation.
* Theoretical curves.
* Theoretical-model fitting.
* MSE calculation.
* Neuron-pool sweeps.
* JSON-compatible output.

### `MODEL_NOTES.md`

Detailed research and model notes covering:

* Central claim.
* Model mechanics.
* Experimental results.
* Theoretical validation.
* Known limitations.
* BDH relationship.

### `presets_export.json`

Exported experiment/preset information and result data.

### `neuron_sweep_export.json`

Exported neuron-pool sweep results.

This allows the frontend to use sweep results without rerunning every simulation.

### `test-model.py`

Test/demo entry point for checking the model.

### `requirements.txt`

Current Python dependency:

```text
numpy>=1.24
```

### Frontend

```text
index.html
app.js
style.css
```

These provide the browser-based visualization layer.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/t3rrible0ctopus/synaptic-plasticity-dataforge.git
cd synaptic-plasticity-dataforge
```

Create a virtual environment if desired:

```bash
python -m venv venv
```

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

The current dependency list requires NumPy 1.24 or newer.

---

# Running the Model

Run the core demonstration:

```bash
python hebbian_core.py
```

The demonstration performs two phases.

### Phase 1 — Learning

It repeatedly presents:

```text
A → B
```

six times.

### Phase 2 — Interference

It then presents unrelated symbols:

```text
10
11
12
13
14
15
16
17
```

The model compares association strength before and after interference.

The core demonstration also exports the weight history:

```text
weight_history.json
```

when the corresponding export path is used by the implementation.

---

# Running the Experiments

Run the experiment layer with:

```bash
python experiments.py
```

Available presets:

```text
learn_then_forget
reinforced_control
competing_associations
```

---

# Running a Preset Programmatically

The primary interface is:

```python
from experiments import run_preset

data = run_preset("learn_then_forget")

print(data)
```

The model parameters can also be supplied explicitly:

```python
data = run_preset(
    "learn_then_forget",
    n_neurons=30,
    decay=0.08,
    learning_rate=0.4
)
```

The returned experiment data contains:

```text
name
description
sequence
tracked_pairs
steps
params
```

Each step records the current input and association strengths.

This makes it possible to reconstruct the full association-strength curve rather than only comparing final values.

---

# Changing Model Parameters

The standard configuration is:

```python
n_neurons=30
decay=0.08
learning_rate=0.4
```

These parameters can be changed when running a preset.

Example:

```python
data = run_preset(
    "learn_then_forget",
    n_neurons=50,
    decay=0.05,
    learning_rate=0.4
)
```

## `n_neurons`

Controls the size of the neuron pool.

Smaller values:

```text
more representation collisions
```

Larger values:

```text
less accidental overlap
```

## `decay`

Controls how quickly synaptic weights weaken.

Higher decay:

```text
faster forgetting
```

Lower decay:

```text
slower forgetting
```

## `learning_rate`

Controls the strength of the Hebbian update.

Higher learning rate:

```text
stronger reinforcement
```

Lower learning rate:

```text
weaker reinforcement
```

---

# Output Data

Experiment results are structured approximately as:

```json
{
  "name": "learn_then_forget",
  "description": "...",
  "sequence": [
    "cat",
    "meow"
  ],
  "tracked_pairs": [
    "cat-meow"
  ],
  "steps": [
    {
      "step": 0,
      "symbol": "cat",
      "associations": {
        "cat-meow": 0.0
      }
    }
  ],
  "params": {
    "n_neurons": 30,
    "decay": 0.08,
    "learning_rate": 0.4
  }
}
```

The important feature is that association strength is recorded **at every step**.

This allows the complete progression to be visualized:

```text
Learning
   ↓
Peak association
   ↓
Interference
   ↓
Decay
```

---

# Understanding the Results

## Increasing association strength

If association strength increases during repeated:

```text
cat → meow
```

presentations, this represents learning.

The relevant synaptic connections are being strengthened.

## Decreasing association strength

If the association later changes:

```text
34
 ↓
29
 ↓
24
 ↓
18
```

during unrelated input, this represents interference and forgetting.

The original association is no longer continuously reinforced while the synaptic state continues to change and decay.

## Stable association

If:

```text
cat → meow
```

continues to be presented and the association remains high, this represents the expected behavior of the reinforced control.

It demonstrates that continued reinforcement can maintain the learned association.

---

# Relation to BDH and BDH-CQ

The project is motivated by the broader idea that synaptic plasticity can provide a mechanism for memory during inference.

Dragon Hatchling (BDH) provides a relevant architectural example in which information can be represented through changing synaptic state and Hebbian-style updates.

The conceptual relationship is:

```text
Input
  ↓
Neural activity
  ↓
Synaptic update
  ↓
Changed network state
  ↓
Later recall
```

However:

> **This repository is not a BDH implementation.**

The project uses:

* A hand-designed word vocabulary.
* A small neuron pool.
* Fixed sparse representations.
* Simplified Hebbian dynamics.
* Simplified decay.
* Small-scale experiments.

It does **not** reproduce the scale, architecture, training procedure, or exact equations of BDH.

The purpose of the BDH connection is to show how the same broad idea—using changing synaptic state as part of memory—appears in a current AI architecture.

BDH-CQ provides a related example involving inference-time recurrent memory and latent reasoning. It is included as research context rather than as a claim that this toy model reproduces BDH-CQ.

---

# Limitations

This project should be interpreted as a **toy educational model**, not as a biologically complete simulation or production-scale AI architecture.

## 1. Small network

The main configuration uses only:

```text
30 neurons
```

This is extremely small compared with biological neural systems and modern AI models.

## 2. Hand-designed representations

The word-to-neuron mapping is fixed.

The model therefore does not learn semantic representations from data.

For example:

```text
cat
```

does not intrinsically encode animal-related meaning.

It simply maps to a predetermined set of active neurons.

## 3. Simplified learning rule

The Hebbian mechanism is designed to demonstrate the concept rather than reproduce the full biological complexity of synaptic plasticity.

## 4. Simplified activity trace

The activity trace represents recent activity in a simplified way.

It should not be interpreted as an exact reproduction of biological synaptic dynamics or BDH.

## 5. Fixed sparsity

The number of active neurons per word is fixed by construction.

The project therefore does not demonstrate sparsity emerging through training.

## 6. Representation collisions

When the neuron pool becomes small, different words can share neurons.

This introduces interactions that are not fully represented by the simplified theoretical model.

This limitation is also useful experimentally because it demonstrates where the simplified theory stops accurately describing the full simulation.

---

# Reproducibility

The primary experiment can be reproduced using:

```text
Neuron pool: 30
Decay:       0.08
Learning rate: 0.4
Preset:      learn_then_forget
```

The learning sequence is:

```text
cat
meow
cat
meow
cat
meow
cat
meow
cat
meow
cat
meow
```

followed by:

```text
car
tree
cloud
phone
shoe
lamp
rain
book
```

The reinforced control repeatedly presents:

```text
cat
meow
```

without unrelated interference.

The competing-associations experiment uses:

```text
cat
meow
...
dog
bark
...
interference
```

The experiment data stores the parameters used to generate each result so that the configuration can be identified alongside the output.

---

# Project Takeaway

The central result is:

> **Synaptic changes can act as short-term memory.**

Repeated activity can strengthen associations in the network.

Those associations can later be recalled by measuring the corresponding synaptic connections.

However, because the memory is stored in the same changing network state, subsequent activity can weaken or overwrite previous associations.

Therefore:

```text
Synaptic Plasticity
        ↓
Temporary Memory
        ↓
Fast Adaptation
        ↓
But also
        ↓
Interference + Limited Capacity
```

The project makes this trade-off observable through a small Hebbian model rather than treating memory as an abstract concept.

---

# AI Assistance and Provenance

AI-assisted coding, writing, research, or design may have been used during development of the project.

All generated or assisted components should be reviewed and understood by the project team before submission.

The project should not claim that AI-generated or externally reused components were independently developed.

Any reused code, data, graphics, fonts, libraries, or other third-party assets should be identified separately with their applicable licenses.

The project team is responsible for understanding and defending the implementation and its results.

---

# References

1. Kozachkov, L. et al. (2022). **Robust and brain-like working memory through short-term synaptic plasticity.** *PLOS Computational Biology*. DOI: `10.1371/journal.pcbi.1010776`

2. Kosowski, A. et al. (2025). **The Dragon Hatchling: The Missing Link between the Transformer and Models of the Brain.** arXiv: `2509.26507`

3. Engdahl, B. et al. (2026). **BDH-CQ: In-Context Learning with Recurrent Latent Reasoning.** arXiv: `2608.09888`

4. **Synaptic Plasticity DataForge Project Repository.**
   Contains the Hebbian memory implementation, experiment presets, model notes, frontend, and exported experimental data.

---

# Project Status

This repository currently represents a **small experimental and educational implementation of synaptic plasticity as short-term memory**.

The intended mechanism is:

```text
Co-occurrence
     ↓
Hebbian strengthening
     ↓
Changed synaptic weights
     ↓
Temporary association
     ↓
Interference / decay
     ↓
Forgetting
```

The implementation is intentionally small enough for the learner to inspect the underlying state and reproduce the main behavior.

It is **not presented as a complete BDH implementation or a biologically exact simulation**.

The repository's implementation, model notes, and exported experimental data should be treated as the authoritative description of the current experiments and their parameters.

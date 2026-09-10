# Synaptic Plasticity DataForge

## Synaptic Plasticity as Short-Term Memory

A small experimental model demonstrating how **changes in synaptic strength can act as a form of short-term memory**.

This project explores a simple question:

> Can a neural network remember which items recently occurred together by changing the strength of connections between neurons, without maintaining a separate memory slot for every association?

The project uses a deliberately small Hebbian memory model so that the complete process of **learning, interference, forgetting, and recall** can be observed directly.

This repository is part of the **DataForge 2026 Pathway Track** project on synaptic plasticity and short-term memory.

---

## Table of Contents

* [Overview](#overview)
* [Core Idea](#core-idea)
* [How the Model Works](#how-the-model-works)
* [Model Architecture](#model-architecture)
* [Hebbian Learning](#hebbian-learning)
* [Short-Term Memory and Decay](#short-term-memory-and-decay)
* [Vocabulary and Representations](#vocabulary-and-representations)
* [Experiments](#experiments)
* [Experimental Results](#experimental-results)
* [Theoretical Comparison](#theoretical-comparison)
* [Neuron Pool Sweep](#neuron-pool-sweep)
* [Repository Structure](#repository-structure)
* [Installation](#installation)
* [Running the Model](#running-the-model)
* [Running Individual Experiments](#running-individual-experiments)
* [Output Data](#output-data)
* [Understanding the Results](#understanding-the-results)
* [Relation to BDH](#relation-to-bdh)
* [Limitations](#limitations)
* [Reproducibility](#reproducibility)
* [References](#references)

---

# Overview

Synaptic plasticity is the ability of connections between neurons to change as a result of neural activity.

In this project, those changing connections are treated as a temporary memory system.

Instead of storing an association such as:

```text
cat → meow
```

inside a conventional lookup table, the model strengthens connections between the neurons activated by `cat` and the neurons activated by `meow`.

When the same association is reinforced, its connection strength increases.

When unrelated information is subsequently processed, the existing connection is weakened through decay and interference.

This produces a simple form of **short-term associative memory**.

The project therefore demonstrates three related behaviors:

1. **Learning** — repeated co-occurrence strengthens an association.
2. **Recall** — the association can be measured from the current synaptic weights.
3. **Forgetting/interference** — later activity can weaken an association.

The report describes the central claim as a network retaining information about recently co-occurring items through synapse-strength changes rather than dedicated memory slots.

---

# Core Idea

The entire model can be summarized as:

```text
Input words
    ↓
Active neuron groups
    ↓
Hebbian synaptic updates
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

causes the connections between their active neurons to become stronger.

If the network then receives:

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

the previously strengthened `cat–meow` association becomes weaker.

The important point is that the memory is not stored in a separate data structure containing the relationship.

It is represented by the current values in the synaptic weight matrix.

---

# How the Model Works

## 1. Words are converted into symbols

The experiment uses a small fixed vocabulary.

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

The mapping is deliberately simple and fixed. The IDs are not learned from data.

The experiment layer converts these readable words into the integer IDs used by the core memory model.

---

# Model Architecture

The core model is implemented in:

```text
hebbian_core.py
```

The model contains:

* a fixed number of neurons
* a synaptic weight matrix
* sparse neuron activation
* a recent-activity trace
* Hebbian strengthening
* weight decay
* association-strength measurement
* optional weight-history export

The main experiment uses:

```text
Number of neurons = 30
Active neurons per word = 3
Decay = 0.08
Learning rate = 0.4
```

The model therefore represents each word using a small subset of the total neuron pool.

For the standard configuration:

```text
30 total neurons
       ↓
3 active neurons for each input word
```

This sparse representation is intentional and is also discussed in the project's model notes as being conceptually related to the sparse activity described for BDH. It should not, however, be interpreted as an exact implementation of BDH's neuron representation.

---

# Hebbian Learning

The learning mechanism is based on the basic idea commonly summarized as:

> Neurons that are repeatedly active together strengthen their connections.

In this project, when the neurons associated with one word are active shortly before another word, the connections between the corresponding neuron groups are strengthened.

A simplified representation is:

```text
A activates neurons
        ↓
recent activity trace
        ↓
B activates neurons
        ↓
connections A → B strengthened
```

The model uses a short activity trace rather than requiring both groups of neurons to activate at exactly the same instant.

This allows the model to represent a sequence such as:

```text
A → B
```

rather than only simultaneous activation:

```text
A + B
```

The project documentation describes this as the mechanism that allows the model to capture ordered recent activity.

---

# Short-Term Memory and Decay

The memory is temporary because synaptic weights are continuously decayed.

At every processing step, the connections shrink slightly.

Conceptually:

```text
old weight
    ↓
decay
    ↓
slightly smaller weight
```

If an association is repeatedly reinforced, learning can compensate for the decay:

```text
reinforcement + decay
        ↓
association remains strong
```

If the association is no longer reinforced:

```text
decay
  ↓
weaker connection
  ↓
lower recall strength
```

This is what makes the model a **short-term memory** rather than a permanent storage mechanism.

The core implementation uses a decay parameter and applies the model's update rule every time a new symbol is processed.

---

# Association Strength

The model does not use a separate lookup table to answer:

```text
"Does cat mean meow?"
```

Instead, it directly measures the strength of the connections between the active neuron groups for the two words.

Conceptually:

```text
cat neurons
     ↓
synaptic weight matrix
     ↓
meow neurons
     ↓
association strength
```

The code calculates association strength from the active neuron vectors and the synaptic weight matrix.

This means that **storage and recall use the same underlying representation**: the synaptic weights.

---

# Vocabulary and Representations

The experiment layer is implemented in:

```text
experiments.py
```

It provides a readable interface over the lower-level Hebbian model.

Instead of working directly with integer symbol IDs, experiments can be described using words such as:

```python
["cat", "meow", "car", "tree"]
```

The experiment system then:

1. converts words to IDs
2. feeds them to `HebbianMemory`
3. records association strengths
4. stores the strength at every step
5. returns JSON-compatible experiment data

This makes the results suitable for visualization and analysis rather than only printing a final number.

---

# Experiments

The repository currently contains three main experimental presets.

## 1. `learn_then_forget`

This is the main experiment.

Sequence:

```text
cat → meow
cat → meow
cat → meow
cat → meow
cat → meow
cat → meow

then:

car
tree
cloud
phone
shoe
lamp
rain
book
```

The first phase repeatedly reinforces:

```text
cat ↔ meow
```

The second phase introduces unrelated words.

The expected behavior is:

```text
Association strength
       ↑
       │       /\
       │      /  \
       │     /    \
       │____/      \________
       │
       └────────────────────→ time
             learning  interference
```

The actual experiment records the association at every step rather than only measuring it before and after interference.

---

## 2. `reinforced_control`

This is the control experiment.

Sequence:

```text
cat → meow
cat → meow
cat → meow
...
```

The association continues to be reinforced and no unrelated interference is introduced.

This experiment is important because otherwise a decrease in association strength could simply be explained by natural decay over time.

The control asks:

> What happens if the memory continues to receive reinforcement?

The expected result is that the association remains high.

The repository documentation explicitly uses this control to distinguish **decay caused by interference** from simple decay caused by lack of reinforcement.

---

## 3. `competing_associations`

This experiment introduces two learned associations:

```text
cat → meow
```

and

```text
dog → bark
```

Both associations are stored in the same synaptic matrix.

After learning both pairs, unrelated filler words are introduced.

The purpose is to demonstrate that there are no dedicated memory slots such as:

```text
Memory Slot 1 = cat/meow
Memory Slot 2 = dog/bark
```

Instead:

```text
          Shared Synaptic Matrix
        ┌─────────────────────────┐
cat ───→│                         │←── meow
dog ───→│                         │←── bark
        │                         │
        └─────────────────────────┘
```

Because both associations share the same network, later activity can affect both.

This demonstrates the trade-off between flexible synaptic memory and interference.

---

# Experimental Results

The exported experimental results reported in the project show:

### Main learning/forgetting experiment

The `cat–meow` association:

```text
After learning:       ~34.5
After interference:   ~18.8
```

The association therefore becomes substantially weaker after unrelated activity.

### Reinforced control

With continuous reinforcement and no interference:

```text
Association: ~53
```

The association remains strong.

This supports the interpretation that the decrease in the main experiment is related to interference rather than simply the passage of additional processing steps.

### Competing associations

Both:

```text
cat–meow
dog–bark
```

can coexist in the same synaptic matrix.

Both can subsequently weaken when interference is introduced.

## These results are documented in the project's model notes and report.

# Theoretical Comparison

The repository also includes a simplified theoretical model.

The theoretical model assumes:

1. Association strength decays by a fixed percentage at every step.
2. A fixed amount is added whenever the tracked pair occurs.
3. The pair is considered reinforced when the two words occur adjacently.

Conceptually:

```text
If pair occurs:

strength = strength × (1 - decay) + bump

Otherwise:

strength = strength × (1 - decay)
```

This is intentionally simpler than the actual Hebbian simulation.

The real model contains a multi-step activity trace, while the theoretical model treats reinforcement using a simpler adjacent-pair rule.

---

# Why Compare Theory and Simulation?

The comparison is not intended to prove that the simplified equation is the exact behavior of the neural model.

Instead, it asks:

> How closely does a simple mathematical approximation describe the actual simulation?

The repository fits the theoretical model's reinforcement "bump" using a coarse grid search and then calculates the mean squared error between the simulated and predicted curves.

The bump is searched over:

```text
0.5 → 20.0
```

in increments of:

```text
0.5
```

The best-fitting value is selected using least-squares mean squared error.

---

# Neuron Pool Sweep

The project also investigates what happens when the neuron pool becomes smaller.

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

The reason for this experiment is important.

With a large neuron pool:

```text
Word A → neurons 1, 4, 9
Word B → neurons 12, 17, 25
```

there is less chance that unrelated words accidentally use the same neurons.

With a small neuron pool:

```text
Word A → neurons 1, 4, 6
Word B → neurons 1, 5, 6
```

unrelated words can share neurons.

This creates **representation collisions**.

As a result, the simple theoretical assumption that each association behaves independently becomes less accurate.

The repository specifically uses this sweep to study the relationship between neuron-pool size, representation collisions, and theoretical-model error.

---

# Neuron Pool Results

The project reports approximately:

```text
30-neuron case:
MSE ≈ 1.4

8-neuron case:
MSE ≈ 24.8
```

Therefore, reducing the neuron pool from 30 to 8 can cause a large increase in the difference between the simplified theoretical model and the actual simulation.

The report describes this as approximately a 15–18× increase in MSE.

Importantly, this does **not** mean that the Hebbian model stops working.

Instead, it shows that the simplified mathematical approximation does not capture the additional interactions created by overlapping neuron representations.

---

# Repository Structure

The current repository contains the following main files:

```text
synaptic-plasticity-dataforge/
│
├── MODEL_NOTES.md
├── experiments.py
├── hebbian_core.py
├── neuron_sweep_export.json
├── presets_export.json
├── requirements.txt
├── test-model.py
└── .gitignore
```

The repository currently exposes these files on its main branch.

---

## `hebbian_core.py`

Contains the core memory mechanism.

Responsibilities include:

* neuron representation
* synaptic weight matrix
* activity trace
* Hebbian updates
* decay
* association-strength calculation
* history export
* basic forgetting demonstration

The file also contains a direct demonstration that repeatedly presents two symbols and then introduces unrelated symbols to test whether the original association decreases.

---

## `experiments.py`

Contains the higher-level experiment layer.

Responsibilities include:

* readable word vocabulary
* experiment presets
* running experiments
* tracking association strengths
* generating per-step results
* theoretical curve generation
* theoretical-model fitting
* MSE calculation
* neuron-pool sweeps
* JSON-compatible result generation

The experiment layer is designed to provide data suitable for a frontend or visualization system.

---

## `MODEL_NOTES.md`

Contains the project's detailed model explanation and research handoff notes.

It documents:

* the central claim
* model mechanics
* experimental results
* theoretical validation
* known limitations
* relationship to BDH

It is particularly useful when trying to understand what the project is intended to demonstrate and what should **not** be overclaimed.

---

## `presets_export.json`

Contains exported experiment/preset information used to represent the experiment configurations and results.

---

## `neuron_sweep_export.json`

Contains exported neuron-pool sweep results.

This allows the results of the sweep to be used without having to rerun every simulation.

---

## `test-model.py`

Provides a test/demo entry point for checking the model.

---

## `requirements.txt`

The current repository specifies:

```text
numpy>=1.24
```

as its dependency.

---

# Installation

Clone the repository:

```bash
git clone https://github.com/t3rrible0ctopus/synaptic-plasticity-dataforge.git
cd synaptic-plasticity-dataforge
```

Create a Python virtual environment if desired:

```bash
python -m venv venv
```

Activate it on macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

Install the dependency:

```bash
pip install -r requirements.txt
```

The current dependency list contains NumPy 1.24 or newer.

---

# Running the Model

The core demonstration can be run with:

```bash
python hebbian_core.py
```

The basic demonstration performs two phases.

### Phase 1 — Learning

The model repeatedly presents:

```text
A → B
```

six times.

### Phase 2 — Interference

It then presents:

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

as unrelated symbols.

The model compares the association strength before and after interference.

If the association decreases, the experiment prints a supported result.

It also exports the weight history to:

```text
weight_history.json
```

for visualization.

---

# Running the Experiments

The higher-level experiments can be executed from:

```bash
python experiments.py
```

The available experiment presets are:

```text
learn_then_forget
reinforced_control
competing_associations
```

These presets are defined directly in `experiments.py`.

---

# Running a Preset Programmatically

The main experiment interface is:

```python
run_preset(
    name,
    n_neurons=30,
    decay=0.08,
    learning_rate=0.4
)
```

For example:

```python
from experiments import run_preset

data = run_preset("learn_then_forget")

print(data)
```

The returned object contains:

```text
name
description
sequence
tracked_pairs
steps
params
```

Each step contains the input symbol and the current association strengths.

This makes it possible to plot the complete association-strength curve rather than only comparing two final values.

---

# Changing Model Parameters

The standard experiment uses:

```python
n_neurons=30
decay=0.08
learning_rate=0.4
```

These can be changed when calling `run_preset`.

For example:

```python
data = run_preset(
    "learn_then_forget",
    n_neurons=50,
    decay=0.05,
    learning_rate=0.4
)
```

The three parameters have different effects.

### `n_neurons`

Controls the size of the neuron pool.

Smaller values increase the probability of representation collisions.

Larger values reduce accidental overlap between unrelated word representations.

### `decay`

Controls how quickly synaptic weights weaken.

Higher decay:

```text
faster forgetting
```

Lower decay:

```text
slower forgetting
```

### `learning_rate`

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

The experiment runner produces data structured approximately as:

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

The exact association values depend on the model configuration and sequence.

The important feature is that the model records the association at **every step**.

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

The repository explicitly describes this per-step representation as being more useful for visualization than a single before/after value.

---

# Understanding the Results

## Increasing association strength

If the graph shows:

```text
0
 ↓
10
 ↓
20
 ↓
30
```

during repeated `cat–meow` presentations, this represents learning.

The repeated co-occurrence strengthens the relevant synaptic connections.

---

## Decreasing association strength

If the graph later shows:

```text
34
 ↓
29
 ↓
24
 ↓
18
```

during unrelated input, this represents interference/forgetting.

The original association is no longer continuously reinforced while the model continues to update and decay its synaptic state.

---

## Stable association

If the association remains high while:

```text
cat → meow
```

continues to be repeated, that is the behavior expected from the reinforced control experiment.

It demonstrates that the model is capable of maintaining an association when reinforcement continues.

---

# Relation to BDH

The project is inspired by the idea that **synaptic plasticity can provide a mechanism for memory during inference**.

Dragon Hatchling (BDH) describes a model in which information can be represented through changing synaptic state and Hebbian-style updates.

The current project uses the same broad conceptual direction:

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

However, this repository is **not a BDH implementation**.

It is a deliberately small educational model designed to make the underlying concept observable.

The project uses:

* a hand-designed word vocabulary
* a small neuron pool
* fixed sparse representations
* simplified Hebbian dynamics
* simplified decay
* small-scale experiments

It does not reproduce BDH's scale, architecture, training procedure, or exact equations.

The report explicitly makes this distinction and describes the implementation as an educational model rather than a BDH reproduction.

---

# Why This Model Is Useful

The model is intentionally small.

A large neural architecture can make it difficult to understand exactly where a memory is being stored.

Here, the mechanism can be directly inspected:

```text
word
 ↓
active neurons
 ↓
synaptic matrix
 ↓
association strength
```

This makes several concepts easy to demonstrate:

### Learning

Repeated activation changes the synaptic state.

### Short-term memory

The changed synaptic state persists temporarily.

### Recall

The current synaptic state determines the measured association.

### Forgetting

Unused connections decay.

### Interference

New activity can weaken previously learned associations.

### Capacity limitations

Smaller neuron pools produce more representation collisions.

---

# Important Experimental Insight

One of the most important findings is that **memory and interference are two sides of the same mechanism**.

The same changing synaptic state that makes rapid learning possible also makes the memory vulnerable to later activity.

In simplified form:

```text
Plasticity
    │
    ├── enables rapid learning
    │
    └── allows later activity to modify old memories
                  ↓
              interference
```

Therefore, the goal of the project is not to show that synaptic memory is universally better than conventional memory.

Instead, it demonstrates a trade-off:

```text
Compact temporary memory
          ↕
Interference and limited capacity
```

This is consistent with the project's stated takeaway.

---

# Limitations

This project should be interpreted as a **toy educational model**, not as a biologically complete or production-scale neural architecture.

## 1. Small network

The model uses only a small number of neurons.

The main configuration uses:

```text
30 neurons
```

This is far smaller than a biological neural network or modern AI model.

---

## 2. Hand-designed representations

The word-to-neuron mapping is fixed rather than learned from data.

Therefore, the model does not learn useful semantic representations of words.

For example:

```text
cat
```

does not inherently contain semantic information about an animal.

It is simply mapped to a predetermined set of active neurons.

---

## 3. Simplified learning rule

The Hebbian mechanism is designed to demonstrate the concept rather than reproduce the complete biological complexity of synaptic plasticity.

---

## 4. Simplified trace

The activity trace is a simplified representation of recent activity.

It should not be interpreted as an exact reproduction of the mechanisms used in biological synapses or in BDH.

---

## 5. Fixed sparsity

The number of active neurons per word is fixed by construction.

The model therefore does not demonstrate sparsity emerging through training.

---

## 6. Representation collisions

When the neuron pool becomes small, different words can share neurons.

This can produce interactions that are not represented by the simplified theoretical model.

This limitation is actually useful experimentally because it demonstrates where the simplified theory stops accurately describing the full simulation.

---

# Reproducibility

The primary experiment can be reproduced using the model parameters:

```text
Neuron pool:    30
Decay:          0.08
Learning rate:  0.4
```

and the preset:

```text
learn_then_forget
```

The sequence is:

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
car
tree
cloud
phone
shoe
lamp
rain
book
```

The control uses repeated:

```text
cat
meow
```

without unrelated interference.

The competing-association experiment uses:

```text
cat
meow
...
dog
bark
...
interference
```

The code stores the parameters alongside the generated experiment data, making it possible to identify which configuration produced a result.

---

# Project Takeaway

The central result of the project is:

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

# References

1. Kozachkov, L. et al. (2022). **Robust and brain-like working memory through short-term synaptic plasticity.** PLOS Computational Biology.
   DOI: `10.1371/journal.pcbi.1010776`

2. Kosowski, A. et al. (2025). **The Dragon Hatchling: The Missing Link between the Transformer and Models of the Brain.**
   arXiv: `2509.26507`

3. Engdahl, B. et al. (2026). **BDH-CQ: In-Context Learning with Recurrent Latent Reasoning.**
   arXiv: `2608.09888`

4. **Synaptic Plasticity DataForge Project Repository.**
   Contains the Hebbian memory implementation, experiment presets, model notes, and exported experimental data.

---

# Project Status

This repository currently represents a **small experimental/educational implementation** of synaptic plasticity as short-term memory.

The model is intended to make the following mechanism easy to inspect:

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

It is intentionally not presented as a complete implementation of BDH or as a biologically exact simulation.

The repository's current implementation and model notes should be treated as the authoritative description of the experiments and their parameters.

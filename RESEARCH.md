# Research References and Evidence

## Project: Synaptic Plasticity as Short-Term Memory

This project uses published research to provide the scientific and technical context for the educational simulation. The simulation itself is an intentionally simplified toy model and should not be interpreted as a reproduction of any of the research systems described below.

---

## 1. Short-Term Synaptic Plasticity and Working Memory

**Kozachkov, L., Tauber, J., Lundqvist, M., Brincat, S. L., Slotine, J.-J., & Miller, E. K. (2022).**
**"Robust and brain-like working memory through short-term synaptic plasticity."**
*PLOS Computational Biology, 18(12), e1010776.*

DOI: 10.1371/journal.pcbi.1010776

Source: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010776

### Relevance to this project

This paper investigates whether short-term synaptic plasticity (STSP) can contribute to working-memory maintenance in recurrent neural networks.

The authors compare recurrent neural networks with and without STSP on an object working-memory task. Both types of networks were able to maintain memories in the presence of distractors, while networks with STSP showed activity that was more similar to recorded non-human-primate cortical activity and were more robust to network degradation.

This provides the biological and computational motivation for the project's central idea: information can be represented not only through persistent neural activity, but also through temporary changes in synaptic connections.

### How the project uses this evidence

The project simplifies this idea into a small Hebbian network in which repeated co-activation strengthens connections and subsequent decay weakens them.

The project's simulation is **not** a reproduction of the architecture, training procedure, or experiments from this paper. It is an educational abstraction designed to make the mechanism visible and interactive.

### Evidence classification

**Primary research paper — peer-reviewed computational neuroscience research.**

---

## 2. The Dragon Hatchling (BDH)

**Kosowski, A., Uznański, P., Chorowski, J., Stamirowska, Z., & Bartoszkiewicz, M. (2025).**
**"The Dragon Hatchling: The Missing Link between the Transformer and Models of the Brain."**

arXiv:2509.26507

Source: https://arxiv.org/abs/2509.26507

### Relevance to this project

The Dragon Hatchling (BDH) proposes a biologically inspired language-model architecture based on a scale-free network of locally interacting neuron-like particles.

The work is relevant to this project because it explores an alternative to the conventional Transformer view of sequence processing, connecting neural-network computation with biologically inspired structures and mechanisms. The paper describes BDH as combining theoretical structure and interpretability with Transformer-like performance.

### How the project uses this evidence

The BDH connection is used to explain why changing internal connections can be viewed as a computational memory mechanism.

The project's toy model uses a small matrix of synaptic weights that changes as inputs arrive. This provides an intuitive educational analogy for the broader idea of computation in which internal state changes as a sequence is processed.

However:

> **This project is NOT an implementation or reproduction of BDH.**

The project's 30-neuron network, hand-designed symbol representations, Hebbian update rule, decay parameter, and experiments are independently simplified for educational purposes.

### Evidence classification

**Primary research preprint — arXiv.**

The project uses BDH as research context and comparison rather than claiming to reproduce its architecture or reported results.

---

## 3. BDH-CQ: Recurrent Latent Reasoning

**Engdahl, B., Kosowski, A., Chorowski, J., Stamirowska, Z., Uznański, P., Jiang, J., Phadke, R., Kinas, R., & Zhong, R. (2026).**
**"BDH-CQ: In-Context Learning with Recurrent Latent Reasoning."**

arXiv:2608.09888

Source: https://arxiv.org/abs/2608.09888

### Relevance to this project

BDH-CQ extends the BDH direction toward recurrent latent reasoning and in-context learning.

The paper describes a system in which inputs presented during inference continuously update recurrent memory. The updated internal state is then used to solve a query through iterative computation in a latent space.

This is particularly relevant to the project's focus on **memory through changing internal state**. Instead of treating all useful information as something that must be stored in a separate external memory structure, recurrent computation can allow information from previous inputs to influence later computation.

### How the project uses this evidence

The project's educational simulation provides a much smaller and more interpretable demonstration of the general intuition:

```text
Input
  ↓
Activity
  ↓
Synaptic update
  ↓
Changed internal state
  ↓
Later input
  ↓
Recall influenced by previous experience
```

The simulation is **not BDH-CQ** and does not reproduce its recurrent latent reasoning architecture, training procedure, parameter count, or evaluation results.

### Evidence classification

**Primary research preprint — arXiv.**

The project uses BDH-CQ as a technical comparison and motivation for discussing inference-time recurrent memory.

---

## 4. Evidence Used by the Project's Own Experiments

The numerical results shown in this project come from the project's own simulation rather than being copied from the research papers.

The core model uses:

* 30 neurons in the main demonstration.
* 3 active neurons for each symbolic input.
* A Hebbian learning rate of 0.4 in the main experiment.
* A synaptic decay value of 0.08.
* A short activity trace to represent recent activity.
* Repeated co-activation to strengthen associations.
* Interference from unrelated inputs to demonstrate forgetting.

The main experiments examine:

1. **Learning followed by interference**

   * A repeated `cat → meow` association is learned.
   * Unrelated inputs are then presented.
   * The association weakens through decay and interference.

2. **Reinforced control**

   * The `cat → meow` association continues to be reinforced.
   * This provides a comparison against the interference condition.

3. **Competing associations**

   * `cat → meow` and `dog → bark` share the same network.
   * Both associations can be affected by subsequent activity.

4. **Neuron-pool sweep**

   * The simulation varies the number of neurons.
   * This explores how representational capacity affects the toy model's ability to preserve associations.

These results are **project-generated simulation results**, not results reported by the cited research papers.

---

## 5. Research vs. Project Evidence

To avoid overclaiming, the project separates external research evidence from results generated by the educational model.

| Evidence                                                            | Source                  | Status             |
| ------------------------------------------------------------------- | ----------------------- | ------------------ |
| STSP can support working-memory behavior                            | Kozachkov et al. (2022) | Published research |
| STSP networks showed greater robustness to network degradation      | Kozachkov et al. (2022) | Published research |
| STSP networks showed more brain-like activity                       | Kozachkov et al. (2022) | Published research |
| BDH uses a biologically inspired network architecture               | Kosowski et al. (2025)  | Research preprint  |
| BDH connects biological inspiration with language-model computation | Kosowski et al. (2025)  | Research preprint  |
| Inference-time inputs update recurrent memory in BDH-CQ             | Engdahl et al. (2026)   | Research preprint  |
| `cat → meow` association strengthens in the toy model               | This project            | Project simulation |
| Association weakens after unrelated inputs                          | This project            | Project simulation |
| Reinforcement preserves association strength                        | This project            | Project simulation |
| Neuron-pool sweep results                                           | This project            | Project simulation |

---

## 6. Important Scope and Limitations

The cited research supports the broader motivation for investigating synaptic plasticity and changing internal state, but it does **not** validate every behavior of this project's toy model.

In particular, the project should not be interpreted as demonstrating that:

* biological human short-term memory works exactly like this simulation;
* the 30-neuron model is biologically realistic;
* the project reproduces BDH;
* the project reproduces BDH-CQ;
* the measured association-strength values correspond to biological quantities;
* the toy model establishes the superiority of synaptic plasticity over Transformers.

The educational goal is narrower:

> **Repeated co-activation can modify a network's internal connections, allowing recent experience to influence later behavior without requiring a separate memory slot for every item.**

The interactive simulation is therefore best understood as a **mechanistic educational model**, while the cited papers provide the external scientific and technical context.

---

## 7. Project Source

Project repository:

https://github.com/t3rrible0ctopus/synaptic-plasticity-dataforge

The repository contains the implementation, experiments, exported results, and interactive frontend used by this project.

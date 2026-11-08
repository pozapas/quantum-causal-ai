---
title: Glossary
subtitle: Short definitions, ordered alphabetically
---

Definitions are deliberately short. Each lesson defines its terms again in context, with the assumptions that apply.

:::{glossary}
Amplitude
: A complex number attached to a possible outcome of a quantum state. The probability of the outcome in an ideal measurement is the squared magnitude of its amplitude (the Born rule).

Average treatment effect (ATE)
: The mean difference between the outcomes a population would have under treatment and under no treatment, $E[Y(1) - Y(0)]$.

Back-door criterion
: A graphical condition on a set of variables $Z$: no member of $Z$ is a descendant of $X$, and $Z$ blocks every path from $X$ to $Y$ that starts with an arrow into $X$. If it holds, adjusting for $Z$ identifies the effect of $X$ on $Y$.

Barren plateau
: A region of a variational circuit's parameter space where gradients are exponentially small in the number of qubits, which makes training by gradient descent impractical.

Bayes' rule
: $P(H\mid E) = P(E\mid H)\,P(H) / P(E)$. It updates the probability of a hypothesis $H$ after seeing evidence $E$.

Bell inequality
: A bound on correlations that every local hidden-variable model satisfies. Some measurements on entangled quantum states violate it.

Bloch sphere
: A geometric picture of single-qubit states: pure states lie on the surface of a unit sphere, mixed states inside it.

Causal discovery
: Inferring a causal graph, or a set of graphs that fit equally well, from data plus explicit assumptions such as the causal Markov condition and faithfulness.

Causal graph (DAG)
: A directed acyclic graph whose arrows represent direct causal influences among variables.

CHSH inequality
: The Clauser–Horne–Shimony–Holt form of a Bell inequality, $|S| \le 2$ for local hidden-variable models. Quantum mechanics allows up to $2\sqrt{2}$ (Tsirelson's bound).

Choi matrix
: A matrix that represents a quantum channel completely. The channel is completely positive exactly when its Choi matrix is positive semidefinite.

Classical shadow
: A compact classical description of a quantum state built from randomized measurements. It can estimate many properties of the state from relatively few measurements.

Collider
: A variable with two arrows pointing into it on a path, as $X \to C \leftarrow Y$. Conditioning on a collider can create an association between $X$ and $Y$ that is not causal.

Common cause
: A variable that influences two others. An unmeasured common cause (a confounder) can create correlation without direct causation between the two.

Complete positivity
: The property that a map stays positive when it acts on part of a larger system. Physical quantum channels are completely positive and trace preserving (CPTP).

Concurrence
: A measure of entanglement for two qubits, from 0 (not entangled) to 1 (maximally entangled).

Confounding
: Bias in an estimated causal effect caused by a common cause of treatment and outcome that the analysis does not account for.

Counterfactual
: A statement about what would have happened to the same unit under a different action, given what actually happened.

Density matrix
: A positive semidefinite matrix with trace one. It describes pure and mixed quantum states.

do-operator
: Pearl's notation $do(X = x)$ for an intervention that sets $X$ to $x$ by an external action, cutting the arrows into $X$ in the causal graph.

Entanglement
: A joint quantum state is entangled when it cannot be written as a probabilistic mixture of product states.

Entropy
: A measure of uncertainty. Shannon entropy applies to probability distributions; von Neumann entropy, $-\operatorname{Tr}\rho\log\rho$, applies to density matrices.

Expectation value
: The probability-weighted average of measurement outcomes, $\langle A \rangle = \operatorname{Tr}(\rho A)$ for a quantum observable $A$.

Faithfulness
: The assumption that every conditional independence in the data follows from the causal graph and is not due to an exact cancellation of effects.

Front-door criterion
: A graphical condition that identifies a causal effect through a fully observed mediator even when the treatment and outcome share an unmeasured common cause.

Hermitian matrix
: A matrix equal to its conjugate transpose. Its eigenvalues are real; quantum observables are represented by Hermitian operators.

Identification
: Showing that a causal quantity can be computed from the distribution of observed data under stated assumptions.

Indefinite causal order
: A situation, described by process matrices, in which the operations cannot be assigned a definite order, nor any probabilistic mixture of definite orders (causal nonseparability). A random but classical choice of order is not indefinite; the quantum switch with its control in superposition is the standard example.

Interference
: The effect produced when amplitudes for different paths add, so that outcome probabilities depend on relative phase.

Intervention
: An action that sets or changes a variable from outside the system, as opposed to passively observing it.

Kraus operators
: Matrices $K_k$ that represent a quantum channel as $\rho \mapsto \sum_k K_k \rho K_k^\dagger$, with $\sum_k K_k^\dagger K_k = I$ for trace preservation.

Parameter-shift rule
: A rule that computes exact gradients of many variational quantum circuits from the circuit's outputs at two shifted parameter values.

Partial trace
: The operation that gives the state of a subsystem from the state of a larger joint system.

Process matrix
: An operator that describes how local quantum operations in several laboratories are connected, without assuming a fixed causal order between them.

Quantum causal model
: A causal model in which the nodes are quantum systems or quantum operations and the mechanisms are quantum channels, generalizing classical structural causal models.

Quantum channel
: A completely positive, trace-preserving linear map that describes how a quantum state can change, including noise.

Quantum switch
: A process in which a control qubit determines the order in which two operations act on a target; with the control in superposition, the order is indefinite.

Qubit
: A two-level quantum system, the quantum counterpart of a bit.

Randomized controlled trial
: An experiment in which treatment is assigned by a random mechanism, which balances measured and unmeasured characteristics between groups on average.

Structural causal model (SCM)
: A set of equations, one per variable, that determine each variable from its direct causes and an exogenous noise term, together with a distribution over the noise terms.

Superposition
: A quantum state that is a linear combination of other states, such as $\alpha|0\rangle + \beta|1\rangle$.

Variational quantum algorithm
: A hybrid method in which a classical optimizer tunes the parameters of a quantum circuit to minimize a cost estimated from measurements.
:::

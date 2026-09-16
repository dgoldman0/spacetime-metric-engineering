# Active Rail Handoff: Gate Test 1 — Le-Style Boundary Classification of the Actual beta075 Source Stack

## Purpose

Before spending effort on the Comer-style constitutive reconstruction of the junction medium or the support reservoir, test whether the **current beta075 source architecture actually closes at its interfaces**. The immediate question is whether the present source stack

\[
S_0 \rightarrow J \rightarrow T_{\rm support} \rightarrow \text{exterior}
\]

has the same kind of boundary pathology An T. Le found in smooth finite-thickness radial-tension/warp-shell sources: a healthy-looking bulk followed by an edge where density/enthalpy dies faster than derivative-generated stress or momentum flux. If that happens in the **full beta075 tensor** and survives numerical refinement, it is a more basic problem than the still-open constitutive interpretation of \(J\) or the support stroke.

Freeze the current beta075 geometry and source decomposition for this test. Do **not** retune the rail while diagnosing it. The goal is to find out what the existing design is doing.

### Project context the paper-analysis work adds

The current rail source anatomy is already close enough to Le's setup to make this test meaningful:

- \(S_0\) is dominated by a standing, nearly constant-flux radial-tension/string-like component, approximately \(p_l\simeq-\rho\), with small transverse stress/current through much of its bulk.
- The junction \(J\) carries the more difficult endpoint behavior: anisotropy, angular response, current relaxation/regulation, a small enthalpy cushion, and exchange with the support subsystem.
- The support sector was introduced through conservation accounting and now carries stored state/history and derivative-generated stress.
- The unresolved physical question is therefore concentrated at the **interfaces** between source roles, especially where the last nonzero source is tapered into the exterior.

The direct gate is: **does the composite source actually cure the edge, or merely move it outward one layer at a time?**

---

## Why Le's boundary result is the right diagnostic template

Le's 2026 boundary-cost paper studies source-consistent positive-energy warp shells and finds that the bulk can satisfy the intended energy-condition behavior while the smooth source-to-vacuum transition fails. In the moving cases, a key failure is a **flux-dominated Hawking–Ellis Type-IV layer** in the smoothing tail. A related boundary deficit also persists in a static/zero-shift control, showing that part of the problem is tied to the transition geometry itself rather than only to motion.

For a spherically symmetric stress tensor with radial energy current, the time-radial block can be monitored with

\[
\Delta_{\rm rad}=(\rho+p_l)^2-4j_l^2.
\]

When \(\Delta_{\rm rad}<0\), the time-radial mixed tensor has a complex-conjugate eigenvalue pair: the local source is Type IV rather than an ordinary Type-I material rest-frame stress tensor. This is particularly relevant to \(S_0\), because \(p_l\simeq-\rho\) makes \(\rho+p_l\) intrinsically small. A current that would be modest in a normal fluid can therefore dominate the available radial enthalpy near a taper.

Use \(\Delta_{\rm rad}\) as a fast diagnostic, but perform the **full Hawking–Ellis classification from the mixed tensor \(T^\mu{}_{\nu}\)** as the authoritative result. The degenerate \(\Delta_{\rm rad}=0\) case must be distinguished properly (Type II/degenerate cases are possible), and all eigenvectors should be checked for causal character.

---

## Implementation plan

### 1. Evaluate the actual source stack at every grid point

Construct and retain, at identical \((\sigma,\ell)\) points,

\[
T^{(0)}=S_0,
\]

\[
T^{(1)}=S_0+J,
\]

\[
T^{(2)}=S_0+J+T_{\rm support},
\]

and the final physical tensor

\[
T^{\rm total}=T^{(2)}+T^{\rm any\ remaining\ exterior/transfer\ sector}.
\]

If the current implementation uses additional named residual/correction tensors, include them explicitly and document the order in which they are added.

The **partial sums are diagnostic**. They show which layer creates, removes, or displaces an edge pathology. The Hawking–Ellis type of a nonconserved bookkeeping component should not be treated as a physical verdict. The primary physical verdict belongs to the complete \(T^{\rm total}_{\mu\nu}\).

For every partial sum and the total tensor record:

- \(\rho\), \(j_l\), \(p_l\), \(p_\Omega\);
- \(\rho+p_l\);
- \(\Delta_{\rm rad}=(\rho+p_l)^2-4j_l^2\);
- eigenvalues/eigenvectors and Hawking–Ellis type of \(T^\mu{}_{\nu}\);
- NEC/WEC/DEC margins where the type permits the usual rest-frame interpretation;
- a transverse/edge-stress diagnostic such as \(|p_\Omega|/\max(|\rho|,\epsilon)\);
- source magnitude and radial derivatives of the tapering fields.

Also plot

\[
\chi_j=\frac{2|j_l|}{|\rho+p_l|+\epsilon}
\]

for intuition. \(\chi_j>1\) marks the same flux-dominance tendency as \(\Delta_{\rm rad}<0\), but the discriminant and full eigensystem remain the real classifiers.

### 2. Identify interfaces from the source profiles themselves

Do not diagnose only at hard-coded coordinates. Define masks for the actual transition regions using source weights/gradients: the outer taper of \(S_0\), the \(S_0/J\) overlap, the outer edge of \(J\), the \(J/T_{\rm support}\) overlap, and the final support/exterior taper. Record where each source weight falls through useful fractions (for example 90%, 50%, 10%) and where its gradient is maximal.

For each interface, report the location and value of:

- minimum \(\Delta_{\rm rad}\);
- worst Hawking–Ellis class;
- minimum NEC/DEC margin;
- maximum \(|p_\Omega|\) and normalized transverse stress;
- maximum \(|j_l|\);
- maximum relevant source derivative.

This makes an **edge migration test** possible: if adding \(J\) cures the \(S_0\) taper but the same signature reappears at the outer edge of \(J\), the problem has been displaced rather than solved.

### 3. Separate numerical refinement from physical taper refinement

Run two distinct studies.

**A. Numerical convergence:** hold every physical source profile and transition width fixed while taking \(h\rightarrow0\). A pathology that is real should converge in location and invariant magnitude/classification. A layer that appears only because a derivative is under-resolved should change or disappear with grid refinement.

**B. Physical-width sweep:** only after numerical convergence, vary the actual taper widths. Le's result is specifically about finite smooth transitions and how derivative-generated stresses behave near their tails. Track both peak and integrated burdens. If a layer narrows while its peak grows, also record an integral such as

\[
I_{\rm edge}=\int_{\rm edge} |T_{\mu\nu}|\,d\ell
\]

(or the project's preferred invariant/volume-weighted equivalent) to distinguish a converging thin-shell/distributional limit from an outright divergent source requirement.

### 4. Run a matched holding/static control

Repeat the interface classification on the closest existing **matched holding / beta-off / zero-current control** while keeping the standing support geometry and taper structure as identical as possible.

Interpretation:

- bad edge in both holding and active cases -> primarily a termination/transition cost;
- edge is Type I in holding but becomes Type IV only during active current -> Le-like flux/tilt failure;
- partial tensor is Type IV but the completed total tensor is Type I with stable margins -> successful composite closure;
- the bad layer follows whichever component is currently outermost -> source-stack migration problem.

---

## The outermost-boundary test is mandatory

Do not stop after showing that \(J\) repairs \(S_0\), or that \(T_{\rm support}\) repairs \(J\). Continue the same classification through the **last nonzero source into the exterior**.

This is the central gate. If every added material layer makes the interior interface healthy but reproduces the same pathology at its own outer taper, beta075 has not yet closed physically. The project then needs an explicit outer matching/transfer mechanism or a different asymptotic source architecture before detailed constitutive reconstruction is worth doing.

Le's separate *Steering a warp drive without exotic matter* paper is relevant here because it makes energy-momentum transfer explicit: its confined material shell changes momentum through an exterior radiative channel rather than asking a finite material source to make the transferred momentum simply vanish at its boundary. The active rail need not copy the photon-rocket construction, but the structural lesson is important: **exchange flux and material support are different physical roles**.

---

## Required deliverables and decision gate

Produce:

1. interface maps for \(T^{(0)},T^{(1)},T^{(2)},T^{\rm total}\);
2. Hawking–Ellis classification maps and \(\Delta_{\rm rad}\) maps;
3. an interface table for holding vs active beta075;
4. numerical-convergence plots at fixed physical widths;
5. physical taper-width sweeps after convergence;
6. an edge-migration table showing where the worst invariant/classification sits after each source layer is added;
7. a short final verdict using one of these categories.

**PASS — proceed to constitutive tests:** the complete beta075 tensor is free of a refinement-stable Type-IV/degenerate edge pathology at all real interfaces, including the outermost boundary, and no transverse/derivative burden diverges as an artifact of source termination.

**INTERNAL CLOSURE FAILURE — redesign before Comer inversion:** \(S_0\rightarrow J\) or \(J\rightarrow T_{\rm support}\) retains a physical edge pathology in the total tensor.

**OUTER CLOSURE FAILURE — solve the exterior architecture first:** internal layers cure one another, but the pathology follows the final source-to-exterior boundary.

**NUMERICAL/REPRESENTATION ISSUE — rerun before physics conclusions:** classification does not converge under grid refinement or depends materially on a bookkeeping decomposition while the total tensor remains stable.

Only a PASS makes the Comer-style inverse constitutive tests the next priority.

---

## External papers to load into project context

1. **An T. Le (2026), “On the boundary cost of source-consistent warp shells.”** arXiv:2605.25417.  
   https://arxiv.org/abs/2605.25417  
   **Direct relevance:** primary template for the interface test; source-first shell construction, source-to-vacuum boundary deficit, frame-independent energy-condition diagnostics, and Type-IV behavior in the smoothing tail.

2. **An T. Le (2026), “Steering a warp drive without exotic matter.”** arXiv:2606.22531.  
   https://arxiv.org/abs/2606.22531  
   **Direct relevance:** explicit separation of material support from energy-momentum transfer through an exterior channel; useful if the beta075 problem migrates to the outermost boundary.

3. **G. L. Comer, N. Andersson, T. Celora, and I. Hawke (2026), “Action based approach to dissipative relativistic fluid systems.”** arXiv:2606.17686.  
   https://arxiv.org/abs/2606.17686  
   **Next-stage relevance:** two-current particle/entropy action, entrainment, relative-flow variables, and causal Cattaneo-type heat transport. This is the main template for physicalizing \(J\) if the boundary gate passes.

4. **N. Andersson, T. Celora, G. L. Comer, and I. Hawke (2024), “A Field-Theory Approach for Modeling Dissipative Relativistic Fluids.”** *Entropy* **26**(8), 621.  
   https://doi.org/10.3390/e26080621  
   Open-access article: https://www.mdpi.com/1099-4300/26/8/621  
   **Background for the next stage:** matter-space geometry, proper-time derivatives of internal material metrics, action-derived bulk/shear dissipative response, and evolution of transport coefficients along material worldlines.

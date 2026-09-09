# Screened scalar condensates for rail support

## Material model and reference solutions

The Ishihara–Ogawa construction supplies a concrete material alternative to the charged wall and Fermi atmosphere. A complex matter field, a complex Higgs field, and a common gauge field form localized configurations. Their opposite charge densities screen the total electric charge, while the scalar potential and gradients determine the material boundary. Thus the same action specifies the material density, screening, and mechanical stress. The published families include approximately uniform balls and hollow condensate shells [1, 2]; their gravitational extension supplies the coupled Einstein–matter equations [3].

In units with the Higgs vacuum amplitude \(v=1\), the action is

\[
\mathcal L=-|D\psi|^2-|D\phi|^2-
\frac{\lambda}{4}(|\phi|^2-1)^2-\mu|\psi|^2|\phi|^2
-\frac14F_{ab}F^{ab}.
\]

The stationary ansatz uses \(\psi=u(r)e^{i\omega t}\), \(\phi=h(r)\), and \(A_t=a(r)\). The metric is

\[
ds^2=-\sigma^2N\,dt^2+N^{-1}dr^2+r^2d\Omega^2,
\qquad N=1-2m/r.
\]

Here radius and mass are measured in units of \(v^{-1}\), fields in units of \(v\), and stress in units of \(v^4\). The independent gravitational parameter is \(g=Gv^2\). The registered couplings are \(\lambda=1\), \(\mu=1.4\), and either \(e=1\) for the uniform reference or \(e=0.1\) for the hollow reference.

Define the positive constituent energies

\[
K=\frac{(\omega-ea)^2u^2+e^2a^2h^2}{\sigma^2N},\quad
D=N(u'^2+h'^2),\quad
V=\frac\lambda4(h^2-1)^2+\mu u^2h^2,\quad
E=\frac{a'^2}{2\sigma^2}.
\]

The complete orthonormal tensor follows directly from the action:

\[
\rho=K+D+V+E,\qquad p_r=K+D-V-E,\qquad
p_t=K-D-V+E.
\]

Consequently, \(\rho+p_r=2(K+D)\) and \(\rho+p_t=2(K+E)\). This classical material obeys the null and dominant energy conditions. Its role in the rail construction is supporting material alongside the quantum sector responsible for the required negative null stress.

### Reproduction and tensor checks

The flat controls impose regular derivatives at the origin and the Higgs vacuum at large radius. A coarse solve at the published, rounded frequency locates each branch. Refinement then fixes the conserved matter number and solves for the frequency. This removes the large radius sensitivity of the hollow shell to rounding in its quoted frequency. The retained reduced numbers \(\mathcal N/(4\pi)\) are 58,000 and 85,600, respectively.

| Quantity | Uniform reference | Hollow reference |
| --- | ---: | ---: |
| Frequency \(\omega\) | 1.1700008 | 0.8108910 |
| Energy / free-particle energy | 0.989303 | 0.685378 |
| Radius containing 50% of the energy | 71.8601 | 90.1305 |
| Radii containing 5% and 95% | 33.3528, 91.5390 | 82.0673, 97.3765 |
| \(\int p_t\,dr/\int\rho\,dr\) | 0.000456877 | 0.00192324 |
| Minimum local \(p_t\) | −0.001068 | −0.392795 |
| Maximum local \(p_t\) | 0.000245 | 0.164387 |

Both references reproduce the expected material localization and charge screening. Their energies lie below the energy of the same number of free matter particles. That comparison establishes binding against dissociation into those particles; the spectrum of coupled material and gravitational perturbations remains a separate calculation.

The local stress has both tension and compression. In particular, the negative angular pressure in the hollow profile occupies only part of its material layer. The complete radial tensor satisfies

\[
p_r'=\frac{2}{r}(p_t-p_r),\qquad
\int_0^\infty r^2(p_r+2p_t)\,dr=0,\qquad
\int_0^\infty p_t\,dr=\frac12\int_0^\infty p_r\,dr.
\]

The last identity follows by integrating \(r p_r'=2(p_t-p_r)\) and using the vanishing boundary term. Both retained column pressures are positive. Therefore selecting only the negative local portion would omit part of the same condensate's mechanical stress.

For comparison, the previously derived thin junction at \(R=6.8\), \(b=1.75\), requires \(P/\Sigma\ge b/[2(R-b)]=0.173267\). The unmodified flat reference columns are substantially below that value, and a common material normalization preserves their ratios. This comparison motivates solving the loaded, finite gravitational configuration with its boundary conditions. The finite profiles have curvature and internal stress structure which a column ratio alone cannot represent.

![Fields, complete stresses, and charge densities of the reproduced reference condensates.](data/screened_condensate/condensate_reference_profiles.png)

### Homogeneous fluid limit

The locally screened stationary branch has \(ea=[(\mu-\lambda)\omega+\sqrt{\mu(2\lambda+\mu)\omega^2-\mu\lambda(4\mu-\lambda)}]/(4\mu-\lambda)\), \(h=(\omega-ea)/\sqrt\mu\), and \(u^2=ea(\omega-ea)/\mu\). It reaches zero pressure at \(\omega=\sqrt{2\sqrt{\lambda\mu}-\lambda}=1.1689448\). A narrow interval of negative bulk pressure extends toward the stationary-branch endpoint at 1.1631600.

The rail boundary demands negative radial pressure. For an isotropic positive-density static fluid with positive enclosed mass, the TOV equation gives \(p'=-\rho m/(r^2N)<0\) at a zero-pressure surface. A solution beginning with negative pressure on the inside cannot first reach that free surface by increasing outward through zero. Accordingly, the scalar gradients and gauge stresses are essential to a finite condensate construction surrounding this boundary. They provide the anisotropic terms absent from a homogeneous fluid equation of state.

### Reproducibility

The retained eight runs use tolerances \(10^{-5},10^{-7},10^{-9}\) and an outer-domain extension from 250 to 300. All charge cancellation errors are below \(2.8\times10^{-9}\), and the integrated virial errors are below \(1.0\times10^{-8}\). Nine unit and reference tests check the stationary equations, thermodynamic derivative, null contractions, gravitational limits, charge cancellation, and integrated stress balance. The independent finite-difference stress-conservation check is limited by its sampling interval; the CSV records it separately from the collocation residual.

The four-worker reference run took 3.02 seconds and retained 0.78 MB. Its inputs and outputs are hashed in [the manifest](data/screened_condensate/manifest.json), with detailed results in [the reference table](data/screened_condensate/reference_checks.csv). Reproduction from the repository root:

```bash
PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python toolkit/adm_harness_cli/scripts/run_screened_condensate.py --workers 4 --output /tmp/rail-condensate-reference
PYTHONPATH=toolkit/adm_harness_cli OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 pytest -q toolkit/adm_harness_cli/tests/test_screened_condensate.py
```

## References

1. H. Ishihara and T. Ogawa, “Homogeneous Balls in a Spontaneously Broken U(1) Gauge Theory” (2019), [arXiv:1901.08799](https://arxiv.org/abs/1901.08799).
2. H. Ishihara and T. Ogawa, “A Variety of Nontopological Solitons in a Spontaneously Broken U(1) Gauge Theory — Dust Balls, Shell Balls, and Potential Balls” (2021), [arXiv:2103.13732](https://arxiv.org/abs/2103.13732).
3. T. Ogawa and H. Ishihara, “Gravastars as nontopological solitons” (2024), [arXiv:2409.07818](https://arxiv.org/abs/2409.07818).

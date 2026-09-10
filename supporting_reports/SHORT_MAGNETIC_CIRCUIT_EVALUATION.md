# Short magnetic circuits as a rail source

Date: 9 September 2026.

## Registered adaptation

This evaluation adapts the channel mechanism in
[Maldacena, Milekhin and Popov](https://arxiv.org/html/1807.04726v3), sections
2.3, 5.2 and 7. Magnetic flux supplies light longitudinal modes and their
closed vacuum path supplies Casimir stress. The published near-extremal
geometry is replaced here by the repaired native static rail at phase 0.745.
The existing backbone, angular material and transport retain their roles.

The [long-loop screen](LONGITUDINAL_QUANTUM_SOURCE_LITERATURE.md) motivates
shorter circuits assigned to individual spatial regions. This test includes
each circuit's outgoing segment, return segment and bends. It grants zero
additional radial-null cost to the current-carrying host, confinement boundary
and mechanical support, before attempting their construction.

The candidate is a thin flux tube with constant field magnitude \(B\), flux
\(2\pi q\), and cross-sectional area \(S=2\pi q/B\). The gauge action is
\(-F^2/(4e^2)\), with unit-charge massless Dirac species. The optimistic
longitudinal vacuum has total central charge \(c=qN_f\), the most negative
cylinder ground state, and its Weyl anomaly on the actual loop clock. Light
mode survival, holonomy, finite transverse structure and a full Maxwell and
host solution remain additional conditions. The channel count is granted
through the bends for this necessary source comparison.

## Curved path and radial stress

In the spatial metric \(dl^2+R(l)^2d\Omega^2\), a loop follows a meridian.
Two radial legs of proper length \(D\) sit at angular offsets
\(\pm\delta\), where \(\delta=r_b/R(l_c)\). Two smooth caps close the loop:

\[
l=l_c\pm D/2\pm r_b\cos u,\qquad
\theta=\pm\delta\sin u,\qquad -\pi/2\leq u\leq\pi/2.
\]

Their proper arclength, radial tangent \(t_r=dl/ds\) and spatial curvature
are computed with the rail metric. The tangent is continuous at the joins;
the piecewise curvature has finite jumps. The registered paths have
\(\delta\leq0.25\), keeping the meridian construction within a local angular
strip. Each complete loop has optical circumference \(L=\oint ds/A\).

The magnetic tensor supplies

\[
\rho_B+p_{r,B}=\frac{B^2}{e^2}(1-t_r^2).
\]

Thus straight radial field segments saturate radial null stress, while the
turns contribute a positive load. The quantum tensor per unit central charge
along the path is

\[
\rho_2=-\frac\pi{6L^2A^2}+\frac{2a_{ss}+a_s^2}{24\pi},\qquad
p_2=-\frac\pi{6L^2A^2}-\frac{a_s^2}{24\pi},\qquad a=\log A.
\]

Angular averaging of localized tubes converts the rail opening weight to
\(W=1/(AR)\) per unit tube length. Integration by parts around the closed
loop gives its quantum opening

\[
B_Q=\eta c\left\{\frac\pi{6L^2}
\oint\frac{1+t_r^2}{A^3R}ds
-\frac1{24\pi}\oint Wt_r^2
\left[a_l^2(3-t_r^2)+2a_l\frac{R'}R\right]ds\right\}
\equiv\eta c\,C.
\]

The full magnetic contribution is
\(B_B=-\eta(2\pi qB/e^2)J\), where
\(J=\oint W(1-t_r^2)ds\). A helpful loop requires
\(N_fe^2>2\pi BJ/C\), when \(C>0\). This tests the actual signed opening
of the proposed circuit, independently of assigning the remaining bulk load.

## Field and mode controls

The tube radius \(r_t=\sqrt{2q/B}\) stays below both its bend-radius allowance
and its separation allowance. With \(\gamma=3,5\), the field satisfies

\[
r_t\leq\min\left[\frac1{\gamma\kappa_{\max}},
\frac{\delta R_{\min}}\gamma\right],\qquad
\frac{\pi}{LA_{\min}\sqrt{2B}}\leq0.1.
\]

Here \(\kappa_{\max}\) is the largest proper spatial curvature of the loop.
The last inequality separates its lowest longitudinal frequency from the
first Landau excitation. These are geometric scale checks for an optimistic
one-dimensional approximation; they leave the full transverse spectrum open.
The cheapest allowed constant \(B\) enters the source comparison.

The registered centers have native coordinates
\(-6,-4,-2.5,-1,0,1,2.5,4,6\); leg lengths are
\(D=0,0.25,0.5,1,2,4,8,16,32,64,128\), and cap scales are
\(r_b=0.05,0.1,0.25,0.5,1\). Invalid angular strips are excluded geometrically.
Fluxes \(q=1,8,24\), equal-charge species counts \(N_f=1,8,54\), and gauge
couplings \(e=0.1,0.3,1\) define the comparison ladder. The 54-species case
is a toy equal-charge comparison; matching Standard Model charges also changes
the gauge-loop coefficients. The quantity \(N_fe^2/(16\pi^2)\) records the
size of the gauge-loop expansion; values through 0.1 define the preferred
perturbative subset for this screen.

An exact flat circular loop gives
\(B_Q/|B_B|=N_fe^2/(16\pi^2Br_b^2)\). Flat capsules, constant clock rescaling,
curved quadrature refinement and the independent form of the anomaly integral
check the calculation. Four workers may evaluate independent loop geometries.
The allowance is 300 seconds per run and 10 MB of retained numerical evidence.
The comparison proceeds after the finite-cavity result has been recorded.

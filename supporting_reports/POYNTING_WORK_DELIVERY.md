# Finite electromagnetic work delivery on the active rail

## Registered question and architecture

This investigation measures whether supplying electrical work during the
scheduled late operation reduces the finite local reserve identified in the
[converter evaluation](REGENERATIVE_CONVERTER_EVALUATION.md). It retains the
connected pressure fluid, radial electric storage field, thermal receiving
inventory, prescribed material worldlines, and separate standing-support
reaction role. The protected packet and time-dependent metric remain those
of the active rail. The first comparison covers x in [-2.1,-0.5] and service
time s in [0,1.285]. Earlier preparation and subsequent reset retain their
own service constraints.

The work route has finite input and recovery ports at the patch boundaries.
Its initial travelling energy and all boundary energy transfers are counted.
The thermal receiver retains the earlier finite inventory calculation. An
external electrical supply changes the work inventory equation alone;
receiver heat storage, entropy, and terminal reactions remain physical duties.

The causal calculation grants reversible scheduled taps with the nominal
98% conversion efficiency and full electrical recovery already used in the
previous evaluation. Forward and recovery waves occupy distinct channels.
This first gate supplies a necessary geometric-optics stress and reaction
calculation. Plasma current closure, transverse confinement, actual converter
mass, and exterior supply construction require additional tensors.

## Literature basis and adaptations

[Lovelace and Kronberg (2013)](https://arxiv.org/abs/1212.0577) supply the
transmission-line framework: electromagnetic energy, voltage, current,
impedance, time-dependent waves, loads, and reflection. Their reflected-wave
calculation identifies magnetic-insulation loss and particle acceleration as
a failure mode. The rail adaptation uses scheduled finite work ports in its
prepared support plant. The astrophysical generator and jet geometry are
replaced by the rail's own metric and boundary conditions.

[Gralla and Jacobson (2015)](https://arxiv.org/abs/1503.03848) give exact
force-free travelling-field solutions with longitudinal guide fields and
explicit confinement restrictions. Their drift velocity is the minimum
velocity of a frame with vanishing electric field. A propagating disturbance
can consequently have a much faster phase velocity than its minimum material
drift. Guide-field energy and its external support determine the cost of
that separation. The paper's flat-space solutions supply local field
relations; the propagation screen below uses the scheduled curved background.

## Causal wave equation and counted ports

Use the existing metric

    ds^2 = -alpha^2 ds^2 + B^2(dx+beta ds)^2 + R^2 dOmega^2.

For direction sigma=+1 or -1, a wave has orthonormal stress
(mu,mu,sigma mu,0), with mu nonnegative. Let D_wave=B R^2 mu,
v_sigma=-beta+sigma alpha/B, and v=B beta/alpha be the prescribed material
velocity. Its energy equation with a positive absorbed material-rest power q is

    partial_s D_wave + partial_x(v_sigma D_wave)
      = (alpha K_l - sigma alpha_x/B) D_wave
        - alpha B R^2 q/[Gamma(1-sigma v)].

The Doppler factor follows from projecting the null exchange four-force onto
the material rest frame. Emitted recovered power has the opposite sign.
The least prepared absorption solution has zero future inventory and zero
outgoing wave at its downstream boundary. Integrating that problem backward
determines both the necessary initial wave energy and its scheduled input.
Recovery evolves forward from empty initial and incident states.

The numerical method is a conservative finite-volume scheme with limited
linear reconstruction and SSP RK2 time stepping. Its positivity follows from
positive source terms in the chosen integration direction and a bounded CFL.
Independent spatial resolutions and analytic transport controls measure
numerical error. Each interval records boundary transfer, geometric work,
absorbed or emitted power, and the inventory balance.

Local tap momentum follows the same null four-force: absorbing rest power q
delivers radial rest force sigma q. The thermal inventory carries its own
holding force. Their combined force is compared with the archived endpoint
requirement; the standing plant receives the remaining mechanical duty.

## Guide and storage selection gates

A single travelling wave of rest-frame energy u_wave has E^2=B_wave^2 in
units c=1. Requiring minimum plasma drift at most v_d gives

    u_guide >= (v_d^-2-1) u_wave/2.

The comparisons v_d=0.2, 0.5, and 0.8 expose the velocity/stress tradeoff;
they represent operating comparisons rather than universal feasibility caps.
A flux-conserving radial guide has u_guide=H_guide/R^4 with constant H_guide
on each unbranched leg. Its maximum required flux across time and position
sets the prepared guide energy. Transverse magnetic return and end-turn
stress remain additional physical costs. An instantaneous local guide bound
is retained separately from that constant-flux construction.

For a coherent reflected voltage amplitude fraction r, the worst phase gives

    u_guide/u_incident >= [(1+r)^2/v_d^2-(1-r)^2]/2.

This provides a load-matching sensitivity before selecting switching hardware.
The principal calculation grants matched taps and counts recovered work in a
separate route, preserving the distinction between intended recovery and
unwanted reflection.

A useful continuation must reduce local electrical inventory while retaining
a quantified field, receiving, and mechanical burden. Any positive result at
this gate precedes the complete source comparison with exterior supply,
plasma, converter, confinement, and the independently calculated quantum
stress. The main technical disclosure remains the established design record.

# Stage II Beta075 Service-Rating Ladder Diagnostic

Status: live working report, not yet committed. This report is being kept open
so the V=10 boundary-map result can be added into the same narrative record.

## Purpose

The sealed V=5 Stage II package is the current nominal service-rating result.
This diagnostic asks whether the same beta075 source-family construction behaves
coherently away from nominal service when the source manifest is regenerated
fresh at two comparison ratings:

- `V=2.5`, the half-nominal comparator.
- `V=10`, the double-nominal boundary finder.

The standard for these comparison runs is intentionally stricter than a scaled
stress estimate. Each rating must rebuild the actual source-family ladder from
its own source ledger. A scaled V=5 projection is not admissible as
physical-source evidence.

## Current Result Snapshot

`V=2.5` is not sealed. It is source-safe and covariantly coherent, but the
current endpoint medium/support closure basis misses the half-load service point
by enough that the run must be treated as a diagnostic failure, not as a
half-nominal capstone input.

That result is not a hard physical obstruction. The failure is concentrated in
finite closure/fit quality, while the live-packet safety, boost, tensor identity,
localization, angular support exclusion, and live-tail exclusion remain clean.
The most likely interpretation is that the present medium/support ansatz is
tuned narrowly around the V=5 operating point and needs an explicit
service-rating dependence before it can claim a family result.

`V=10` has failed source safety, as expected for a double-nominal boundary
probe. Its downstream diagnostic map was continued through covariant and
support-total closure. The downstream story is useful but not promotional:
formal tensor identity/localization remains coherent, while medium/support
closure shows the same non-V5 calibration debt seen at V=2.5.

## V=2.5 Ladder

Run root:

`toolkit/adm_harness_cli/runs/stage2_external/beta_collar_generator_beta075_p003_mid_v2p5_dense377x241`

The source manifest was cloned from the beta075 V=5 manifest with only the
service rating changed to `V=2.5`. The dense source ledger completed at the same
`377 x 241` grid shape used by the sealed dense V=5 ladder.

### Source Safety

The half-nominal source ledger is live-packet safe:

- `positive_packet_norm_live = 0`
- `max_packet_norm_live = -6.333722528629708`
- `live_points = 966`

This is an important negative result in the good sense: the lower-service run
does not reveal a hidden packet causal-margin problem. Whatever fails later is
not caused by live packet-norm clipping, live-row activation, or direct causal
poisoning of the passenger packet region.

### Source-Family Construction

The following upstream construction stages completed:

- component/source assignment
- radial string-cloud replacement
- intermediate source model
- structured endpoint-J source fit
- endpoint-J closure component

So the half-nominal comparison does not fail at component existence or at the
basic source decomposition level. The same qualitative source-family machinery
can be built at V=2.5.

### Medium Field Closure Failure

The first hard promotion failure occurs at endpoint medium field closure:

- `field_closure_status = constrained_medium_field_closure_watch`
- `passes_constrained_field_closure = False`
- `worst_normalized_l1_error = 0.17851321189504593`
- `worst_angular_watch_l1_error = 0.1715121410982296`
- `max_angular_residual_to_source_ratio = 0.08049566412060921`

Those are too large for the current V=5-tuned closure gate. The supporting
quantities, however, are not broadly pathological:

- `max_abs_coefficient = 0.4669524607117023`
- `regulator_to_source_abs_ratio = 0.039726327825466486`
- `regulator_boundary_gradient_to_source_ratio = 0.008225662450444848`
- `p99_heat_flux_ratio = 0.9751026188339593`
- `p01_transport_margin = 0.024897381166040483`
- `max_abs_boost_velocity = 0.9836869043593697`
- `live_rows = 0`
- `regulator_live_rows = 0`
- `boost_superluminal_or_nan_rows = 0`
- `max_conservation_burden_delta = 0.0005558398899899192`

This pattern matters. It is not saying the medium becomes superluminal, leaks
into live rows, loses conservation control, or requires absurd coefficients. It
is saying the finite constrained medium closure basis is a poor match for the
half-load residual shape under the current service-independent calibration.

### Covariant Audit Follow-Up

Because the medium closure failure looked like a fit-quality failure rather than
a tensor-identity failure, the covariant audit was run as a diagnostic follow-up.
It passed:

- `passes_covariant_identity_audit = True`
- `projection_reconstruction_pass = True`
- `max_projection_linf_error = 6.938893903907228e-17`
- `projection_error_to_source_ratio = 1.0384221363055549e-16`
- `boost_subluminal_pass = True`
- `max_abs_boost_velocity = 0.9836869043593696`
- `mixed_eigen_real_pass = True`
- `max_mixed_eigen_imag = 0.0`
- `exchange_localization_pass = True`
- `outside_allowed_divergence_fraction = 0.0035505288579735362`
- `live_divergence_fraction = 0.0028655163351321406`

This is the strongest reason not to overread the V=2.5 closure failure as a
physics wall. The regulated medium variables still lift to a coherent spacetime
stress tensor, the ADM projections reconstruct, the mixed eigenstructure remains
real, the boost stays subluminal, and the divergence is localized to the allowed
endpoint/support exchange masks.

### Support-Stroke And Total Closure Follow-Up

The support-stroke exchange fit also fails as a watch/fail diagnostic:

- `passes_support_stroke_exchange_fit = False`
- `best_normalized_active_abs_PF_l1_error = 0.5180760517875904`
- `best_normalized_allowed_abs_PF_l1_error = 0.42542447789668925`
- `best_active_coordinate_l2_error_ratio = 0.52731594580926`
- `best_allowed_coordinate_l2_error_ratio = 0.42435863462313994`
- `best_max_abs_coefficient = 4.194065143284104`
- `best_effective_coefficient_count_total = 15446.789566740676`

The failure is close to the configured active P/F and coefficient gates, not a
localization failure:

- `best_outside_tail_fraction = 1.913439143581238e-05`
- `best_live_tail_fraction = 0.0`
- `best_high_psi_source_fraction = 0.00039410038212481674`

The total support closure follows the same pattern:

- `passes_support_total_closure = False`
- `active_closure_residual_to_endpoint_l2_ratio = 0.5273159458092594`
- `local_max_closure_residual_to_endpoint_l2_ratio = 0.6106898322623961`
- `active_closure_residual_to_target_abs_PF_ratio = 0.5180760517875869`
- `local_max_closure_residual_to_target_abs_PF_ratio = 0.6249192998819255`

But the exclusion/localization quantities remain clean:

- `outside_residual_fraction_of_full_endpoint = 0.0006827171481610137`
- `live_residual_fraction_of_full_endpoint = 0.0028655163351321462`
- `outside_support_tail_fraction = 6.270992636390208e-06`
- `live_support_tail_fraction = 0.0`
- `full_total_closure_residual_angular_volume = 0.0`

The support layer therefore agrees with the medium-layer diagnosis. The
half-nominal source family is structurally coherent, but the current finite
medium/support exchange ansatz is calibrated too narrowly to be a service-family
law.

## V=2.5 Interpretation

The half-nominal run is not evidence that beta075 is physically weak. It is
evidence that the current sealed V=5 construction should be read as a sealed
operating point, not yet as a sealed service-rating family.

The analogy is close to using a control/closure package sized for one operating
load and applying it unchanged to another load. At V=2.5 the source demand is
not dangerous to the live packet, but the regulator and support exchange basis
do not automatically retune to the altered residual geometry. That is a
source-law refinement issue: service rating needs to appear explicitly in the
medium closure/support-reservoir operator, or the closure basis needs a
service-aware normalization.

The encouraging part is that all of the failure data points away from a hard
physics wall:

- no live packet causal failure
- no superluminal boost failure
- no live regulator pollution
- no tensor projection failure
- no mixed-eigenvalue failure
- no offmask/live support leakage
- no angular support residue

The uncomfortable part is that a half-load comparator failing the current
closure gate means the academic narrative cannot say “V=5 is one member of an
already validated V-family.” It can say “V=5 is sealed locally; nearby/farther
service ratings expose a service-law calibration obligation.”

## V=10 Boundary Map

Run root:

`toolkit/adm_harness_cli/runs/stage2_external/beta_collar_generator_beta075_p003_mid_v10_dense377x241`

The V=10 source manifest was cloned from the beta075 V=5 manifest with only the
service rating changed to `V=10`. The dense source ledger completed at
`377 x 241` with `90857` rows and a Parquet point ledger.

### Source Safety Failure

The V=10 boundary run fails at the first hard source-safety gate:

- `positive_packet_norm_live = 123`
- `max_packet_norm_live = 1135.4997081858191`
- `min_packet_norm_live = -884.1285618238594`
- `live_points = 966`

This is a materially different failure from V=2.5. V=2.5 is live-packet safe
and fails later at medium/support closure calibration. V=10 directly violates
the live packet causal safety condition. That means the double-nominal result is
not merely an over/underfit of the current support closure operator; the source
geometry itself is outside the safe operating envelope of the current beta075
package.

The source decision table also shows that the live-packet radial-null and
pressure exposure are worse than nominal-family expectations:

- `live_packet_fraction__neg_Tkk_radial = 0.05157526072411069`
- `live_packet_point_peak__neg_Tkk_radial = 1.9384555029463901`
- `live_packet_fraction__abs_p_l = 0.008466236881927946`
- `live_packet_point_peak__abs_p_l = 0.034023258358964414`
- `live_packet_fraction__abs_j_l = 0.16624710055079128`
- `live_packet_point_peak__abs_j_l = 0.013498452764049526`
- `unsafe_penalty = 10.0`
- `score = 11.0`

The V=10 read is therefore blunt: the current beta075 operating-point package
does not extend to double nominal. This does not weaken the sealed V=5 claim,
but it does define the boundary of the present local design.

### Downstream Diagnostic Continuation

The component/source assignment completed after the source failure, which is
useful for failure localization. Radial string-cloud replacement, intermediate
source modeling, structured endpoint-J source fitting, and endpoint-J closure
component fitting also completed.

The first attempt to continue into radial string-cloud replacement exposed a
software compatibility issue: one downstream reader still assumed the source
point ledger was CSV and attempted to parse the new Parquet ledger as UTF-8
text. That tooling bug was fixed, and the diagnostic ladder was resumed. The
V=10 source-safety failure remains valid regardless of that interruption.

### Medium And Covariant Follow-Up

V=10 medium field closure fails in essentially the same way as V=2.5:

- `passes_constrained_field_closure = False`
- `worst_normalized_l1_error = 0.17851276819592593`
- `worst_angular_watch_l1_error = 0.17151357677944407`
- `max_angular_residual_to_source_ratio = 0.08049780555788218`
- `max_abs_coefficient = 0.4676450472845653`
- `regulator_to_source_abs_ratio = 0.03801033846791329`
- `regulator_boundary_gradient_to_source_ratio = 0.008476471984013134`
- `p99_heat_flux_ratio = 0.9781200882864631`
- `p01_transport_margin = 0.021879911713536836`
- `max_abs_boost_velocity = 0.9913506193424759`
- `live_rows = 0`
- `regulator_live_rows = 0`
- `boost_superluminal_or_nan_rows = 0`
- `max_conservation_burden_delta = 0.0005558418366294589`

The match to the V=2.5 field-closure miss is narratively important. The
medium closure basis is not merely overdriving half-load. It appears calibrated
to the V=5 service point and loses closure quality when service rating is moved
in either direction.

The covariant audit nevertheless passes:

- `passes_covariant_identity_audit = True`
- `projection_reconstruction_pass = True`
- `max_projection_linf_error = 3.0184188481996443e-16`
- `projection_error_to_source_ratio = 1.796198864773392e-16`
- `boost_subluminal_pass = True`
- `max_abs_boost_velocity = 0.991350619342476`
- `mixed_eigen_real_pass = True`
- `max_mixed_eigen_imag = 0.0`
- `exchange_localization_pass = True`
- `outside_allowed_divergence_fraction = 0.0065148660155374075`
- `live_divergence_fraction = 0.0029245800732757054`

This does not rescue V=10, because source safety has already failed. It does,
however, separate the failure types. V=10 is not an algebraic collapse of the
regulated endpoint-medium tensor. It is a live packet causal-safety failure,
with the same service-law calibration debt observed away from V=5.

### Support-Stroke And Total Closure Follow-Up

V=10 support-stroke exchange also fails by a narrow fit margin:

- `passes_support_stroke_exchange_fit = False`
- `best_normalized_active_abs_PF_l1_error = 0.5004232367634598`
- `best_normalized_allowed_abs_PF_l1_error = 0.41428422504428253`
- `best_active_coordinate_l2_error_ratio = 0.5198499440169009`
- `best_allowed_coordinate_l2_error_ratio = 0.41986527056283973`
- `best_max_abs_coefficient = 4.189735084776626`
- `best_effective_coefficient_count_total = 15146.983311300499`
- `best_outside_tail_fraction = 2.363232684913144e-05`
- `best_live_tail_fraction = 0.0`
- `best_high_psi_source_fraction = 0.001158143524628872`

Total support closure preserves the same distinction:

- `passes_support_total_closure = False`
- `active_closure_residual_to_endpoint_l2_ratio = 0.5198499440169003`
- `allowed_closure_residual_to_endpoint_l2_ratio = 0.41986527056283934`
- `local_max_closure_residual_to_endpoint_l2_ratio = 0.610687394717149`
- `active_closure_residual_to_target_abs_PF_ratio = 0.5004232367634565`
- `allowed_closure_residual_to_target_abs_PF_ratio = 0.4142842250442794`
- `local_max_closure_residual_to_target_abs_PF_ratio = 0.6249175607358108`

The localization and angular exclusions still pass:

- `outside_residual_fraction_of_full_endpoint = 0.003587302947678696`
- `live_residual_fraction_of_full_endpoint = 0.0029245800732756832`
- `outside_support_tail_fraction = 7.954377187139912e-06`
- `live_support_tail_fraction = 0.0`
- `full_total_closure_residual_angular_volume = 0.0`

So V=10 does not degrade into an uncontrolled offmask/support-tail mess. The
support closure failure is a narrow fit/gate miss, while the hard design
boundary is the source-safety violation.

### Pending Downstream Questions

The V=10 run is being treated as a boundary map rather than as a seal attempt.
At this point the useful output has localized the failure stack:

- source safety: hard fail
- medium closure fit: non-V5 calibration fail
- covariant tensor identity: pass
- support-stroke exchange: narrow fit/coefficient fail
- total support closure: active/local closure fail, localization and angular exclusions pass
- first-order/capstone: not eligible as promotion evidence because source
  safety and support closure have already failed

No V=10 capstone should be run as evidence from this ladder. A purely diagnostic
first-order/capstone run could be constructed, but it would no longer answer the
physical-source proof question; the proof gate already failed at source safety.

## Cross-Rating Interpretation

The comparison now says something sharper than either run alone.

V=2.5 and V=10 are not symmetric failures. V=2.5 is live-packet safe and
covariantly coherent, but misses the V5-tuned medium/support closure gates. V=10
fails live-packet source safety directly, and then also shows the same
medium/support calibration miss.

That means the sealed V=5 result should be described as an operating-point seal,
not yet as a service-family theorem. The next source-law refinement should not
be framed as rescuing a weak design. It should be framed as promoting an
operating-point construction into a service-aware family:

- service rating must enter the medium closure/support-reservoir operator
  explicitly;
- closure bases need service-aware normalization or additional service modes;
- V10 requires a causal-margin redesign before it can be treated as a possible
  operating point;
- V2.5 is a better immediate target for service-law refinement because its
  source geometry is already packet-safe.

For academic narrative, this is still a useful Stage II outcome. It says the
nominal V=5 package is not a numerical accident across the internal proof stack,
but the current proof stack has exposed its next real obligation: convert the
sealed operating point into a service-parameterized source law, and separately
develop a high-service causal-margin mechanism if V10 is meant to become more
than a boundary probe.

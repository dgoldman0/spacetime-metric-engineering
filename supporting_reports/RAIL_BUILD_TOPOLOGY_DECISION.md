# Active-rail build topology: recognition and working preference

17 September 2026. Architectural decision record from the topology discussion.

The full physical rail topology remains open. **C1 is the leading provisional
architecture: finite, mechanically independent, multicomponent source
assemblies with overlapping active regions and scheduled packet handoff.**
Module size, internal arrangement, separation and overlap width remain design
variables. A lightly connected architecture remains a comparison candidate.
Finite-module closure and intermodule source matching remain to be established.

The agreed [research workflow](SOURCE_FEASIBILITY_WORKFLOW.md) evaluates
physically normalized component sources and a finite overlapping pair before
detailed implementation optimization. Source and boundary costs can motivate
bounded geometry revisions, with service requirements and placement changes
recorded explicitly.

## Recognition retained

Continuity of the required rail geometry and source history is distinct from
mechanical and material continuity of the infrastructure. The earlier
continuous, snake-like build is one possible realization. Its route-length
mechanical connection remains a construction choice requiring its own
justification.

The transport service needs an admissible geometric history, actual source
support, consistent field states and coordinated control through its handoffs.
The extent of each physical material population and each load-bearing member
belongs to the source construction. Terms such as backbone, jacket, railbed,
joint and distributed support identify roles and local arrangements; the
global connectivity must be specified separately.

C1 separates the extent of the route from the size of each mechanically
connected assembly. An astronomical route would still require distributed
infrastructure, deployed source regions and coordinated service. Its total
inventory and operational burden depend on the resulting module and overlap
construction.

## Topology vocabulary

| Family | Physical arrangement | Standing in the comparison |
|---|---|---|
| A1 / A2 | A continuous backbone, either integral or articulated into connected segments. | Earlier construction picture; route-length load transmission needs an explicit reason and model. |
| B1 | Finite modules joined by substantial structural links. | Retains significant mechanical exchange between modules. |
| B2 | Modules carrying their major local duties, with light service connections. | Useful comparison to C1 when connectors simplify the complete assembly. |
| B3 | Primarily field-connected modules, with any physical service links specified separately. | Overlaps C1 when the assemblies move independently. |
| C1 | Mechanically independent assemblies with substantial, adjustable source overlap. | Leading provisional architecture. |
| C2 | Mechanically independent assemblies with narrow handoff overlap. | Comparison whose boundary and response costs require evaluation. |
| C3 | Widely separated stations with substantial gaps between active source regions. | Requires a transport and source construction for those gaps. |

These labels describe hardware arrangements. The spacetime geometry and its
global topology remain properties of the corresponding gravitational solution.

## Multicomponent modules and permitted exchange

A module may contain long internal supports, several distinct materials,
closed current systems, multiple stores, optical interfaces and thermal
receivers. It may also be a coordinated cluster of specialized vehicles. The
service-region boundary and the vehicle boundaries can therefore be different
accounting boundaries. Each boundary carries its specified exchanges, while
the complete assembly supplies the combined duties.

The existing [component responsibilities](RAIL_COMPONENT_CROSS_REFERENCE_AND_JOINT_COORDINATION.md)
remain in force: standing radial support, angular and transition response,
signed quantum opening, endpoint currents, reservoir exchange, live handoff
and shared geometry. The six containment support populations and the six
rotor copies retain their distinct purposes. A numerical receiving node is
an allocation element whose physical embedding remains to be supplied.

For C1, mechanical independence means that structural members carry no
traction from one independent assembly to the next. Radiation, overlapping
fields, packet exchange and specified station-keeping can still transfer
energy, momentum and angular momentum. Their forces determine module motion.
Acceptable recoil, displacement, rotation and recovery over a service/reset
cycle are the requirements; instantaneous zero net force is a possible
specialization. Counterrotating stores and internal reactions can reduce
external exchange where their complete interfaces support that behavior.

Consequently each candidate accounts for its material and field stresses,
stored energy, current returns, reaction paths, heat destinations and boundary
fluxes. A shared support or field interaction earns any inventory saving
through its actual coupled law. Strong field coupling can also give the
formation collective dynamics even with mechanically separate hardware.

## Physical content of the overlap

The overlap region needs the actual material or field states supplying its
required local stress-energy. The gravitational field outside a module and
the local source tensor are different quantities. String and sheet laws apply
where their constituents exist; their finite termination, continuation or
replacement belongs to the overlap construction. The same requirement applies
to current and quantum support.

Neighboring assemblies and their interactions must be evaluated on one shared
geometry, with each contribution counted once. The combined Einstein and
matter equations determine the overlap; the nonlinearity of the gravitational
equations prevents general superposition of independently constructed metrics.
[Carroll's GR notes, section 4](https://arxiv.org/pdf/gr-qc/9712019#page=119)
give the underlying field-equation statement.

Broad, smooth overlap is a useful starting preference because the existing
handoff work exposes derivative costs at transitions. Its width remains
adjustable alongside field range, source inventory, propagation delay and
control requirements. The earlier collar results concern their specified
rail geometry; finite free-flying module handoff is an additional problem.

## Evidence and decision boundary

The [current storage and interface results](RAIL_STORAGE_AND_INTERFACE_STATUS.md)
supply finite local ingredients and conditional history bounds. They retain
the unresolved material laws, fixture dynamics, spatial packing and complete
source requirements. This topology recognition organizes those requirements
into candidate finite assemblies; it adds an architectural preference without
adding a physical feasibility result.

The first topology-specific construction would combine a finite service
assembly, its accounted center-of-mass and rotational response, and one
neighboring overlap. End closures, source tapering, optical and electrical
returns, overlap inventory, and reset all contribute to its cost. Their
tradeoff with bulk length determines useful module size and spacing.

A longer chain additionally requires collective stability, causal service
scheduling, readiness propagation and chronology checks. Pairwise handoff
evidence would be one input to that system calculation.

The subsequent [finite-module source screen](C1_FINITE_MODULE_PAIR_SCREEN.md)
constructs a common electrostatic field from two finite charge populations and
compares their separate static support requirements. A broad offset overlap
and narrower cost reference are retained. The source, constitutive, spatial
embedding and motion gates remain explicit in the
[module specification](../component_design/C1_FINITE_MODULE_PAIR.md).

The [signed-source channel screen](C1_SIGNED_SOURCE_CHANNEL_SCREEN.md) retains
the geometry and electric overlaps while adding inset reflecting quantum
channels as a trial. A transition tensor constraint requires signed-source
structure beyond the radial conformal law. The angular-source and finite
boundary construction remains joint with the exterior source requirement;
the provisional C1 preference and both electric-overlap brackets are retained.

Future architecture work starts from this recognition and the provisional C1
preference. A change of preference should identify the source, boundary,
inventory or control evidence that motivates it.

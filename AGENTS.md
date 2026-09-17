# General

Use informative commit messages.

Commit completed, validated milestones as work proceeds. Keep implementation,
supporting reports, and reproducibility evidence in coherent commits.

Avoid using scripted auto-generation for reports. VERY IMPORTANT. You should write manual reports when narratively important reasonable milestones are reached. 

Make sure code can do independent computations in parralel. And remember, at 16 cores for this laptop, 4 - 6 workers should be viable. 

# Architectural context

For topology, source placement, containment or interface work, consult
[the build-topology decision](supporting_reports/RAIL_BUILD_TOPOLOGY_DECISION.md).
The full rail topology is open; C1 is the leading provisional preference:
mechanically independent multicomponent assemblies with adjustable source
overlap and scheduled handoff. Continuous rail geometry and source support
are distinct from route-length mechanical or material continuity. Preserve
specialized components, explicitly accounted recoil and boundary exchange,
and the open finite-module/overlap feasibility requirements.

# General Paper Writing

Avoid mansplaining language. There should be no reason to tell the reader how the information in the paper should be interpreted. The information and implication should be clear enough from the paper. If it needs to be mansplained to the reader, it means that the underlying content presented is insufficient for an intelligent reader to infer what is obvious. Use positive and informative language. Avoid "not" and "rather than" and similar and avoid bringing up what is not the case, unless we are specifically arguing against a well held belief explicitly. In document writing/papers use proper transition words and phrases to ensure that the document flows rather than feeling like a list of sentences. 

# Technical Doc Writing Style

Whenever updating the technical doc. Avoid defensive language. The technical document always represents just our current full understanding. It avoids progress report style language. It also informs on what is the case, affirmatively, and honestly.

Update PDF in repo whenever tech disclosure is updated.

NEVER use the technical disclosure as a running log. Only use locked in recognized as solid design elements. 

# Commit messages

Use informative multi sentence commit messages.

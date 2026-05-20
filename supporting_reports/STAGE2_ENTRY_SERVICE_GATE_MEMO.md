# Stage II Entry Service Gate Memo

The mild entry-stage redesign worked as intended. Separating the pre-entry setup interval from the live packet accounting gives the compact handoff layer a clean service boundary: setup support is still represented in the full ledger, while live packet scoring begins once the packet is in the supported entry corridor.

On the high-resolution `101 x 151` rerun, the representative `wide4_start_m1p40` setting has zero positive live packet-norm samples. The live packet safety margin is clean on the extended domain, with `max_packet_norm_live = -1.242423476132938` across 861 live points.

The component source ledger closes the live assigned channels with zero live residual fraction for `neg_Tkk_radial`, `abs_p_l`, `abs_j_l`, and `abs_pOmega`. The hard affine SNEC evaluation is also clean across `tau = 2.0`, `3.0`, and `4.0`, with zero raw and zero scoreable benchmark violations. The tightest scoreable margin is the `tau = 4.0` minus branch at about `0.014936`.

The resulting source picture is affirmative: the representative design uses an entry service gate, compact entry/catch/edge handoff windows, packet-edge beta rematch, and packet-local radial support as one coordinated source-placement structure. Source burdens are assigned to the intended infrastructure roles rather than to positive live packet conditions.

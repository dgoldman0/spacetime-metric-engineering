from white_casimir_audit.geometry import (
    CentralReadoutPath,
    PillarMidplaneCavity,
    SphereInCylinder,
    make_xy_grid,
)


def test_plate_pillar_body_ids_and_roles():
    geom = PillarMidplaneCavity(
        gap_um=4.0,
        plate_width_um=40.0,
        plate_height_um=40.0,
        pillar_diameter_um=1.0,
    )
    assert geom.body_id((1.0, -2.0, 0.0)) == 1
    assert geom.body_id((1.0, 2.0, 0.0)) == 2
    assert geom.body_id((0.0, 0.0, 0.0)) == 3
    assert geom.intersects_segment((0.0, -3.0, 0.0), (0.0, 3.0, 0.0)) == {1, 2, 3}

    roles = geom.role_regions(make_xy_grid(-4.0, 4.0, -3.0, 3.0, 40, 40))
    assert roles["boundary_infrastructure"].any()
    assert roles["stress_shaping_body"].any()
    assert roles["source_shell_candidate"].any()


def test_sphere_cylinder_body_ids_readout_and_roles():
    readout = CentralReadoutPath(length_um=8.0, radius_um=0.05)
    geom = SphereInCylinder(
        sphere_diameter_um=1.0,
        cylinder_diameter_um=4.0,
        cylinder_length_um=8.0,
        readout_path=readout,
    )
    assert geom.body_id((0.0, 0.0, 0.0)) == 1
    assert geom.body_id((0.0, 2.0, 0.0)) == 2
    assert readout.contains((1.0, 0.01, 0.0))
    assert not readout.participates_as_casimir_boundary
    assert geom.intersects_segment((0.0, 0.0, 0.0), (0.0, 3.0, 0.0)) == {1, 2}

    roles = geom.role_regions(make_xy_grid(-4.0, 4.0, -3.0, 3.0, 50, 50))
    assert roles["boundary_infrastructure"].any()
    assert roles["stress_shaping_body"].any()
    assert roles["source_shell_candidate"].any()
    assert roles["transit_readout_channel"].any()

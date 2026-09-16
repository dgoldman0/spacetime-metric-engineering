import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy.optimize import linprog

from adm_harness.magnetic_geometry import (
    jacket_requirements, jacket_currents, radial_sleeve_projection,
    radial_sleeve_interval, radial_sleeve_threshold, straight_sheet_fraction,
)
from adm_harness.magnetic_load_balance import loop_currents, conserved_sleeve_interval


def test_two_boundary_forces_include_outer_reaction_and_magnetic_energy():
    # Direct cylinder force balance: tension per length is pressure * radius.
    r, length, p, eta, b, e = .3, 2.4, 1.7, 1.2, .2, 1.2
    volume_core = np.pi*r*r*length
    aspect = .03
    energy = np.array([[3*p*volume_core*(1+np.pi*aspect)]])
    D = np.array([[8.]])
    result = jacket_requirements(energy, D, aspect=aspect, inner_pressure=b,
                                 outer_pressure=e, radius_ratio=eta)
    inner = 2*np.pi*r*length*((p+b*p-e*p)*r)
    outer = 2*np.pi*eta*r*length*(e*p*eta*r)
    assert_allclose(result["inner_hoop"]*D, inner, atol=1e-15)
    assert_allclose(result["outer_hoop"]*D, outer)
    magnetic_energy = b*p*volume_core+e*p*volume_core*(eta**2-1)
    assert_allclose(result["total_hoop"]*D, 2*(p*volume_core+magnetic_energy))
    assert_allclose(result["inner_hoop"], 0., atol=1e-15)
    assert np.all(result["outer_hoop"] > 0)


def test_moving_external_pressure_retains_its_reaction_in_thin_gap_limit():
    E, D = np.array([[3.]]), np.array([[2.]])
    baseline = jacket_requirements(E, D, aspect=.01, inner_pressure=1,
                                    outer_pressure=0, radius_ratio=1)
    external = jacket_requirements(E, D, aspect=.01, inner_pressure=1,
                                    outer_pressure=2, radius_ratio=1+1e-8)
    excluding = jacket_requirements(E, D, aspect=.01, inner_pressure=0,
                                     outer_pressure=1, radius_ratio=1+1e-8)
    assert_allclose(external["total_hoop"], baseline["total_hoop"], rtol=3e-8)
    assert_allclose(excluding["total_hoop"], baseline["total_hoop"]/2, rtol=3e-8)


def test_current_surface_jumps_and_conserved_families_match_undeformed_integrals():
    E, D = np.full((3, 2), 3.), np.full((3, 2), 10.)
    leg = np.array([2., 3.]); aspect, tube, fill, eta = .01, .1, .1, 1.2
    reference = loop_currents(E, D, np.ones_like(E), np.ones_like(E), leg,
        aspect=aspect, angle=0, fill_fraction=fill, tube_ratio=tube)
    b, e = .25, 1.25
    fraction=straight_sheet_fraction(E,D,np.ones_like(E),np.ones_like(E),reference,
                                     aspect=aspect,fill_fraction=fill)
    assert_allclose(fraction,1/(1+np.pi*aspect))
    result = jacket_currents(reference, D, inner_pressure=b, outer_pressure=e,
                             radius_ratio=eta, straight_fraction=fraction,
                             aspect=aspect, tube_ratio=tube)
    r = leg*aspect*tube/result["span_factor"]
    length = 2*leg*(1+np.pi*aspect)/result["span_factor"]
    B = np.sqrt(2*E/(3*fill*D))
    sheet = 2*B*fill*D/r
    bulk = 2*np.pi*B*fill*D/length
    expected = (sheet*abs(np.sqrt(e)-np.sqrt(b)), sheet*eta*np.sqrt(e),
                bulk*np.sqrt(b), bulk*(eta*eta-1)*np.sqrt(e))
    for family, current in zip(result["families"].values(), expected):
        assert_allclose(family["current_integral"], current)
        assert_allclose(family["unit_tensor"][0], 2*current/D)
        assert_allclose(family["unit_rest_inventory"], np.sqrt(2)*current[0])
    for name in ("inner_sheet","outer_sheet"):
        family=result["families"][name]
        assert_allclose(family["unit_straight_hoop"],family["unit_tensor"][0]*fraction/2)
    assert_allclose(result["unit_tensor"][0], 2*sum(expected)/D)


def test_original_current_inventory_is_recovered_and_zero_field_costs_zero():
    E = np.array([[1.], [2.]]); lr=np.array([[1.], [.4]]); lt=np.ones_like(E)
    D=4*lr
    reference=loop_currents(E,D,lr,lt,np.array([1.]),aspect=.01,angle=0)
    fraction=straight_sheet_fraction(E,D,lr,lt,reference)
    old=jacket_currents(reference,D,inner_pressure=1,outer_pressure=0,radius_ratio=1,
                        straight_fraction=fraction)
    assert_allclose(old["unit_tensor"],reference["unit_tensor"])
    zero=jacket_currents(reference,D,inner_pressure=0,outer_pressure=0,radius_ratio=1,
                         straight_fraction=fraction)
    assert_allclose(zero["unit_tensor"],0)


def test_radial_projection_against_independent_joint_time_linear_program():
    rng=np.random.default_rng(667)
    for k in (.1,.5,.50001,.8,1.):
        for _ in range(12):
            n=5; D=rng.uniform(1,5,(n,1)); H=rng.uniform(.01,.2,(n,1))
            F=rng.uniform(-2,.5,(3,n,1))
            projection=radial_sleeve_projection(F,D,H)
            result=radial_sleeve_interval(projection,k)
            rows=[]; rhs=[]
            for t in range(n):
                # Variables M and one physical axial pressure z per time.
                offsets=[F[0,t,0]+H[t,0],F[1,t,0]-H[t,0]/2,F[2,t,0]-H[t,0]/2]
                for offset, slope in zip(offsets,(-1,-1,2)):
                    row=np.zeros(n+1);row[0]=1/D[t,0];row[t+1]=slope
                    rows.append(row);rhs.append(-offset)
                for sign in (-1,1):
                    row=np.zeros(n+1);row[0]=-k/D[t,0];row[t+1]=sign
                    rows.append(row);rhs.append(0)
            bounds=[(float((D*H).max()/k),None)]+[(None,None)]*n
            objective=np.r_[1.,np.zeros(n)]
            low=linprog(objective,A_ub=rows,b_ub=rhs,bounds=bounds,method="highs")
            assert bool(result["feasible"][0])==bool(low.success)
            generic=conserved_sleeve_interval(F,D,H,np.ones_like(D),stress_fraction=k)
            assert_allclose(result["lower"],generic["lower"],atol=1e-12)
            assert_allclose(result["upper"],generic["upper"],atol=1e-12)
            if low.success:
                high=linprog(-objective,A_ub=rows,b_ub=rhs,bounds=bounds,method="highs")
                assert high.success
                assert_allclose([result["lower"][0],result["upper"][0]],
                                [low.fun,-high.fun],atol=1e-11)


def test_threshold_brackets_joint_feasibility():
    F=np.full((3,2,1),-1.);D=np.ones((2,1));H=np.full((2,1),.2)
    projection=radial_sleeve_projection(F,D,H)
    threshold=radial_sleeve_threshold(projection)
    assert 0<threshold<1
    assert radial_sleeve_interval(projection,threshold)["feasible"].all()
    assert not radial_sleeve_interval(projection,threshold-1e-7)["feasible"].all()
    impossible=radial_sleeve_projection(-F,D,H)
    assert radial_sleeve_threshold(impossible) is None


def test_separate_boundary_inventories_retain_both_peak_loads():
    D=np.ones((2,1));F=np.full((3,2,1),-10.)
    inner=np.array([[2.],[.1]]);outer=np.array([[.1],[3.]])
    projection=radial_sleeve_projection(F,D,inner+outer,boundary_hoops=[inner,outer])
    assert_allclose(projection["hoop_max"],5.)
    assert_allclose(radial_sleeve_interval(projection,1.)["lower"],5.)
    # The common-inventory relaxation would only retain the larger total peak.
    relaxed=radial_sleeve_projection(F,D,inner+outer)
    assert_allclose(relaxed["hoop_max"],3.1)


@pytest.mark.parametrize("b,e,eta", [(0,1,1),(0,2,1.1),(-1,0,1.1),(1,0,.9)])
def test_invalid_jackets_rejected(b,e,eta):
    with pytest.raises(ValueError):
        jacket_requirements(np.ones((2,1)),np.ones((2,1)),aspect=.01,
                            inner_pressure=b,outer_pressure=e,radius_ratio=eta)

from types import SimpleNamespace

import numpy as np
from numpy.testing import assert_allclose

from adm_harness.active_transfer_reservoir import MetricJets, divergence_projections
from adm_harness.composite_capacitor import anisotropic_moments
from adm_harness.pressure_linked_storage import fluid_coefficients
from evaluate_composite_capacitor_transport import support_force


class SmoothMetric:
    def metric(self, time, x):
        x = np.asarray(x)
        alpha = np.exp(.07*time+.11*x)
        b = np.exp(.09*time+.04*x)
        radius = 2*np.exp(.03*time+.06*x)
        beta = .08*np.exp(.02*time-.03*x)
        return MetricJets(alpha,beta,b,radius,.11*alpha,-.03*beta,
                          np.full_like(x,.09),np.full_like(x,.04),
                          np.full_like(x,.03),np.full_like(x,.06))

    def medium(self, time, x):
        z = np.zeros((4,len(x)))
        return z,z,z


def material(time,x,field=False):
    metric=SmoothMetric().metric(time,x)
    if field:
        u=.6/metric.radius**4
        return u,-u,u
    return 2+.1*time+.02*x*x, .3+.04*time+.05*x, -.2+.01*time+.03*x


def normal_tensor(time,x,field=False):
    g=SmoothMetric().metric(time,x)
    return anisotropic_moments(*material(time,x,field),g.b*g.beta/g.alpha)


def check_force(field):
    geometry=SmoothMetric()
    t=.6+np.arange(5)*.002
    x=np.linspace(-.6,.6,121)
    c=fluid_coefficients(geometry,t,x)
    cm=fluid_coefficients(geometry,(t[1:]+t[:-1])/2,x)
    rest=np.array([material(time,x,field) for time in t]).transpose(1,0,2)
    model=SimpleNamespace(t=t,x=x,cm=cm)
    actual=support_force(model,rest[0]*c['rest_volume'],rest[1],rest[2])
    expected=[]
    eps=1e-5
    for time in (t[1:]+t[:-1])/2:
        g=geometry.metric(time,x)
        moments=normal_tensor(time,x,field)
        dt=(normal_tensor(time+eps,x,field)-normal_tensor(time-eps,x,field))/(2*eps)
        dx=(normal_tensor(time,x+eps,field)-normal_tensor(time,x-eps,field))/(2*eps)
        power,force=divergence_projections(g,moments,dt,dx)
        v=g.b*g.beta/g.alpha
        expected.append((force-v*power)/np.sqrt(1-v*v))
    assert_allclose(actual,np.array(expected),atol=3e-8,rtol=1e-6)
    return actual


def test_material_force_matches_independent_normal_frame_covariant_divergence():
    check_force(False)


def test_source_free_radial_field_changes_energy_without_material_force():
    assert_allclose(check_force(True),0.,atol=3e-8)

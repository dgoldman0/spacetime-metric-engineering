import numpy as np

from adm_harness.c1_population_boundary import cell_columns, cell_costs, refine_partition
from adm_harness.c1_signed_channels import boundary_exchange, optical_partitions, quadrature, strip_tensor
from test_c1_signed_channels import AnalyticChart


def test_refinement_preserves_extent_but_changes_casimir_energy_and_end_load():
    g=AnalyticChart(curved=False)
    ends,lengths=optical_partitions(g,(-1.,1.),1)
    old=cell_costs(g,[(ends,lengths)],1.)
    e,l,c=refine_partition(g,ends,lengths,[3.],0.)
    new=cell_costs(g,[(e,l)],1.)
    np.testing.assert_allclose(l.sum(),lengths.sum(),rtol=1e-13)
    np.testing.assert_allclose(old['proper_length']@[3.],new['proper_length']@c,rtol=1e-13)
    np.testing.assert_allclose(new['killing_energy']@c,4*(old['killing_energy']@[3.]),rtol=1e-13)
    np.testing.assert_allclose((new['force_matrix']@c)[[0,-1]],4*(old['force_matrix']@[3.]),rtol=1e-13)
    np.testing.assert_allclose((new['force_matrix']@c)[1],0.,atol=1e-14)


def test_energy_against_direct_tensor_volume_integral_and_clock_scaling():
    energies=[]
    for clock in (1.,3.7):
        g=AnalyticChart(clock=clock);e,l=optical_partitions(g,(-1.1,.9),3)
        costs=cell_costs(g,[(e,l)],.03)
        direct=[]
        for lo,hi,length in zip(e[:-1],e[1:],l):
            x,w=quadrature(g,lo,hi,order=12)
            r,a,b,_,_,ap,app=g.jets(x)
            t=strip_tensor(r,a,ap,app,length,strength=.03)
            direct.append(w@(4*np.pi*r*r*a*b*t[:,0]))
        np.testing.assert_allclose(costs['killing_energy'],direct,rtol=1e-12,atol=1e-14)
        energies.append(costs)
    np.testing.assert_allclose(energies[1]['killing_energy'],3.7*energies[0]['killing_energy'],rtol=1e-12)
    np.testing.assert_allclose(energies[1]['force_matrix'],energies[0]['force_matrix'],rtol=1e-12)


def test_one_sided_sources_reproduce_population_jump_and_boundary_reaction():
    g=AnalyticChart();e,l=optical_partitions(g,(-1.,1.),2)
    x=np.array([e[1],e[1]]);eta=.027;central=np.array([3.,7.])
    columns=cell_columns(g,x,['left','right'],[(e,l)],eta)
    bulk=np.einsum('nct,c->nt',columns,central)
    r=g.jets(x)[0]
    reaction=4*np.pi*r[0]**2*(bulk[0,1]-bulk[1,1])
    costs=cell_costs(g,[(e,l)],eta)
    np.testing.assert_allclose(reaction,(costs['force_matrix']@central)[1],rtol=1e-13)
    independent=np.zeros(3)
    for j,c in enumerate(central):
        independent[j:j+2]+=boundary_exchange(g,e[j:j+2],l[j:j+1],strength=eta*c)['force_on_material']
    np.testing.assert_allclose(costs['force_matrix']@central,independent,rtol=1e-13)

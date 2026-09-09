import numpy as np
from numpy.testing import assert_allclose
from scipy.integrate import simpson

from adm_harness.confined_fermion import DiracMesh, MassWell, occupied_tensor


def test_constant_product_space_spectrum_and_mass_response():
    # Dirichlet F, free G gives the exact continuum positive branch below.
    errors = []
    for points in (401, 801):
        z = np.linspace(-5, 5, points)
        mesh = DiracMesh(z, np.full(points, .8), np.full(points-1, .8),
                         np.full(points-1, .3))
        modes = mesh.roots(1.25)
        exact = np.sqrt(.8**2+.3**2+(np.arange(1, len(modes)+1)*np.pi/10)**2)
        errors.append(np.max(abs(np.array([m['frequency'] for m in modes])-exact)))
        for mode in modes:
            norm = mesh.spacing*(np.sum(mode['f']**2)+np.sum(mode['g_faces']**2))
            assert_allclose(norm, 1., atol=1e-13)
            # Hellmann--Feynman derivative d omega / d mass = mass / omega.
            mass_response = mesh.spacing*(np.sum(mode['f']**2)-np.sum(mode['g_faces']**2))
            assert_allclose(mass_response, .8/mode['frequency'], rtol=2e-8)
    assert errors[1] < errors[0]/3.8


def test_exact_mode_tensor_ward_identity_and_energy():
    z = np.linspace(-5, 5, 10001)
    mass, kappa, radius = .8, 1, 10/3
    wave = np.pi/10
    omega = np.sqrt(mass**2+(kappa/radius)**2+wave**2)
    f = np.sin(wave*(z+5))
    g = (-wave*np.cos(wave*(z+5))+kappa/radius*f)/(omega+mass)
    norm = np.sqrt(simpson(f*f+g*g, x=z))
    f, g = f/norm, g/norm
    fields = dict(lapse=np.ones_like(z), radius=np.full_like(z, radius),
                  mass=np.full_like(z, mass))
    tensor, scalar = occupied_tensor(fields, dict(f=f, g=g, frequency=omega), kappa)
    rho, pr, pt = tensor
    assert np.max(abs(np.gradient(pr, z)[2:-2])) < 2e-10
    assert_allclose(rho-pr-2*pt, mass*scalar, atol=1e-17)
    assert_allclose(4*np.pi*radius**2*simpson(rho, x=z), 2*omega, rtol=1e-10)


def test_isolated_scalar_wall_equation_and_surface_energy():
    well = MassWell(width=.8, vacuum_scale=1.3)
    proper = np.linspace(-8, 8, 8001)
    chi, cp, cpp, potential, force = well.values(proper, -100., 0.)
    assert_allclose(cpp, force, atol=1e-14)
    assert_allclose(.5*cp*cp, potential, atol=1e-15)
    # Integral chi'^2 dl = v^2/(3d) for a 0-to-v tanh interface.
    assert_allclose(simpson(cp*cp, x=proper), well.vacuum_scale**2/(3*well.width), rtol=1e-10)


def test_schur_roots_include_both_parities_without_extra_low_branch():
    z = np.linspace(-8, 8, 1001)
    m = 1.2-.9*np.exp(-(z/2)**4)
    faces = (z[1:]+z[:-1])/2
    mf = 1.2-.9*np.exp(-(faces/2)**4)
    roots = []
    for sign in (-1, 1):
        modes = DiracMesh(z, m, mf, np.full_like(faces, sign*.15)).roots(1.1)
        roots.append([row['frequency'] for row in modes])
    assert len(roots[0]) > 0
    assert_allclose(roots[0], roots[1], atol=2e-10)

"""Prestressed causal backbone bonded to local material heat buffers.

The backbone has rho=K*(n_b**2+1)/2 and p=K*(n_b**2-1)/2.
The attached buffers carry rho=n_t*(m+q), positive heat capacity, and
the endpoint exchange. Both reference amounts are conserved. Their
common longitudinal motion follows the sum of their material actions.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import linprog

from .elastic_endpoint_reservoir import ElasticLaw, ElasticDomainError
from .electrothermal_endpoint import ElectricalLaw
from .material_ensemble import MaterialEnsemble, nodal_sum


class PrestressedBufferAssembly(MaterialEnsemble):
    def __init__(self, template, backbone_scale=.001, forcing=None):
        if backbone_scale <= 0:
            raise ValueError('positive backbone rest-density scale required')
        self.model = template.model
        self.cells, self.edges = template.cells, template.edges
        self.initial_x = template.initial_x.copy()
        self.reference = template.reference.copy()
        self.mass = template.mass.copy()
        self.initial_cell_width = template.initial_cell_width.copy()
        source = template.fields(0., template.initial())
        self.initial_heat = source['heat'].copy()
        self.buffer_mass = 1.
        self.backbone_scale = float(backbone_scale)
        self.forcing = template.forcing if forcing is None else float(forcing)
        self.thermal_share = 1.
        self.electrical = ElectricalLaw(energy_ratio=0., conductivity=0.)
        # The inherited inversion uses mass+q-stiffness. Here it equals m+q.
        self.law = ElasticLaw(stiffness=backbone_scale,
                              mass=self.buffer_mass+backbone_scale,
                              scale=template.law.scale)
        self.backbone_weight = backbone_scale*self.reference**2
        self.template_initial_slice_energy = float(4*np.pi*source['matter_adm'].sum())

    def coefficients(self, t, x):
        width = np.diff(x)
        if np.min(width) <= 1e-10 or not np.isfinite(x).all():
            raise ElasticDomainError('material cells reached the ordered-mesh boundary')
        g = self.model.metric(t, x)
        volume = nodal_sum(width)
        a = nodal_sum(self.backbone_weight/width)/(2*g.b)
        b = .5*self.backbone_scale*g.b*volume
        return g, width, volume, a, b

    def fields(self, t, state):
        x, momentum, heat, charge = self.split(state)
        g, width, volume, a, b = self.coefficients(t, x)
        v = self.velocity(momentum, heat, g, a)
        gamma = 1/np.sqrt(1-v*v)
        momentum = self.law.scale*g.b*v*(self.mass*(self.buffer_mass+heat)*gamma+2*a)
        bb, gg, vv = np.array([g.b[:-1], g.b[1:]]), np.array([gamma[:-1], gamma[1:]]), np.array([v[:-1], v[1:]])
        nt = self.reference[None, :]/(width[None, :]*bb*gg)
        nb2 = self.backbone_weight[None, :]/(self.backbone_scale*(width[None, :]*bb*gg)**2)
        qb = np.array([heat[:-1], heat[1:]])
        backbone = .5*self.backbone_scale*(nb2+1)
        pressure = .5*self.backbone_scale*(nb2-1)
        buffer = nt*(self.buffer_mass+qb)
        rest = backbone+buffer
        sound2 = self.backbone_scale*nb2/(self.backbone_scale*nb2+buffer)
        if np.any(sound2 < 0) or np.any(sound2 >= 1) or np.min(rest-abs(pressure)) <= 0:
            raise ElasticDomainError('bonded backbone and buffer left their causal positive-energy domain')
        energy = (rest+pressure)*gg**2-pressure
        current = (rest+pressure)*gg**2*vv
        radial = pressure+vv*current
        def lump(values):
            return .5*(np.r_[width*values[0], 0.]+np.r_[0., width*values[1]])
        energy_int, current_int, radial_int = lump(energy), lump(current), lump(radial)
        matter_adm = self.law.scale*g.b*energy_int
        backbone_adm = self.law.scale*g.b*lump((backbone+pressure)*gg**2-pressure)
        return dict(x=x, momentum=momentum, heat=heat, charge=charge, metric=g, width=width,
                    volume=volume, a=a, b=b, velocity=v, gamma=gamma, stretch=nt,
                    backbone_stretch=np.sqrt(nb2), pressure=pressure, sound2=sound2,
                    energy_int=energy_int, current_int=current_int, radial_int=radial_int,
                    matter_adm=matter_adm, backbone_adm=backbone_adm,
                    field_adm=np.zeros_like(x), canonical=g.alpha*matter_adm-g.beta*momentum,
                    effective_n=self.mass/(g.b*gamma*volume),
                    minimum_rest_dec_margin=float(np.min(rest-abs(pressure))))

    def required_fixed_momentum_rate(self, t, f, heat_rate):
        """Momentum derivative for x_s=0 under the active metric and heat rate."""
        g, v, gamma, a = f['metric'], f['velocity'], f['gamma'], f['a']
        alpha_t, beta_t = self.lapse_shift_time(t, f['x'], g)
        vt = v*(g.logb_t-alpha_t/g.alpha)+g.b*beta_t/g.alpha
        c = self.buffer_mass+f['heat']
        return self.law.scale*g.b*(self.mass*c*gamma*v*g.logb_t
                                   +self.mass*heat_rate*gamma*v
                                   +(self.mass*c*gamma**3+2*a)*vt)

    def rhs(self, t, state):
        rate, diagnostics = super().rhs(t, state)
        f = self.fields(t, state)
        g, v = f['metric'], f['velocity']
        xrate = -g.beta+g.alpha*v/g.b
        xrate[[0, -1]] = 0.
        correction = -nodal_sum((self.backbone_weight-self.law.stiffness*self.reference**2)
                                *np.diff(xrate)/f['width']**2)/(2*g.b)
        wall_correction = 2*self.law.scale*g.b*v*correction
        diagnostics['anchor_left'] += float(wall_correction[0])
        diagnostics['anchor_right'] += float(wall_correction[-1])
        reactions = np.array([diagnostics['anchor_left'], diagnostics['anchor_right']])
        diagnostics['maximum_anchor_force'] = float(np.max(abs(reactions)/(g.alpha[[0, -1]]*g.b[[0, -1]])))
        return rate, diagnostics

    def fixed_motion_residual(self):
        state = self.initial()
        f = self.fields(0., state)
        rate, _ = self.rhs(0., state)
        offset = 2*(self.cells-1)
        qrate = rate[offset:offset+self.cells+1]
        required = self.required_fixed_momentum_rate(0., f, qrate)
        return rate[self.cells-1:2*(self.cells-1)]-required[1:-1]

    def equilibrate_initial_preload(self, *, floor=1e-12):
        """Minimize initial backbone ADM energy with zero interior acceleration.

        The squared reference weights enter the momentum balance linearly.
        End reactions are retained as measured ports. All active metric
        derivatives, the attached buffer inertia, and endpoint load enter
        this finite-dimensional initial equilibrium.
        """
        self.backbone_weight = np.zeros(self.cells)
        base_residual = self.fixed_motion_residual()
        base = self.fields(0., self.initial())
        e0 = float(4*np.pi*base['matter_adm'].sum())
        matrix, cost = [], []
        for i in range(self.cells):
            weights = np.zeros(self.cells); weights[i] = 1.
            self.backbone_weight = weights
            matrix.append(self.fixed_motion_residual()-base_residual)
            f = self.fields(0., self.initial())
            cost.append(float(4*np.pi*f['matter_adm'].sum())-e0)
        matrix = np.array(matrix).T
        normalization = np.maximum(np.max(abs(matrix), axis=1), abs(base_residual))
        normalization = np.maximum(normalization, 1e-15)
        solution = linprog(np.array(cost)/max(cost),
                           A_eq=matrix/normalization[:, None], b_eq=-base_residual/normalization,
                           bounds=(floor, None), method='highs')
        if not solution.success:
            raise ElasticDomainError('positive initial backbone equilibrium failed: '+solution.message)
        self.backbone_weight = solution.x.copy()
        residual = self.fixed_motion_residual()
        f = self.fields(0., self.initial())
        return dict(initial_slice_energy=float(4*np.pi*f['matter_adm'].sum()),
                    initial_backbone_slice_energy=float(4*np.pi*f['backbone_adm'].sum()),
                    zero_preload_slice_energy=e0,
                    maximum_initial_momentum_residual=float(abs(residual).max()),
                    maximum_relative_initial_momentum_residual=float(np.max(abs(residual)/normalization)),
                    squared_reference_weights=self.backbone_weight.copy())

    def match_template_energy(self, full_preload):
        """Scale the registered equilibrium preload to the prior energy budget."""
        fraction = ((self.template_initial_slice_energy-full_preload['zero_preload_slice_energy'])
                    /(full_preload['initial_slice_energy']-full_preload['zero_preload_slice_energy']))
        if not 0 < fraction <= 1:
            raise ElasticDomainError('template energy lies outside the registered preload allocation')
        self.backbone_weight = fraction*full_preload['squared_reference_weights']
        return float(fraction)

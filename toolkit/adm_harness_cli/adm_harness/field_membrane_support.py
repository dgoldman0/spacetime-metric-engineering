"""Local energy cost of radial fields, radiation, and angular membranes.

Rest-frame basis tensors (rho,p_r,p_t), per positive unit energy:
radial Maxwell field (1,-1,1); balanced radial radiation (1,1,0);
angular radiation (1,0,1/2); angular tensile membrane (1,0,-1);
rest inventory (1,0,0). Each component retains its own energy.
"""
import numpy as np


def minimum_energy(radial, angular):
    p, q = np.broadcast_arrays(radial, angular)
    return np.maximum.reduce([p+2*q, p-q, -2*p-q])


def decompose(density, radial, angular):
    rho, p, q = np.broadcast_arrays(density, radial, angular)
    field = np.maximum(-p, 0.)
    residual = q-field
    radial_wave = p+field
    angular_wave = 2*np.maximum(residual, 0.)
    membrane = np.maximum(-residual, 0.)
    inventory = rho-field-radial_wave-angular_wave-membrane
    return np.array([field, radial_wave, angular_wave, membrane, inventory])

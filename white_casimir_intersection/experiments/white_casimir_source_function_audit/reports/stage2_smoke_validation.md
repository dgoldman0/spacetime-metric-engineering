# Stage 2 Scalar Worldline Proxy Smoke

Status: `pass`.

Loop method: `brownian_bridge`.

Brownian-bridge proxy loops with thickened smoke-test boundary surfaces.

- plate mean is negative: `True`
- plate symmetry relative error: `0.102105`
- gap scaling pass: `True`
- sphere negative proxy pixels: `625`
- sphere contrast |min|/|mean|: `13.2321`
- sphere minimum coordinate: `(0, -1) um`
- estimated full Python-proxy runtime: `2.94` hours

Generated artifacts:

- `outputs/plate_validation_density_proxy.npy`
- `outputs/plate_validation_density_proxy.csv`
- `outputs/sphere_cylinder_density_proxy_smoke.npy`
- `outputs/sphere_cylinder_density_proxy_smoke.csv`
- `reports/fig_plate_validation_density_proxy.png`
- `reports/fig_sphere_cylinder_density_proxy_smoke.png`

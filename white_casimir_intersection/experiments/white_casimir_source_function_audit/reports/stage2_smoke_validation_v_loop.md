# Stage 2 Scalar Worldline Proxy Smoke

Status: `pass`.

Loop method: `v_loop`.

Paper-style v-loop generator following White et al. Eq. 7-9 summary.

- plate mean is negative: `True`
- plate symmetry relative error: `0.0296878`
- gap scaling pass: `True`
- sphere negative proxy pixels: `625`
- sphere contrast |min|/|mean|: `12.4678`
- sphere minimum coordinate: `(-0.25, 1) um`
- estimated full Python-proxy runtime: `2.88` hours

Generated artifacts:

- `outputs/plate_validation_density_proxy_v_loop.npy`
- `outputs/plate_validation_density_proxy_v_loop.csv`
- `outputs/sphere_cylinder_density_proxy_smoke_v_loop.npy`
- `outputs/sphere_cylinder_density_proxy_smoke_v_loop.csv`
- `reports/fig_plate_validation_density_proxy_v_loop.png`
- `reports/fig_sphere_cylinder_density_proxy_smoke_v_loop.png`

"""Finite radial partitions, one-sided bulk sources and physical cost ledgers."""
import numpy as np

from .c1_signed_channels import quadrature, strip_tensor


def proper_length(chart, lower, upper, order=8):
    x, w = quadrature(chart, lower, upper, order=order)
    return float(w @ chart.jets(x)[2])


def refine_partition(chart, ends, lengths, central, wall, order=8):
    """Insert one physical reflector, retaining each parent's population."""
    ends, lengths, central = map(lambda a: np.asarray(a, float), (ends, lengths, central))
    if (lengths.shape != (len(ends)-1,) or central.shape != lengths.shape
            or np.any(np.diff(ends) <= 0) or np.any(lengths <= 0)
            or np.any(central < 0) or not ends[0] < wall < ends[-1]
            or np.any(ends == wall)):
        raise ValueError('new interior wall and aligned finite partition required')
    j = int(np.searchsorted(ends, wall)-1)
    values = []
    for lo, hi in ((ends[j], wall), (wall, ends[j+1])):
        x, w = quadrature(chart, lo, hi, order=order)
        _, a, b, *_ = chart.jets(x)
        values.append(float(w @ (b/a)))
    return (np.insert(ends, j+1, wall), np.r_[lengths[:j], values, lengths[j+1:]],
            np.insert(central, j+1, central[j]))


def cell_columns(chart, coordinate, sides, partitions, eta):
    """Per-unit-central-charge tensors; both limits at physical walls are explicit."""
    x = np.asarray(coordinate, float)
    sides = np.asarray(sides)
    if sides.shape != x.shape or not np.isin(sides, ['left', 'right']).all():
        raise ValueError('each sample requires a left or right bulk limit')
    r, a, _, _, _, ap, app = chart.jets(x)
    columns = []
    for ends, lengths in partitions:
        ends, lengths = np.asarray(ends), np.asarray(lengths)
        index = np.where(sides == 'left', np.searchsorted(ends, x, side='left')-1,
                         np.searchsorted(ends, x, side='right')-1)
        for j, length in enumerate(lengths):
            tensor = strip_tensor(r, a, ap, app, length, strength=eta)
            columns.append(tensor*(index == j)[:, None])
    return np.stack(columns, axis=1)


def cell_costs(chart, partitions, eta, order=8):
    """Proper carrier extent, Killing energy and reflector force per unit c.

    Energy integrates A rho dV in the retained time normalization. Reflector
    forces are local area-integrated radial tractions, with separate rows for
    the two modules. Surface energy and microscopic carrier mass remain separate.
    """
    count = sum(len(lengths) for _, lengths in partitions)
    forces = np.zeros((sum(len(ends) for ends, _ in partitions), count))
    lengths_out, energy, walls = [], [], []
    column = offset = 0
    for module, (ends, lengths) in enumerate(partitions):
        ends, lengths = np.asarray(ends), np.asarray(lengths)
        walls.extend(dict(module=module, coordinate=float(x)) for x in ends)
        for j, length in enumerate(lengths):
            x, w = quadrature(chart, ends[j], ends[j+1], order=order)
            _, a, b, _, _, ap, app = chart.jets(x)
            lengths_out.append(float(w @ b))
            energy.append(float(eta*(-np.pi/(24*length)
                                + (w @ (a*b*(2*app+ap*ap)))/(24*np.pi))))
            r0, a0, _, _, _, ap0, app0 = chart.jets(ends[j:j+2])
            pressure = strip_tensor(r0, a0, ap0, app0, length, strength=eta)[:, 1]
            forces[offset+j:offset+j+2, column] = 4*np.pi*r0*r0*pressure*[-1, 1]
            column += 1
        offset += len(ends)
    return dict(proper_length=np.array(lengths_out), killing_energy=np.array(energy),
                force_matrix=forces, walls=walls)


def occupied_intervals(partitions, central, threshold=1e-6):
    result = []; offset = 0
    for ends, lengths in partitions:
        intervals = []
        for j, c in enumerate(central[offset:offset+len(lengths)]):
            if c <= threshold:
                continue
            lo, hi = map(float, ends[j:j+2])
            if intervals and intervals[-1][1] == lo:
                intervals[-1][1] = hi
            else:
                intervals.append([lo, hi])
        offset += len(lengths)
        result.append(intervals)
    return result


def overlap_intervals(left, right):
    return [[max(a, c), min(b, d)] for a, b in left for c, d in right
            if max(a, c) < min(b, d)]

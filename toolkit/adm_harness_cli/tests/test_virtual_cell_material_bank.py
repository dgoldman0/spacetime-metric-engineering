import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from numpy.testing import assert_allclose
import pytest

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('material_bank', SCRIPTS/'audit_virtual_cell_material_bank.py')
bank = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bank)


def test_two_temperature_contacts_give_capacity_ratio_and_strict_feasible_bank():
    # At a2=1 the photon temperatures are 1 and 4. Hot E=(1,2) requires
    # B_hot<1/2; cold E=(1,4) requires B_cold>1. Hence B_cold/B_hot>2.
    H = np.array([[1.], [2.]])
    C = np.array([[1.], [4.]])
    active = np.ones((4, 2, 1), dtype=bool)
    active[:2] = False
    limits = bank.constant_capacity_thresholds(H, C, H, C*C, np.ones_like(H), active).max(axis=1)[:, 0]
    assert_allclose(limits, [0., 0., 2., 1.])
    assert_allclose(max(limits[0]*limits[1], limits[2]*limits[3]), 2.)
    assert np.all(H/.45 > np.sqrt(C*C))
    assert np.all(C/1.1 < np.sqrt(C*C))


def test_inactive_fluid_contact_leaves_cold_bank_bound_unconstrained():
    one = np.ones((1, 1))
    active = np.zeros((4, 1, 1), dtype=bool)
    active[2:] = True
    values = bank.constant_capacity_thresholds(one, one, 1e-30*one, one, one, active)
    assert values[1, 0, 0] == 0
    assert np.isfinite(values).all()
    active[1] = True
    constrained = bank.constant_capacity_thresholds(one, one, 1e-30*one, one, one, active)
    assert_allclose(constrained[1, 0, 0], 1e30)


def test_empty_active_donor_rejected_and_empty_receiving_bank_allowed():
    one = np.ones((1, 1)); zero = one*0
    active = np.zeros((4, 1, 1), dtype=bool); active[3] = True
    with pytest.raises(ValueError, match='positive energy'):
        bank.constant_capacity_thresholds(one, one, one, zero, one, active)
    received = bank.constant_capacity_thresholds(one, zero, one, one, one, active)
    assert received[3, 0, 0] == 0 and np.isfinite(received).all()


def test_static_rest_budget_uses_each_times_actual_volume_and_keeps_initial_heat():
    D = np.array([[10.], [2.], [4.]])
    shortfall = -np.array([[.2], [.5], [.4]])
    C = np.array([[.25], [.5], [.75]])
    result = bank.additive_inventory_bounds(D, shortfall, C, np.array([[.25], [.25]]))
    assert_allclose(result['added_dust_rest_allowance'], [1.])
    assert result['allowance_time_index'][0] == 1
    assert_allclose(result['required_specific_energy_increase'], [.5])
    assert_allclose(result['required_specific_energy_from_zero'], [.75])
    # A specific-energy swing .1 costs mass 5, which exceeds the available 1.
    assert result['cold_heat_receipts'][0]/.1 > result['added_dust_rest_allowance'][0]


def test_receipt_and_inventory_conservation_is_checked_before_mass_comparison():
    D = np.ones((2, 1)); C = np.array([[0.], [1.]])
    with pytest.raises(ValueError, match='counted receipts'):
        bank.additive_inventory_bounds(D, -D, C, np.array([[.5]]))
    with pytest.raises(ValueError, match='positive full density margin'):
        bank.additive_inventory_bounds(D, D*0, C, np.array([[1.]]))


def test_dimensionless_specific_energy_bound_is_invariant_under_energy_rescaling():
    D = np.array([[2.], [3.]])
    shortfall = -np.array([[.3], [.1]])
    C = np.array([[.2], [.5]]); heat = np.array([[.3]])
    original = bank.additive_inventory_bounds(D, shortfall, C, heat)
    scaled = bank.additive_inventory_bounds(D, 7*shortfall, 7*C, 7*heat)
    assert_allclose(scaled['required_specific_energy_increase'], original['required_specific_energy_increase'])
    assert_allclose(scaled['required_specific_energy_from_zero'], original['required_specific_energy_from_zero'])


def test_consumed_output_requires_its_own_manifest_identity(tmp_path, monkeypatch):
    monkeypatch.setattr(bank, 'ROOT', tmp_path)
    calls = []
    monkeypatch.setattr(bank, 'validate_controls', lambda folder, labels: (calls.append(labels) or {}, []))
    source = tmp_path/'source'; source.mkdir()
    data = source/'temperature.npz'; data.write_bytes(b'original immutable state')
    manifest = {'output_sha256': {data.name: bank.sha256_file(data)}}
    (source/'manifest.json').write_text(json.dumps(manifest))
    hashes, _ = bank.verify_outputs(source, [data.name])
    assert hashes['source/temperature.npz'] == bank.sha256_file(data)
    assert calls == [[]]
    data.write_bytes(b'changed state')
    with pytest.raises(RuntimeError, match='consumed output'):
        bank.verify_outputs(source, [data.name])

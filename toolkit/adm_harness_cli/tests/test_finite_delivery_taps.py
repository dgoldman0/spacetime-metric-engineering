"""Supplied boundary energy and a closed paired return in a flat control."""
import importlib
from pathlib import Path

import numpy as np

from adm_harness.active_transfer_reservoir import MetricJets


class FlatChannel:
    def __init__(self):
        self.t = np.linspace(0., 2., 201)
        self.edges = np.linspace(0., 1., 81)
        self.x = .5*(self.edges[1:]+self.edges[:-1])

    def geometry(self, unused):
        def metric(x):
            one, zero = np.ones_like(x), np.zeros_like(x)
            return MetricJets(one, zero, one, one, zero, zero, zero, zero, zero, zero)
        return metric(self.x), metric(self.edges), np.zeros_like(self.x)


def load_runner(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]/'scripts'))
    return importlib.import_module('evaluate_finite_delivery_taps')


def test_supplied_transparent_wave_keeps_flat_equilibrium(monkeypatch):
    runner = load_runner(monkeypatch)
    channel = FlatChannel()
    state, ledger = runner.transparent_wave(channel, -1, np.ones_like(channel.x), lambda t: 1.)
    np.testing.assert_allclose(state, 1., atol=1e-14)
    np.testing.assert_allclose(sum(row['incoming'] for row in ledger), 2., atol=1e-14)
    np.testing.assert_allclose(sum(row['outgoing'] for row in ledger), 2., atol=1e-14)


def test_return_fills_causally_and_pays_for_its_final_inventory(monkeypatch):
    runner = load_runner(monkeypatch)
    channel = FlatChannel()
    state, ledger = runner.transparent_wave(channel, 1, np.zeros_like(channel.x), lambda t: 1.)
    dx = channel.edges[1]-channel.edges[0]
    incoming = sum(row['incoming'] for row in ledger)
    outgoing = sum(row['outgoing'] for row in ledger)
    np.testing.assert_allclose(dx*state[-1].sum(), incoming-outgoing, atol=1e-14)
    assert np.max(state[20, channel.x > .5]) < 1e-6
    assert abs(dx*state[-1].sum()-1.) < 1e-5

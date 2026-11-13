import math
import pytest
from rates_fx.analytics import (bootstrap_annual_par_swaps,swap_par_rate,bond_pv,bond_dv01,receive_fixed_swap_pv,fx_forward,long_fx_forward_pv,scenario_table,illustrative_curve)

def test_bootstrap_reprices_par_curve():
    c=bootstrap_annual_par_swaps([.02,.03,.04,.05])
    for n in range(1,len(c)+1):
        assert swap_par_rate(c.discount_factor.iloc[:n])==pytest.approx(c.par_rate.iloc[n-1])
def test_bond_dv01_positive():
    c=illustrative_curve()
    assert bond_dv01(c,5,.03)>0
    assert bond_pv(c,5,.03,parallel_shift_bp=100)<bond_pv(c,5,.03)
def test_receive_fixed_at_par_zero():
    c=illustrative_curve()
    assert abs(receive_fixed_swap_pv(c,swap_par_rate(c.discount_factor)))<1e-7
def test_cip():
    assert fx_forward(1.1,1,.02,.04)==pytest.approx(1.1*math.exp(.02))
def test_mtm_zero_at_fair_forward():
    k=fx_forward(1.1,2,.02,.04)
    assert long_fx_forward_pv(1.1,k,2,.02,.04)==pytest.approx(0.0,abs=1e-8)
def test_fx_spot_higher_improves_long_base():
    a=long_fx_forward_pv(1.1,1.1,1,.02,.04)
    b=long_fx_forward_pv(1.2,1.1,1,.02,.04)
    assert b>a
def test_scenarios():
    tab=scenario_table(illustrative_curve(),1.1,.03,1.12,.02,.04)
    assert len(tab)==5

"""Pedagogical annual-pay par swap bootstrap, bond DV01 and CIP FX forwards.
All rates decimal and notionals in quote currency as documented.
"""
from math import exp,log
import numpy as np
import pandas as pd

def bootstrap_annual_par_swaps(par_rates):
    """Par fixed annual vs par floating, spot-start with DF(0)=1; annual nodes 1..N."""
    rates=np.asarray(par_rates,dtype=float)
    if rates.ndim!=1 or not len(rates) or not np.isfinite(rates).all() or (rates<=-0.99).any():
        raise ValueError('Expected 1D annual par rates above -99%')
    dfs=[]
    for rate in rates:
        df=(1-rate*sum(dfs))/(1+rate)
        if df<=0: raise ValueError('Inconsistent par rates: nonpositive discount factor')
        dfs.append(float(df))
    maturities=np.arange(1,len(dfs)+1,dtype=float)
    return pd.DataFrame({'year':maturities.astype(int),'par_rate':rates,'discount_factor':dfs,
                         'cont_zero_rate':-np.log(dfs)/maturities})

def swap_par_rate(discount_factors):
    dfs=np.asarray(discount_factors,dtype=float)
    if len(dfs)==0 or (dfs<=0).any(): raise ValueError('Positive discount factors required')
    return float((1-dfs[-1])/sum(dfs))

def bond_pv(curve, maturity_years, coupon_rate, notional=1_000_000, parallel_shift_bp=0):
    """Annual coupon bond at par redemption; discount from annual curve nodes."""
    if not isinstance(maturity_years,int) or maturity_years<1 or maturity_years>len(curve):
        raise ValueError('Maturity must be an integer annual node within curve')
    if notional<=0:raise ValueError('Notional must be positive')
    df=curve['discount_factor'].to_numpy()[:maturity_years]
    times=np.arange(1,maturity_years+1)
    shifted=df*np.exp(-parallel_shift_bp*0.0001*times)
    cashflows=np.full(maturity_years,coupon_rate*notional)
    cashflows[-1]+=notional
    return float(np.sum(cashflows*shifted))

def bond_dv01(curve,maturity_years,coupon_rate,notional=1_000_000):
    """Positive long-bond DV01 in currency per +1bp yield move (PV down).
    Symmetric: (PV(-1bp)-PV(+1bp))/2.
    """
    return (bond_pv(curve,maturity_years,coupon_rate,notional,-1)-bond_pv(curve,maturity_years,coupon_rate,notional,1))/2

def receive_fixed_swap_pv(curve, fixed_coupon, notional=1_000_000, parallel_shift_bp=0):
    """Spot start, reset floating leg simplified PV=N*(1-DF_N), annual payments."""
    if notional<=0:raise ValueError('Notional must be positive')
    years=np.arange(1,len(curve)+1)
    dfs=curve.discount_factor.to_numpy()*np.exp(-parallel_shift_bp*0.0001*years)
    fixed=notional*fixed_coupon*sum(dfs)
    floating=notional*(1-dfs[-1])
    return float(fixed-floating)

def fx_forward(spot_quote_per_base, maturity_years, base_rate, quote_rate):
    """Continuous CIP. Example EUR/USD: base EUR, quote USD, USD per EUR."""
    if spot_quote_per_base<=0 or maturity_years<0:raise ValueError('Positive spot and nonnegative maturity required')
    return spot_quote_per_base*exp((quote_rate-base_rate)*maturity_years)

def long_fx_forward_pv(spot,contract_forward,maturity,base_rate,quote_rate,base_notional=1_000_000):
    """Long base currency forward MTM in quote currency, no credit adjustments."""
    if base_notional<=0:raise ValueError('Notional must be positive')
    f=fx_forward(spot,maturity,base_rate,quote_rate)
    return base_notional*exp(-quote_rate*maturity)*(f-contract_forward)

def scenario_table(curve,spot,fixed_coupon,contract_forward,base_rate,quote_rate,shock_bp=50,fx_shock_pct=0.05):
    """Separate +rate bp parallel discount shift and +/- FX spot shocks."""
    bond_year=min(5,len(curve))
    rows=[]
    for name,rate_bp,fx_pct in [('base',0,0),('rates_up',shock_bp,0),('rates_down',-shock_bp,0),('fx_up',0,fx_shock_pct),('fx_down',0,-fx_shock_pct)]:
        rows.append({'scenario':name,'bond_pv_quote':bond_pv(curve,bond_year,fixed_coupon,parallel_shift_bp=rate_bp),
                     'receive_fixed_swap_pv_quote':receive_fixed_swap_pv(curve,fixed_coupon,parallel_shift_bp=rate_bp),
                     'fx_forward_mtm_quote':long_fx_forward_pv(spot*(1+fx_pct),contract_forward,1,base_rate,quote_rate)})
    return pd.DataFrame(rows)

def illustrative_curve():
    return bootstrap_annual_par_swaps([.026,.027,.028,.029,.030,.031,.032])

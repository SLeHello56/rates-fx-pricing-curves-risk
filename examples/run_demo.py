from rates_fx.analytics import illustrative_curve,swap_par_rate,bond_dv01,fx_forward
c=illustrative_curve()
print(c.to_string(index=False))
print('Par rate',swap_par_rate(c.discount_factor))
print('5y bond DV01 per 1bp:',bond_dv01(c,5,.03))
print('EUR/USD 1y fair forward:',fx_forward(1.10,1,.02,.04))

from rates_fx.historical import fetch_ecb_eurusd,fetch_fred_us_treasury
class FakeResponse:
    def __init__(self,text):self.text=text
    def raise_for_status(self):pass
def test_ecb_parser(monkeypatch):
    monkeypatch.setattr('rates_fx.historical.requests.get',lambda *a,**kw:FakeResponse('TIME_PERIOD,OBS_VALUE\n2025-10-01,1.15\n'))
    d=fetch_ecb_eurusd()
    assert len(d)==1
    assert d.eurusd.iloc[0]==1.15
def test_fred_parser(monkeypatch):
    monkeypatch.setattr('rates_fx.historical.requests.get',lambda *a,**kw:FakeResponse('observation_date,DGS10\n2025-10-01,4.20\n'))
    d=fetch_fred_us_treasury()
    assert len(d)==1
    assert d.yield_percent.iloc[0]==4.2

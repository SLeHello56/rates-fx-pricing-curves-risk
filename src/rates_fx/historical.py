"""Optional public context: ECB euro FX fix and FRED US Treasury yields.
These historical series are NOT OIS/swap discount curves; never combine as if same instrument.
"""
from io import StringIO
import pandas as pd
import requests

def fetch_ecb_eurusd(start='2023-01-01',end=None):
    url='https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A'
    params={'startPeriod':start,'format':'csvdata','detail':'dataonly'}
    if end: params['endPeriod']=end
    resp=requests.get(url,params=params,headers={'Accept':'text/csv'},timeout=30)
    resp.raise_for_status()
    df=pd.read_csv(StringIO(resp.text))
    if not {'TIME_PERIOD','OBS_VALUE'}.issubset(df.columns):raise ValueError('Unexpected ECB CSV structure')
    result=df[['TIME_PERIOD','OBS_VALUE']].rename(columns={'TIME_PERIOD':'date','OBS_VALUE':'eurusd'})
    result['date']=pd.to_datetime(result.date)
    result['eurusd']=pd.to_numeric(result.eurusd,errors='coerce')
    return result.dropna().sort_values('date').reset_index(drop=True)

def fetch_fred_us_treasury(series='DGS10',start='2023-01-01'):
    if series not in ('DGS1','DGS2','DGS5','DGS10'):raise ValueError('Unsupported Treasury maturity')
    r=requests.get('https://fred.stlouisfed.org/graph/fredgraph.csv',params={'id':series,'cosd':start},timeout=30)
    r.raise_for_status()
    df=pd.read_csv(StringIO(r.text))
    col='observation_date' if 'observation_date' in df else 'DATE'
    df=df.rename(columns={col:'date',series:'yield_percent'})
    if not {'date','yield_percent'}.issubset(df):raise ValueError('Unexpected FRED CSV structure')
    df['date']=pd.to_datetime(df.date)
    df['yield_percent']=pd.to_numeric(df.yield_percent,errors='coerce')
    return df.dropna().reset_index(drop=True)

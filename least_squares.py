import pandas as pd
import numpy  as np
import math
from collections import namedtuple
from typing import List, NamedTuple

class LsmChangeResult(NamedTuple):
  """最小二乗による半径変化量を格納するNamedTuple"""
  cap : List[float]
  rod : List[float]
  cx  : float
  cy  : float
  r   : float

def calc_corrected_roundness(coord: pd.DataFrame, std_radius: float) -> LsmChangeResult:
  """最小二乗による半径変化量を計算する"""
  cap_y = coord["cap_y"].tolist()
  cap_x = coord["cap_x"].tolist()
  rod_y = coord["rod_y"].tolist()
  rod_x = coord["rod_x"].tolist()
  
  rad = std_radius
  pre_y = cap_y + list(reversed(rod_y))
  pre_x = cap_x + list(reversed(rod_x))
  
  df1 = pd.DataFrame()
  df1["preY"] = pre_y
  df1["preX"] = pre_x
  df1['x0y1'] = (df1['preX'] ** 0) * (df1['preY'] ** 1)
  df1['x0y2'] = (df1['preX'] ** 0) * (df1['preY'] ** 2)
  df1['x0y3'] = (df1['preX'] ** 0) * (df1['preY'] ** 3)
  df1['x1y0'] = (df1['preX'] ** 1) * (df1['preY'] ** 0)
  df1['x1y1'] = (df1['preX'] ** 1) * (df1['preY'] ** 1)
  df1['x1y2'] = (df1['preX'] ** 1) * (df1['preY'] ** 2)
  df1['x1y3'] = (df1['preX'] ** 1) * (df1['preY'] ** 3)
  df1['x2y0'] = (df1['preX'] ** 2) * (df1['preY'] ** 0)
  df1['x2y1'] = (df1['preX'] ** 2) * (df1['preY'] ** 1)
  df1['x2y2'] = (df1['preX'] ** 2) * (df1['preY'] ** 2)
  df1['x2y3'] = (df1['preX'] ** 2) * (df1['preY'] ** 3)
  df1['x3y0'] = (df1['preX'] ** 3) * (df1['preY'] ** 0)

  df2 = pd.DataFrame()
  df2['col1'] = [df1['x2y0'].sum(), df1['x1y1'].sum(), df1['x1y0'].sum()]
  df2['col2'] = [df1['x1y1'].sum(), df1['x0y2'].sum(), df1['x0y1'].sum()]
  df2['col3'] = [df1['x1y0'].sum(),  df1['x0y1'].sum(), len(df1)]

  df3 = pd.DataFrame()
  df3['col1'] = [-(df1['x3y0'].sum() + df1['x1y2'].sum()), 
                 -(df1['x2y1'].sum() + df1['x0y3'].sum()),
                 -(df1['x2y0'].sum() + df1['x0y2'].sum()) ]
  
  invdf2 = np.linalg.inv(df2.values)
  resultABC = np.dot(invdf2, df3.values)
  a = resultABC[0][0]
  b = resultABC[1][0]
  c = resultABC[2][0]
  cx = -a/2
  cy = -b/2
  r = math.sqrt(cx**2 + cy**2 - c)

  df4 = pd.DataFrame()
  df4['lsmCapY'] = cap_y - cy
  df4['lsmCapX'] = cap_x - cx
  df4['lsmRodY'] = rod_y - cy
  df4['lsmRodX'] = rod_x - cx
  df4['lsmChangeCap'] = ((df4['lsmCapY']**2 + df4['lsmCapX']**2)**(1/2) - rad) * 10**3
  df4['lsmChangeRod'] = ((df4['lsmRodY']**2 + df4['lsmRodX']**2)**(1/2) - rad) * 10**3 
  
  lsmChangeCap = df4['lsmChangeCap'].tolist()
  lsmChangeRod = df4['lsmChangeRod'].tolist()

  return LsmChangeResult(cap=lsmChangeCap, rod=lsmChangeRod, cx=cx, cy=cy, r=r)
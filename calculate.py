import os
import re
import sys
import csv
import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
import math
import openpyxl
from openpyxl.styles import Alignment, Font
from dataclasses import dataclass
from typing import List
from abc import ABC, abstractmethod
from read_excel import *
from file_utils import *
from least_squares import *
from result import *

def activate_fft(amount_of_change, threshold) -> List[float]:   
  """FFT -> フィルター -> 逆FFT を行い、平滑化されたデータを返すメソッド"""
  original_len = len(amount_of_change)
  signal = np.array(amount_of_change)
  
  # 信号を反転させて連結し、周期的な境界の不連続性をなくす
  # 例: [1, 2, 3] -> [1, 2, 3, 3, 2, 1]
  padded_signal = np.concatenate([signal, signal[::-1]])

  # FFT、フィルタリング、逆FFT
  fft_result = np.fft.fft(padded_signal)
  power = np.abs(fft_result) / len(padded_signal) 
  filter_mask = power >= threshold
  filtered_fft = fft_result * filter_mask
  
  inverse_fft_result = np.fft.ifft(filtered_fft)
  
  # パディング部分を捨てて元の長さに戻す
  smoothed_signal = inverse_fft_result.real[:original_len]
  
  return smoothed_signal.tolist()
  
  # fft = np.fft.fft(amount_of_change)
  # power = np.abs(fft/len(amount_of_change))
  # filter = list(
  # map(float, power >= threshold)
  # )
  # filtered = fft * filter
  # inv_fft = np.fft.ifft(filtered)
  # inv_fft_real = inv_fft.real.tolist()
  # return inv_fft_real

def cap_rod_concat(cap: list, rod:list) -> List[float]:
  """capとrodを連結して一続きにするメソッド"""
  change_radius = cap + rod
  change_radius.append(change_radius[0])
  return change_radius

def main_calculation_flow(file_path:str, props: InputProperty) -> List[BaseResult]:
  # それぞれのクラスをインスタンス化
  all_data = InputData.from_excel(file_path)
  
  #エラーのないものをフィルタリング
  valid_data = [data for data in all_data if not data.is_error]

  #基準マーカをチェック
  std_data_list : List[InputData] = []
  non_std_data_list : List[InputData] = []
  for data in valid_data:
    if data.is_standard:
      std_data_list.append(data)
    else:
      non_std_data_list.append(data)

  if len(std_data_list) != 1:
    raise ValueError("基準となるデータは１つだけ設定してください．")
  std_data = std_data_list[0]

  # valid_data内のcoordinateをソートして，sorted_coordinateに再登録
  for data in valid_data:
    sorted_cap = data.coord[["cap_y", "cap_x"]].sort_values(by="cap_x").reset_index(drop=True)
    sorted_rod = data.coord[["rod_y", "rod_x"]].sort_values(by="rod_x", ascending=False).reset_index(drop=True)
    sorted_coord = pd.concat([sorted_cap, sorted_rod], axis=1)
    data.sorted_coord = sorted_coord

  # 基準データから必要なデータを計算
  std_df = std_data.sorted_coord
  std_rad_cap = np.sqrt(std_df["cap_y"]**2 + std_df["cap_x"]**2)
  std_rad_rod = np.sqrt(std_df["rod_y"]**2 + std_df["rod_x"]**2)

  std_radius = (std_rad_cap.mean() + std_rad_rod.mean()) / 2
  std_diameter = np.sqrt((std_df["cap_y"] - std_df["rod_y"])**2 + (std_df["cap_x"] - std_df["rod_x"])**2)
  std_rod_dist = np.sqrt((std_df["rod_x"].iloc[0] - std_df["rod_x"].iloc[-1])**2
                         + (std_df["rod_y"].iloc[0] - std_df["rod_y"].iloc[-1])**2)

  r_degree = 180 + abs(np.degrees(np.arctan2(std_df["rod_y"],-std_df["rod_x"])))
  c_degree = abs(np.degrees(np.arctan2(std_df["cap_y"], -std_df["cap_x"])))
  rad_degrees = pd.concat([c_degree, r_degree.iloc[::-1]])
  rad_degrees = pd.concat([rad_degrees, pd.Series(rad_degrees.iloc[0])], ignore_index=True)
  rad_degrees = rad_degrees.tolist()
  

  dia_degrees = abs(np.degrees(np.arctan2(std_df["cap_y"], -std_df["cap_x"])))
  dia_degrees = dia_degrees.tolist()

  # 変化量を求める
  calculated_results : List[BaseResult] = []
  for data in valid_data:
    coord_df = data.sorted_coord

    rad_cap = np.sqrt(coord_df["cap_y"]**2 + coord_df["cap_x"]**2)
    rad_rod = np.sqrt(coord_df["rod_y"]**2 + coord_df["rod_x"]**2)
    change_cap = (rad_cap - std_rad_cap)*10**3
    change_rod = (rad_rod - std_rad_rod)*10**3
    change_cap = change_cap.tolist()
    change_rod = change_rod.tolist()
    change_radius = cap_rod_concat(change_cap, change_rod)

    lsm_result = calc_corrected_roundness(coord=coord_df, std_radius=std_radius)
    lsm_change_radius = cap_rod_concat(cap=lsm_result.cap, rod=lsm_result.rod)

    diameter = np.sqrt((coord_df["cap_y"] - coord_df["rod_y"])**2 + (coord_df["cap_x"] - coord_df["rod_x"])**2)
    change_diameter = (diameter - std_diameter)*10**3
    change_diameter = change_diameter.tolist()

     # 共通の引数を辞書として準備
    base_args = {
        "situation": data.situation,
        "fft_on_or_off": data.fft_on_or_off,
        "is_standard": data.is_standard,
        "line_color": data.line_color,
        "is_error": data.is_error,
        "coord": data.coord,
        "change_radius": change_radius,
        "lsm_change_radius": lsm_change_radius,
        "change_diameter": change_diameter,
        "rad_degrees": rad_degrees,
        "dia_degrees": dia_degrees,
        "std_rod_dist": std_rod_dist,
        "std_situation": std_data.situation,
        "std_coord": std_data.sorted_coord,
        "lsm_cx": lsm_result.cx,
        "lsm_cy": lsm_result.cy,
        "lsm_r": lsm_result.r,
    }
        
    if data.fft_on_or_off:
      fft_change_cap = activate_fft(change_cap, props.threshold_rad)
      fft_change_rod = activate_fft(change_rod, props.threshold_rad)
      fft_change_radius = cap_rod_concat(cap=fft_change_cap, rod=fft_change_rod)
      
      fft_lsm_cap = activate_fft(lsm_result.cap, props.threshold_lsm)
      fft_lsm_rod = activate_fft(lsm_result.rod, props.threshold_lsm)
      fft_lsm_change_radius = cap_rod_concat(cap=fft_lsm_cap, rod=fft_lsm_rod)

      fft_change_diameter=activate_fft(change_diameter, props.threshold_dia)

      # FFTResult固有の引数を追加
      fft_args = {
          "fft_change_radius": fft_change_radius,
          "fft_lsm_change_radius": fft_lsm_change_radius,
          "fft_change_diameter": fft_change_diameter
      }
      result = FFTResult(**base_args, **fft_args)
    else:
        result = NonFFTResult(**base_args)
      
        # sorted_coordは__init__から除外されているので、後から手動で設定する
    result.sorted_coord = data.sorted_coord
    calculated_results.append(result)
    
  return calculated_results
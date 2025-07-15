import os
import re
import sys
import csv
import openpyxl as pyxl
import pandas as pd
import numpy  as np
import matplotlib.pyplot as plt
import math
from dataclasses import dataclass
from typing import List

import pandas as pd
import openpyxl as pyxl
from dataclasses import dataclass, field
from typing import List

@dataclass
class InputData:
    """
    Excelの座標入力シートの入力データを分類して保持するクラス
    """
    situation: str
    fft_on_or_off: bool
    is_standard: bool
    line_color: str
    is_error: bool
    coord: pd.DataFrame
    sorted_coord: pd.DataFrame | None = field(init=False, default=None)

    @classmethod
    def from_excel(cls, file_path: str) -> List['InputData']:
        """
        Excelの入力データをInputDataクラスに登録するメソッド
        """
        all_input_data = []
        input_df = pd.read_excel(file_path, header=None, sheet_name="座標入力")
        for col_start in range(0, input_df.shape[1], 4):
            situation = input_df.iloc[0, col_start]
            fft_on_or_off_str = input_df.iloc[2, col_start]
            if fft_on_or_off_str == "on":
                fft_on_or_off = True
            else:
                fft_on_or_off = False

            is_standard_str = input_df.iloc[2, col_start + 1]
            if is_standard_str == "基準とする":
                is_standard = True
            else:
                is_standard = False
            line_color = input_df.iloc[2, col_start + 2]
            is_error_str = input_df.iloc[2, col_start + 3]
            if is_error_str == "行数OK":
                is_error = False
            else:
                is_error = True
            coord = input_df.iloc[4:, col_start:col_start + 4].copy()
            coord = coord.reset_index(drop=True)
            coord.columns = ["cap_y", "cap_x", "rod_y", "rod_x"]

            try:
                coord = coord.astype(float)
            except ValueError as e:
                raise TypeError(f"座標データに数値以外の値が含まれています。 situation: '{situation}', エラー: {e}")
            
            input_data_item = cls(
                situation=situation,
                fft_on_or_off=fft_on_or_off,
                is_standard=is_standard,
                line_color=line_color,
                is_error=is_error,
                coord=coord
            )
            all_input_data.append(input_data_item)
        return all_input_data


@dataclass
class InputProperty:
    """
    Excelのグラフ設定シートの入力データを分類して保持するクラス
    """
    is_auto: bool
    max_val: float
    min_val: float
    interval: float
    rotation: float
    threshold_rad: float
    threshold_dia: float
    threshold_lsm: float

    @classmethod
    def from_excel(cls, file_path: str) -> 'InputProperty':
        """
        Excelの入力データをInputPropertyクラスに登録するメソッド
        """
        wb = pyxl.load_workbook(file_path)
        sht = wb["設定"]
        max_val = sht["C6"].value
        min_val = sht["C7"].value
        interval = sht["C8"].value
        rotation = sht["G3"].value
        auto_or_manual_str = sht["C5"].value
        if auto_or_manual_str == "自動":
            is_auto = True
        else:
            is_auto = False
        threshold_dia = sht["C4"].value
        threshold_rad = sht["D4"].value
        threshold_lsm = sht["E4"].value

        input_property_item = cls(
            is_auto=is_auto,
            max_val=float(max_val),
            min_val=float(min_val),
            interval=float(interval),
            rotation=float(rotation),
            threshold_rad=float(threshold_rad),
            threshold_lsm=float(threshold_lsm),
            threshold_dia=float(threshold_dia)
        )
        return input_property_item
    

    

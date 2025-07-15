import os
import re
from typing import List
from pathlib import Path
import openpyxl


def response() -> str: 
  response_file = input("読み込むフォルダかファイル名は？：")
  if response_file.endswith('"'):
    file_or_folder_name = response_file.strip('"')
  elif response_file.startswith("& "):
    file_or_folder_name = response_file.strip("& '")
  else:
    file_or_folder_name = response_file
  return file_or_folder_name

def arg_to_xlsx(file_or_folder_name: str) -> List[str]:
    """
    指定されたパスから、「座標入力」と「設定」シートが両方含まれているExcelファイルのみをリストアップ。
    """
    xlsx_list = []   
    potential_files = []

    if os.path.isdir(file_or_folder_name):
        files = os.listdir(file_or_folder_name)
        for a_file in files:
            if a_file.endswith(".xlsx"):
              full_path = os.path.join(file_or_folder_name, a_file)
              potential_files.append(full_path)
              
    elif file_or_folder_name.endswith(".xlsx"):
        potential_files.append(file_or_folder_name)

    for file_path in potential_files:
      try:
          workbook = openpyxl.load_workbook(file_path, read_only=True)
          sheet_names = workbook.sheetnames          
          if "座標入力" in sheet_names and "設定" in sheet_names:
              xlsx_list.append(file_path) 
      except Exception as e:
          print(f"ファイル処理中にエラー: {file_path}, {e}")

    return xlsx_list

def make_filename(r_file_name:str) -> str: 
  r_file_path = Path(r_file_name)
  w_folder_path = r_file_path.parent / "計算結果フォルダ"
  w_folder_path.mkdir(exist_ok=True)
  w_file_name = w_folder_path / f"結果_{r_file_path.name}"
  return w_file_name

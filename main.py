from read_excel import *
from file_utils import *
from least_squares import *
from result import *
from calculate import *
from plotter import *
import warnings

"""メイン制御モジュール"""

def main(a_file):
    w_file_name = make_filename(a_file)

    #プロパティ読み込みとメイン計算処理の実行
    props = InputProperty.from_excel(a_file)
    all_results = main_calculation_flow(file_path=a_file, props=props)
    report_output_results = [a_result for a_result in all_results if not a_result.is_standard] 

    if not all_results:
        print("処理対象データがありません。処理を修了します。")
    else:
        #グラフ生成・保存
        plotter = Plotter(results=all_results, props=props, write_filename=w_file_name)
        plotter.plot_all_graphs()

        #Excelレポートブック作成
        with pd.ExcelWriter(w_file_name, engine="openpyxl") as writer:
            for a_result in report_output_results:
                a_result.write_to_output_excel_sheet(writer)


if __name__ == "__main__":
    warnings.simplefilter('ignore')
    try:
        read_file_or_folder = response()
        file_list = arg_to_xlsx(read_file_or_folder)
        if len(file_list) > 0:
            for a_file in file_list:
                main(a_file)
            print("処理が完了しました。")
        else:
            print("読み込み対象のファイルがありません。")
            
    except Exception as e:
        print(f"エラーが発生しました: {e}")






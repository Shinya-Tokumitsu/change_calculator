from result import *
from pathlib import Path
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'MS Gothic'

style_dict = {
    '非表示': {'visible': False},
    '赤':     {'color': 'red'},
    '青':     {'color': 'blue'},
    '緑':     {'color': 'green'},
    '黒':     {'color': 'black'},
    '赤（点線）': {'color': 'red',   'linestyle': 'dotted'},
    '青（点線）': {'color': 'blue',  'linestyle': 'dotted'},
    '緑（点線）': {'color': 'green', 'linestyle': 'dotted'},
    '黒（点線）': {'color': 'black', 'linestyle': 'dotted'},
}

class Plotter:
    """複数の計算結果をまとめてグラフ化するクラス"""
    def __init__(self, results: List[BaseResult], props: InputProperty, write_filename: str):
        self.results = results
        self.props = props
        self.write_filename = write_filename
        self.x_axis_for_dia = results[0].dia_degrees
        self.x_axis_for_rad = np.radians(results[0].rad_degrees)

    def plot_all_graphs(self):
        """全種類のグラフを生成・保存する"""
        self._plot_rad_graph("半径変化量", "change_radius", "fft_change_radius")
        self._plot_rad_graph("半径変化量（最小二乗円補正）", "lsm_change_radius", "fft_lsm_change_radius")
        self._plot_diameter_graph("内径変化量", "change_diameter", "fft_change_diameter")

    def _plot_diameter_graph(self, title: str, raw_attr: str, fft_attr: str):
        """内径変化量のグラフ描画"""
        plt.figure(figsize=(7, 7))
        for res in self.results:
            y_data = getattr(res, fft_attr) if isinstance(res, FFTResult) else getattr(res, raw_attr)
            plot_label = None if res.line_color == "非表示" else res.situation
            plt.plot(self.x_axis_for_dia, y_data, label=plot_label, **style_dict[res.line_color])
            plt.plot()
        plt.xlabel("角度 [degree]", fontname = "MS Gothic", fontsize=20)
        plt.ylabel("内径変化量 [µm]", fontname = "MS Gothic", fontsize=20)
        plt.legend(prop={"family":"MS Gothic", "size": 15})
        plt.tick_params(axis='both', labelsize=15)
        plt.xlim(0, 180)
        x_scale = np.arange(0, 180 + 30, 30)
        plt.xticks(x_scale)
        if not self.props.is_auto:
            plt.ylim(self.props.min_val, self.props.max_val)
            try:
                y_scale = np.arange(
                    self.props.min_val,
                    self.props.max_val + self.props.interval,
                    self.props.interval
                )
                plt.yticks(y_scale)
            except Exception as e:
                print(f"警告: Y軸の目盛設定に失敗しました。自動設定を使用します。({e})")
        r_file_path = Path(self.write_filename)
        r_file_path_name = r_file_path.name.replace(".xlsx", "")
        w_graph_folder_path = r_file_path.parent / f"{r_file_path_name}_グラフフォルダ"
        w_graph_folder_path.mkdir(exist_ok=True)
        graph_filename = w_graph_folder_path / f"{r_file_path_name}_{title}.png"
        graph_title = r_file_path_name.replace("結果_", "") + "_" + title + "\n"
        plt.title(graph_title, fontsize=25)
        plt.savefig(graph_filename)
        plt.close()
        print(f"グラフを保存しました: {graph_filename}")
             
    def _plot_rad_graph(self, title: str, raw_attr: str, fft_attr: str):
        """半径変化量のグラフ描画"""
        fig, ax =  plt.subplots(figsize=(12, 10), subplot_kw={'projection': 'polar'})

        overall_max = -float("inf")
        overall_min = float("inf")
        all_y_data = []

        for res in self.results:
            y_data = getattr(res, fft_attr) if isinstance(res, FFTResult) else getattr(res, raw_attr)
            all_y_data.append(y_data)
            if max(y_data) > overall_max:
                overall_max = max(y_data)
            if min(y_data) < overall_min:
                overall_min = min(y_data)

        max_abs_val = max(overall_max, abs(overall_min))


        for i, res in enumerate(self.results):
            y_data = all_y_data[i]
            plot_label = None if res.line_color == '非表示' else res.situation
            plt.plot(self.x_axis_for_rad, y_data, label=plot_label, **style_dict[res.line_color])
                
        if max_abs_val > 30:
            ax.set_rticks([-250, -100, -75, -50, -25, 0, 25, 50, 75, 100]) 
            ax.set_yticklabels(['', '-100[µm]', '-75', '-50', '-25', '0', '25', '50', '75', '100'])
        elif max_abs_val > 20:
            ax.set_rticks([-70, -30, -20, -10, 0, 10, 20, 30])
            ax.set_yticklabels(["", "-30[µm]", "-20",  "-10", "0", "10", "20", "30"])
        else:
            ax.set_rticks([-60, -20, -15, -10, -5, 0, 5, 10, 15, 20])
            ax.set_yticklabels(["", "-20[µm]", "-15", "-10", "-5", "0", "5", "10", "15", "20"])

        ax.tick_params(axis='y', labelsize=18)
        ax.tick_params(axis='x', labelsize=20)
        ax.set_theta_direction(-1)
        ax.set_rlabel_position(-50)  # メモリラベルの位置調整
        ax.set_theta_zero_location("W")  
        ax.set_theta_offset(np.radians(-self.props.rotation + 180))
        ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1), fontsize=20)
        r_file_path = Path(self.write_filename)
        r_file_path_name = r_file_path.name.replace(".xlsx", "")
        w_graph_folder_path = r_file_path.parent / f"{r_file_path_name}_グラフフォルダ"
        w_graph_folder_path.mkdir(exist_ok=True)
        graph_filename = w_graph_folder_path / f"{r_file_path_name}_{title}.png"
        graph_title = r_file_path_name.replace("結果_", "") + "_" + title + "\n"
        plt.title(graph_title, fontsize=25)
        plt.savefig(graph_filename)
        plt.close()
        print(f"グラフを保存しました: {graph_filename}")







#   plt.plot(degrees, pre_invfft, label="運転時")
#   plt.xlabel("角度[°]", fontname = "MS Gothic")
#   plt.ylabel("内径変化量 [µm]", fontname = "MS Gothic")
#   plt.legend(prop={"family":"MS Gothic"})
#   plt.ylim([-100, 100])
#   # plt.ylim([-30, 35])
#   plt.title(file_name)
#   plt.savefig(fname = dir_path + "\\result\\" + file_name + "_figure.png") 
#   plt.close()
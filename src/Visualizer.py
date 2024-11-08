import os
import config as p
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle
# from matplotlib.widgets import Slider
import plotly.graph_objects as go

class OnlineVisualizer:

    def __init__(self, monitor):
        self.monitor = monitor

    def show_voltages(self):
        while True:
            os.system('cls')
            data = self.monitor.get_data()
            min_v = 4
            for i in list(data.keys()):
                if data[i] == 0: del data[i]
                elif data[i] < min_v: 
                    min_v = data[i]
    
    def show_temperatures(self):
        pass

    def plot_voltages(self):
        fig, ax = plt.subplot()         # Create plot
        c = []

        # Update loop
        while True:
            data = self.monitor.get_data()

            stack_plots = [
                ax.scatter(
                    data[28*i:28*(i+1)],
                    data[-1][28*i:28*(i+1)],
                    c=c[i]
                ) 
                for i in range(p.N_STACKS)
            ]
            for i, plot in enumerate(stack_plots):
                start = 28*i
                end = 28*(i+1)
                voltages = df.loc[time_slider.val<df.index].iloc[0][start:end]
                plot.set_offsets(np.c_[df.columns[start:end], voltages]))
            fig.canvas.draw_idle()

        plt.show()

    
    def plot_temperatures(self):
        pass


class OfflineVisualizer:

    def __init__(self, file):
        self.file = file
        self.df = pd.read_csv(file, index_col=0)
    
    def plot_voltages(self):
        pass
        # df = self.df
        # df[[
        #     'Cell14_s1_spi2',
        #     'Cell14_s2_spi3',
        #     'Cell14_s3_spi2',
        #     'Cell14_s4_spi3',
        #     'Cell14_s5_spi2',
        # ]] = np.NaN*np.ones((len(df.index), 5))
        # soc = pd.read_csv('lut_soc.csv', index_col=1)

        # soc_initial = 10
        # vmin = float(soc.loc[soc.index>soc_initial].iloc[0])

        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        # fig.subplots_adjust(bottom=0.2)
        # plt.title(self.file)
        # plt.xlim([0, 17])
        # plt.ylim([0, 6])

        # vcells = df.min()
        # cells = {}
        # W = 1; H = 0.2
        # Wsep = 0.1; Hsep = 0.1
        # for i in range(1, 6):
        #     for j in range(2, 4):
        #         for k in range(1, 15):
        #             vcell = vcells[f'Cell{k}_s{i}_spi{j}']
        #             if not np.isnan(vcell):
        #                 c = ['r', 'g', 'b', 'y', 'm'][i-1] if vcell < vmin else 'w'
        #                 cells[f'Cell{k}_s{i}_spi{j}'] = ax.add_patch(
        #                     Rectangle(
        #                         ((Wsep+W)*k, 2*Hsep*i+(Hsep+H)*(j+2*i)), W, H,
        #                         fc=c, ec='k'
        #                     )
        #                 )

        # def update(val):
        #     num = 0
        #     vmin = float(soc.loc[soc.index>time_slider.val].iloc[0])
        #     for i in range(1, 6):
        #         for j in range(2, 4):
        #             for k in range(1, 15):
        #                 vcell = vcells[f'Cell{k}_s{i}_spi{j}']
        #                 if not np.isnan(vcell):
        #                     if vcell < vmin: num += 1
        #                     cells[f'Cell{k}_s{i}_spi{j}'].set_facecolor(
        #                         ['r', 'g', 'b', 'y', 'm'][i-1] if vcell < vmin else 'w'
        #                     )
        #     fig.canvas.draw_idle()

        # time_slider.on_changed(update)

if __name__=='__main__':
    from classes.Monitor import FileMonitor
    OnlineVisualizer(FileMonitor('data/20240508_1700.csv')).show_voltages()
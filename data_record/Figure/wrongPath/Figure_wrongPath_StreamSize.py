# 读取excel数据进行绘图
import numpy as np
import pandas
from matplotlib import rcParams, pyplot as plt

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.axes3d import Axes3D

import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator, AutoMinorLocator



if __name__ == '__main__':
    # draw_figure()
    config = {
        "font.family": 'serif',
        "font.size": 20,
        "mathtext.fontset": 'stix',
        "font.serif": ['Times New Roman']  # ['SimSun'],
    }  # mac字体不一样   Songti SC  windows Simsun
    rcParams.update(config)

    df1 = pandas.read_excel(r'../../错误转发路径/流中包的数量/数据统计_streamSize_10_2022_0821_2230.xlsx')
    data1 = np.array(df1)

    df2 = pandas.read_excel(r'../../错误转发路径/流中包的数量/数据统计_streamSize_50_2022_0901_0353.xlsx')
    data2 = np.array(df2)

    df3 = pandas.read_excel(r'../../错误转发路径/流中包的数量/数据统计_streamSize_100_2022_0901_0705.xlsx')
    data3 = np.array(df3)

    x_array1 = data1[:, 0][0:12]
    y_Jaccard1 = data1[:, 6][0:12]
    y_RandIndex1 = data1[:, 8][0:12]

    x_array2 = data2[:, 0][0:12]
    y_Jaccard2 = data2[:, 6][0:12]
    y_RandIndex2 = data2[:, 8][0:12]

    x_array3 = data3[:, 0][0:12]
    y_Jaccard3 = data3[:, 6][0:12]
    y_RandIndex3 = data3[:, 8][0:12]

    fw = 10 / 2.54
    fh = 8 / 2.54
    fig = plt.figure(figsize=(8, 6))
    ax1 = fig.subplots()
    # plt.figure(figsize=(14, 7))
    # ax1.spines['left'].set_visible(False)  # 去掉左边框
    # ax1.spines['right'].set_visible(False)  # 去掉右边框
    # ax.spines['top'].set_visible(False)

    # ax1.tick_params("y", colors='firebrick')
    # ax1.tick_params("x",colors='k')
    plt.rcParams['font.sans-serif'] = 'SimSun'
    plt.plot(x_array1, y_Jaccard1, 'o', linewidth=1.5, color="firebrick", linestyle="-", markerfacecolor='white',
             markersize=5,
             markeredgecolor='firebrick', label='#Packets:10')
    plt.plot(x_array2, y_Jaccard2, 's', linewidth=1.5, color="firebrick", linestyle="-", markerfacecolor='white',
             markersize=5,
             markeredgecolor='firebrick', label='#Packets:50')
    plt.plot(x_array3, y_Jaccard3, '^', linewidth=1.5, color="firebrick", linestyle="-", markerfacecolor='white',
             markersize=5,
             markeredgecolor='firebrick', label='#Packets:100')
    # plt.legend(loc='lower right')
    plt.ylim(0, 1.0)
    # plt.ylabel('Jaccard')
    # ax1.set_ylabel('imbanlance', fontsize=15)
    plt.xlabel('Maliciousness')

    ax2 = ax1.twinx()
    # ax2.spines['left'].set_visible(False)  # 去掉左边框
    # ax2.spines['right'].set_visible(False)  # 去掉右边框
    plt.plot(x_array1, y_RandIndex1, 'o', linewidth=1.2, color="g", linestyle="--", markerfacecolor='white',
             markersize=5,
             markeredgecolor='g', label='#Packets:5')
    plt.plot(x_array2, y_RandIndex2, 's', linewidth=1.2, color="g", linestyle="--", markerfacecolor='white',
             markersize=5,
             markeredgecolor='g', label='#Packets:10')
    plt.plot(x_array3, y_RandIndex3, '^', linewidth=1.2, color="g", linestyle="--", markerfacecolor='white',
             markersize=5,
             markeredgecolor='g', label='#Packets:20')
    # plt.legend(loc=[0.7,0.05])
    plt.ylim(0, 1.0)
    # plt.ylabel('Rand Index')
    # ax1.set_xlabel("X1", color=c1, fontsize=fontsize)
    ax1.set_ylabel("Threat Score", color="firebrick", fontsize=20)
    # ax2.set_xlabel('X2', color=c2, fontsize=fontsize)
    ax2.set_ylabel('Rand Index', color="g", fontsize=20)
    # ax2.set_xlabel('attributes', fontsize=15)
    # ax2.set_ylabel('ratio', fontsize=15)
    legend = ax1.legend(loc='lower right', edgecolor='black', fancybox=True, frameon=True)  # Add a legend.
    ax = plt.gca()

    ax.spines['left'].set_color('firebrick')
    ax.spines['right'].set_color('green')
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['right'].set_linewidth(1.2)
    #
    # # 图形四周是否显示tick
    # ax.tick_params(bottom=True, top=True, left=True, right=True)
    # # 图形四周是否显示tick_label
    # ax.tick_params(labelbottom=True, labeltop=False, labelleft=True, labelright=True)

    # 设置tick的长度和宽度
    for xtl in ax1.get_xticklines():
        xtl.set_markersize(2)  # length
        xtl.set_markeredgewidth(0.57)  # width

    for ytl in ax1.get_yticklines():
        ytl.set_markersize(2)
        ytl.set_markeredgewidth(0.57)

    for tl in ax1.get_yticklabels():
        tl.set_color('firebrick')

    for tl in ax2.get_yticklabels():
        tl.set_color('g')

    for xtl in ax2.get_xticklines():
        xtl.set_markersize(2)  # length
        xtl.set_markeredgewidth(0.57)  # width

    for ytl in ax2.get_yticklines():
        ytl.set_markersize(2)
        ytl.set_markeredgewidth(0.57)

    # legend = ax.legend(loc='lower left', bbox_to_anchor=(0.01, 0.99), ncol=1, frameon=True, fancybox=False,
    #                    facecolor='white', edgecolor='red')  # Add a legend.
    # frame = legend.get_frame()
    # frame.set_linewidth(0.57)  # 设置图例边框线宽
    # frame.set_edgecolor("black")  # 设置图例边框颜色
    # plt.tight_layout()

    frame = legend.get_frame()
    frame.set_linewidth(1)  # 设置图例边框线宽
    frame.set_edgecolor("black")  # 设置图例边框颜色
    ax1.grid()
    plt.tight_layout()
    plt.savefig(
        'E:\OneDrive同步文件夹\OneDrive - 东南大学\研一科研\main_project\Broker_continue\投稿相关\\response相关\\nhefrevise\data_record\Figure\\wrongPath_StreamSize.pdf',
        dpi=600)
    plt.show()

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


def load_data():
    df1 = pandas.read_excel(r'../../新增数据包/自然丢包率/数据统计_lossRate_0.0001_2022_0821_2311.xlsx')
    data1 = np.array(df1)

    df2 = pandas.read_excel(r'../../新增数据包/自然丢包率/数据统计_lossRate_0.0005_2022_0821_2311.xlsx')
    data2 = np.array(df2)

    df3 = pandas.read_excel(r'../../新增数据包/自然丢包率/数据统计_lossRate_0.001_2022_0821_2311.xlsx')
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


def draw_figure():
    # 1pt = 0.35146mm = 0.035146cm
    # 1inch = 2.54cm = 72.27pt
    # 图表坐标轴线条粗细最佳为 0.2mm = [0.57pt]
    # 线条粗细在0.1mm-0.4mm之间 >>> 0.3mm = [0.85pt]
    # 原则上不超过14号字，尽量使用7-12号字，尽量少使用小于6号以下的字体
    # 最多见的文字大小推荐使用7、8、9号字 >> [9pt]
    load_data()
    # 图片大小 单位厘米
    fw = 10 / 2.54
    fh = 8 / 2.54
    x, y_list = draw_figure()
    # 设置全局的字体
    mpl.rcParams['font.family'] = 'serif'
    mpl.rcParams['font.serif'] = 'Times New Roman'
    mpl.rcParams['font.style'] = 'normal'
    mpl.rcParams['font.variant'] = 'normal'
    mpl.rcParams['font.weight'] = 'normal'
    mpl.rcParams['font.stretch'] = 'normal'
    mpl.rcParams['font.size'] = 9

    # 第一种方式设置字体
    font0 = {'fontfamily': 'serif',
             'fontname': 'Times New Roman',
             'fontstyle': 'normal',
             'fontvariant': 'normal',
             'fontweight': 'normal',
             'fontstretch': 'normal',
             'fontsize': 9}

    # 第二种方式设置字体
    tick_font = fm.FontProperties(family='Times New Roman', style='normal', variant='normal', weight='normal',
                                  stretch='normal', size=9)
    # x = np.linspace(0, 2, 100)

    # 1pt = 0.35146mm = 0.035146cm
    # 1inch = 2.54cm = 72.27pt

    # plt.rcParams['xtick.direction'] = 'in'
    # plt.rcParams['ytick.direction'] = 'in'
    fig = plt.figure(figsize=(fw, fh))
    # figsize=(8/2.54,6/2.54),dpi=72
    ax = fig.add_subplot(111)  # Create a figure and an axes.

    ax.plot(x_array1, y_Jaccard1, label='Jaccard:0.0001', linewidth=0.85)  # Plot some data on the axes.
    ax.plot(x_array1, y_Jaccard2, label='Jaccard:0.0005', linewidth=0.85)  # Plot more data on the axes...
    ax.plot(x_array1, y_Jaccard3, label='Jaccard:0.001', linewidth=0.85)  # ... and some more.

    # 图形四周是否显示tick
    ax.tick_params(bottom=True, top=True, left=True, right=True)
    # 图形四周是否显示tick_label
    ax.tick_params(labelbottom=True, labeltop=False, labelleft=True, labelright=False)

    # ax.tick_params(which='both', width=2)
    # ax.tick_params(which='major', length=7)
    # ax.tick_params(which='minor', length=4, color='r')

    # axis --> 坐标轴
    # which --> 主要和次要tick ”both" "major" minor"
    ax.tick_params(axis="both", which='both', direction="in")  # length=16, width=2, color="turquoise"
    ax.tick_params(axis="both", which='both', direction="in")

    ax.xaxis.set_major_locator(MultipleLocator(base=0.5))
    # ax.xaxis.set_minor_locator(MultipleLocator(base=0.1))
    # ax.xaxis.set_minor_locator(AutoMinorLocator(n=5))

    ax.yaxis.set_major_locator(MultipleLocator(base=1))
    # ax.yaxis.set_minor_locator(AutoMinorLocator(n=2))

    # 设置tick的长度和宽度
    for xtl in ax.get_xticklines():
        xtl.set_markersize(2)  # length
        xtl.set_markeredgewidth(0.57)  # width

    for ytl in ax.get_yticklines():
        ytl.set_markersize(2)
        ytl.set_markeredgewidth(0.57)

    # 设置tick_label字体
    for xtlabel in ax.get_xticklabels():
        xtlabel.set_fontproperties(tick_font)

    for ytlabel in ax.get_yticklabels():
        ytlabel.set_fontproperties(tick_font)

    # ax.set_xticks(np.linspace(0,2,5),minor=False)
    # ax.set_xticks(np.linspace(0,2,21),minor=True)

    # ax.set_yticks(np.linspace(0,9,10),minor=False)
    # ax.set_yticks(np.linspace(0,9,19),minor=True)

    # ax.minorticks_off()

    # tick_label 为公式
    # ticks = [-np.pi/2,np.pi/2.]
    # labels = [r"$-\frac{\pi}{2}$",r"$\frac{\pi}{2}$"]
    # ax.xaxis.set_minor_locator(ticker.FixedLocator(ticks))
    # ax.xaxis.set_minor_formatter(ticker.FixedFormatter(labels))

    # 设置图形变宽线宽度和颜色
    bwith = 0.57
    ax.spines['left'].set_color((0, 0, 0, 1))
    ax.spines['left'].set_linewidth(bwith)
    ax.spines['right'].set_color((0, 0, 0, 1))
    ax.spines['right'].set_linewidth(bwith)
    ax.spines['top'].set_color((0, 0, 0, 1))
    ax.spines['top'].set_linewidth(bwith)
    ax.spines['bottom'].set_color((0, 0, 0, 1))
    ax.spines['bottom'].set_linewidth(bwith)

    # ax.spines['left'].set_color('black')
    # ax.spines['bottom'].set_linewidth(bwith)

    # 设置图形坐标轴标签和标题字体
    ax.set_xlabel('Maciliousness', fontdict=font0)  # Add an x-label to the axes.
    ax.set_ylabel('Jaccard', fontdict=font0)  # Add a y-label to the axes.
    # ax.set_title("Simple Plot", fontdict=font0)  # Add a title to the axes.

    legend = ax.legend(loc='upper left', bbox_to_anchor=(0.01, 0.99), ncol=1, frameon=True, fancybox=False,
                       facecolor='white', edgecolor='red')  # Add a legend.
    frame = legend.get_frame()
    frame.set_linewidth(0.57)  # 设置图例边框线宽
    frame.set_edgecolor("black")  # 设置图例边框颜色
    plt.tight_layout()
    plt.savefig('data_record/Figure/test.tiff', dpi=600)
    plt.show()


if __name__ == '__main__':
    # draw_figure()
    config = {
        "font.family": 'serif',
        "font.size": 20,
        "mathtext.fontset": 'stix',
        "font.serif": ['Times New Roman']  # ['SimSun'],
    }  # mac字体不一样   Songti SC  windows Simsun
    rcParams.update(config)

    df1 = pandas.read_excel(r'../../新增数据包/流中包的数量/数据统计_streamSize_5_2022_0821_2232.xlsx')
    data1 = np.array(df1)

    df2 = pandas.read_excel(r'../../新增数据包/流中包的数量/数据统计_streamSize_10_2022_0821_2312.xlsx')
    data2 = np.array(df2)

    df3 = pandas.read_excel(r'../../新增数据包/流中包的数量/数据统计_streamSize_20_2022_0821_2347.xlsx')
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
             markeredgecolor='firebrick', label='StreamSize:5')
    plt.plot(x_array2, y_Jaccard2, 's', linewidth=1.5, color="firebrick", linestyle="-", markerfacecolor='white',
             markersize=5,
             markeredgecolor='firebrick', label='StreamSize:10')
    plt.plot(x_array3, y_Jaccard3, '^', linewidth=1.5, color="firebrick", linestyle="-", markerfacecolor='white',
             markersize=5,
             markeredgecolor='firebrick', label='StreamSize:20')
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
             markeredgecolor='g', label='StreamSize:5')
    plt.plot(x_array2, y_RandIndex2, 's', linewidth=1.2, color="g", linestyle="--", markerfacecolor='white',
             markersize=5,
             markeredgecolor='g', label='StreamSize:10')
    plt.plot(x_array3, y_RandIndex3, '^', linewidth=1.2, color="g", linestyle="--", markerfacecolor='white',
             markersize=5,
             markeredgecolor='g', label='StreamSize:20')
    # plt.legend(loc=[0.7,0.05])
    plt.ylim(0, 1.0)
    # plt.ylabel('Rand Index')
    # ax1.set_xlabel("X1", color=c1, fontsize=fontsize)
    ax1.set_ylabel("Jaccard", color="firebrick", fontsize=20)
    # ax2.set_xlabel('X2', color=c2, fontsize=fontsize)
    ax2.set_ylabel('Rand Index', color="g", fontsize=20)
    # ax2.set_xlabel('attributes', fontsize=15)
    # ax2.set_ylabel('ratio', fontsize=15)
    # plt.legend(loc='lower right')
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
        'E:\OneDrive同步文件夹\OneDrive - 东南大学\研一科研\main_project\Broker_continue\投稿相关\\response相关\\nhefrevise\data_record\Figure\\new_add_StreamSize.pdf',
        dpi=600)

    plt.show()

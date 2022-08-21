# 读取excel数据进行绘图
import numpy as np
import pandas
from matplotlib import rcParams, pyplot as plt

config = {
    "font.family": 'serif',
    "font.size": 20,
    "mathtext.fontset": 'stix',
    "font.serif": ['Times New Roman']  # ['SimSun'],
}  # mac字体不一样   Songti SC  windows Simsun
rcParams.update(config)

df1 = pandas.read_excel(r'../../新增数据包/自然丢包率/数据统计_lossRate_0.0001_2022_0821_2311.xlsx')
data1 = np.array(df1)

df2 = pandas.read_excel(r'../../新增数据包/自然丢包率/数据统计_lossRate_0.0005_2022_0821_2311.xlsx')
data2 = np.array(df2)

df3 = pandas.read_excel(r'../../新增数据包/自然丢包率/数据统计_lossRate_0.001_2022_0821_2311.xlsx')
data3 = np.array(df3)

x_array1 = data1[:, 0][0:12]
y_Jaccard1 = data1[:, 6][0:12]
y_RandIndex1 = data1[:,8][0:12]

x_array2 = data2[:, 0][0:12]
y_Jaccard2 = data2[:, 6][0:12]
y_RandIndex2 = data2[:,8][0:12]

x_array3 = data3[:, 0][0:12]
y_Jaccard3 = data3[:, 6][0:12]
y_RandIndex3 = data3[:,8][0:12]

fig,ax1 = plt.subplots()

ax1.spines['left'].set_visible(False) #去掉左边框
ax1.spines['right'].set_visible(False) #去掉右边框
# ax.spines['top'].set_visible(False)

ax1.tick_params("y",colors='r')
# ax1.tick_params("x",colors='k')
plt.rcParams['font.sans-serif'] = 'SimSun'
plt.plot(x_array1, y_Jaccard1, 'o', linewidth=1.2, color="r", linestyle="-", markerfacecolor='white', markersize=4,
         markeredgecolor='r', label='0.0001')
plt.plot(x_array2, y_Jaccard2, 's', linewidth=1.2, color="r", linestyle="-", markerfacecolor='white', markersize=4,
         markeredgecolor='r', label='0.0005')
plt.plot(x_array3, y_Jaccard3, '^', linewidth=1.2, color="r", linestyle="-", markerfacecolor='white', markersize=4,
         markeredgecolor='r', label='0.001')
plt.legend(loc='lower right')
plt.ylim(0,1.0)
plt.ylabel('Jaccard')
plt.xlabel('Maliciousness')

ax2 = ax1.twinx()
ax2.spines['left'].set_visible(False) #去掉左边框
ax2.spines['right'].set_visible(False) #去掉右边框
ax2.tick_params(colors='b')
plt.plot(x_array1, y_RandIndex1, 'o', linewidth=1.2, color="b", linestyle="--",markerfacecolor='white', markersize=4,
         markeredgecolor='b', label='0.0001')
plt.plot(x_array2, y_RandIndex2, 's', linewidth=1.2, color="b", linestyle="--", markerfacecolor='white', markersize=4,
         markeredgecolor='b', label='0.0005')
plt.plot(x_array3, y_RandIndex3, '^', linewidth=1.2, color="b", linestyle="--", markerfacecolor='white', markersize=4,
         markeredgecolor='b', label='0.001')
plt.legend(loc='center right')
plt.ylim(0,1.0)
plt.ylabel('Rand Index')
ax = plt.gca()
ax.spines['left'].set_visible(True) #去掉左边框
ax.spines['right'].set_visible(True) #去掉右边框
ax.spines['left'].set_color('red')
ax.spines['right'].set_color('blue')
plt.grid()
plt.show()

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib as mpl
import matplotlib.ticker as mtick  
#from brokenaxes import brokenaxes
from matplotlib import gridspec
from matplotlib.pyplot import MultipleLocator

fig = plt.figure(figsize=(12, 6))

gs = gridspec.GridSpec(1, 2, width_ratios=[6, 1]) 
# 建立子图
ax1 = fig.add_subplot(gs[0])   # 2*1
#ax2 = fig.add_subplot(gs[1])
# 第一个图为
plt.rcParams.update({'font.size': 28})

df1 = pd.read_csv('scheduler_scalability.csv')
x = list(df1['node'])

y1 = list(df1['mem_usage'])
bar_width = 0.25
tick_label = ["10","25","50","100","200"]
plt.plot(x,y1,color='#74a9cf',linewidth=6,label='Overhead',marker='o', ms=12)
plt.xticks([10,25,50,100,200],tick_label)
plt.yticks(fontsize=28)
ax1.set_xticklabels(tick_label, fontsize=28)
ax1.set_ylim(22.5, 37.5)
ax1.set_ylabel("Memory usage (MB)", fontsize=34)
ax1.set_xlabel('Function Nodes in Benchmark Genome', fontsize=34)
ax1.axhline(y=25, xmin=0.0, xmax=1, color='tab:grey', linestyle='--')
ax1.axhline(y=27.5, xmin=0.0, xmax=1, color='tab:grey', linestyle='--')
ax1.axhline(y=30, xmin=0.0, xmax=1, color='tab:grey', linestyle='--')
ax1.axhline(y=32.5, xmin=0.0, xmax=1, color='tab:grey', linestyle='--')
ax1.axhline(y=35, xmin=0.0, xmax=1, color='tab:grey', linestyle='--')


# 设置子图之间的间距，默认值为1.08
plt.tight_layout(pad=0)  
fig.savefig("scalability_mem.pdf", bbox_inches='tight')
plt.show()

fig = plt.figure(figsize=(12, 6))

gs = gridspec.GridSpec(1, 2, width_ratios=[6, 1]) 
# 建立子图
ax1 = fig.add_subplot(gs[0])   # 2*1
#ax2 = fig.add_subplot(gs[1])
# 第一个图为
plt.rcParams.update({'font.size': 28})
x = list(df1['node'])

y1 = list(df1['core x second'])
bar_width = 0.25
tick_label = ["10","25","50","100","200"]
plt.plot(x,y1,color='#9bbb59',linewidth=6,label='Overhead',marker='o', ms=12)
plt.xticks([10,25,50,100,200],tick_label)
ax1.set_ylim(0, 1)
ax1.set_ylabel("Cores × Seconds", fontsize=34)
ax1.set_xlabel('Function Nodes in Benchmark Genome', fontsize=34)

ax1.axhline(y=0.2, xmin=0.0, xmax=1, color='tab:grey', linestyle='--')
ax1.axhline(y=0.4, xmin=0.0, xmax=1, color='tab:grey', linestyle='--')
ax1.axhline(y=0.6, xmin=0.0, xmax=1, color='tab:grey', linestyle='--')
ax1.axhline(y=0.8, xmin=0.0, xmax=1, color='tab:grey', linestyle='--')


# 设置子图之间的间距，默认值为1.08
plt.tight_layout(pad=0)  
fig.savefig("scalability_cpu.pdf", bbox_inches='tight')
plt.show()
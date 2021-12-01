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

fig = plt.figure(figsize=(19, 7))

gs = gridspec.GridSpec(1, 2, width_ratios=[6, 1]) 
# 建立子图
ax1 = fig.add_subplot(gs[0])   # 2*1
# 第一个图为
plt.rcParams.update({'font.size': 28})
x = np.arange(8)

bar_width = 0.26
tick_label = ["Cyc","Epi","Gen","Soy","Vid","IR","FP","WC"]

df1 = pd.read_csv('optimized_corun.csv')
df2 = pd.read_csv('optimized_single.csv')
df3 = pd.read_csv('raw_corun.csv')
df4 = pd.read_csv('raw_single.csv')
y_1 = list(df4['e2e_latency']) # Hyper-flow single
y_2 = list(df3['e2e_latency']) # Hyper-flow co-run
y_3 = list(df2['e2e_latency']) # FaaSFlow single
y_4 = list(df1['e2e_latency']) # FaaSFlow co-run
for i in range(len(y_2)):
    if y_2[i] == 'timeout':
        y_2[i] = 60
    else:
        y_2[i] = float(y_2[i])

yy_1 = []
yy_2 = []
for i in range (0,8):
    yy_1.append(y_4[i]/y_3[i])
for i in range (0,8):
    yy_2.append(y_2[i]/y_1[i])



#ax1.bar(x-1.5*bar_width, y_1, bar_width, color="#76180E", align="center", label="HyperFlow-serverless solo-run",edgecolor='black',linewidth=2)
#ax1.bar(x-0.5*bar_width, y_2, bar_width, color="#C46025", align="center", label="HyperFlow-serverless co-run",edgecolor='black',linewidth=2)
#ax1.bar(x+0.5*bar_width, y_3, bar_width, color="#F0AC48", align="center", label="FaaSFlow-FaaStore solo-run",edgecolor='black',linewidth=2)
#ax1.bar(x+1.5*bar_width, y_4, bar_width, color="#FFFED5", align="center", label="FaaSFlow-FaaStore co-run",edgecolor='black',linewidth=2)

#ax1.bar(x-1.5*bar_width, y_1, bar_width, color="#76180E", align="center", label="HyperFlow-serverless solo-run",edgecolor='black',linewidth=2)
ax1.bar(x-0.5*bar_width, y_2, bar_width, color="#76180E", align="center", label="HyperFlow-serverless co-run",edgecolor='black',linewidth=2)
#ax1.bar(x+0.5*bar_width, y_3, bar_width, color="#F0AC48", align="center", label="FaaSFlow-FaaStore solo-run",edgecolor='black',linewidth=2)
ax1.bar(x+0.5*bar_width, y_4, bar_width, color="#C46025", align="center", label="FaaSFlow-FaaStore co-run",edgecolor='black',linewidth=2)
#F7903D#59A95A#4D85BD

ax1.set_ylim(0,32)
ax1.tick_params(labelsize=30)
ax1.set_xticklabels(tick_label, fontsize=28)
ax1.set_ylabel('The End-to-end Latencies\n Interference when co-running', fontsize=32)


plt.xticks(x, tick_label,rotation=0)
ax1.axhline(y=4, color='tab:grey', linestyle='--')
ax1.axhline(y=8, color='tab:grey', linestyle='--')
ax1.axhline(y=12, color='tab:grey', linestyle='--')
ax1.axhline(y=16, color='tab:grey', linestyle='--')
ax1.axhline(y=20, color='tab:grey', linestyle='--')
ax1.axhline(y=24, color='tab:grey', linestyle='--')
ax1.axhline(y=28, color='tab:grey', linestyle='--')
ax1.legend(ncol=1,loc='upper left',fontsize=24,handlelength=1.7)



ax2 = ax1.twinx()
ax2.plot(x,yy_2, color='#76180E',linewidth=3,label='HyperFlow-serverless degradation',marker='o', ms=12)
ax2.plot(x,yy_1, color='#C46025',linewidth=3,label='FaaSFlow-FaaStore degradation',marker='o', ms=12)
ax2.set_ylim(0,2)
ax2.legend(ncol=1,loc='upper right',fontsize=24,handlelength=1.7)
ax2.set_ylabel('The end-to-end degradation\n normalized to solo-run', fontsize=32)


y2_major_locator=MultipleLocator(0.5)
#把y轴的刻度间隔设置为10，并存在变量里
ax2.yaxis.set_major_locator(y2_major_locator)

y1_major_locator=MultipleLocator(4)
#把y轴的刻度间隔设置为10，并存在变量里
ax1.yaxis.set_major_locator(y1_major_locator)


# 设置子图之间的间距，默认值为1.08
plt.tight_layout(pad=0)  
fig.savefig("co-location.pdf", bbox_inches='tight')
plt.show()

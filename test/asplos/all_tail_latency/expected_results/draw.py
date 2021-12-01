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

fig = plt.figure(figsize=(20, 6))

gs = gridspec.GridSpec(1, 2, width_ratios=[6, 1]) 
# 建立子图
ax1 = fig.add_subplot(gs[0])   # 2*1
# 第一个图为
plt.rcParams.update({'font.size': 30})
x = np.arange(8)

bar_width = 0.23
tick_label = ["Cyc","Epi","Gen","Soy","Vid","IR","FP","WC"]

df1 = pd.read_csv('optimized_6rpm_50MB.csv')
df2 = pd.read_csv('raw_6rpm_50MB.csv')
y_1 = list(df1['tail_latency']) # FaaSFlow single
y_2 = list(df2['tail_latency']) # FaaSFlow co-run
for i in range(len(y_2)):
    if y_2[i] == 'timeout':
        y_2[i] = 60
    else:
        y_2[i] = float(y_2[i])

#ax1.bar(x-1.5*bar_width, y_1, bar_width, color="#76180E", align="center", label="HyperFlow-serverless solo-run",edgecolor='black',linewidth=2)
ax1.bar(x-0.5*bar_width, y_2, bar_width, color="#74a9cf", align="center", label="HyperFlow-serverless",edgecolor='black',linewidth=2)
ax1.bar(x+0.5*bar_width, y_1, bar_width, color="#9bbb59", align="center", label="FaaSFlow-FaaStore",edgecolor='black',linewidth=2)
#ax1.bar(x+1.5*bar_width, y_4, bar_width, color="#FFFED5", align="center", label="FaaSFlow-FaaStore co-run",edgecolor='black',linewidth=2)
#F7903D#59A95A#4D85BD

ax1.set_ylim(0,70)
ax1.tick_params(labelsize=32)
ax1.set_xticklabels(tick_label, fontsize=32)
ax1.set_ylabel('The 99%-ile latency', fontsize=36)
# plt.yticks([0, 1, 2,3,4], ["0.1","1" , "10", "100","1000"],fontsize=32)

plt.xticks(x, tick_label,rotation=0)
ax1.axhline(y=20, color='tab:grey', linestyle='--')
ax1.axhline(y=40, color='tab:grey', linestyle='--')
ax1.axhline(y=60, color='tab:grey', linestyle='--')
ax1.axhline(y=80, color='tab:grey', linestyle='--')
ax1.legend(ncol=2,loc='upper left',fontsize=34)


# 设置子图之间的间距，默认值为1.08
plt.tight_layout(pad=0)  
fig.savefig("tail_latency.pdf", bbox_inches='tight')
plt.show()
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

fig = plt.figure(figsize=(18, 6))

gs = gridspec.GridSpec(1, 2, width_ratios=[6, 1]) 
# 建立子图
ax1 = fig.add_subplot(gs[0])   # 2*1
# 第一个图为
plt.rcParams.update({'font.size': 30})
x = np.arange(8)

bar_width = 0.23
tick_label = ["Cyc","Epi","Gen","Soy","Vid","IR","FP","WC"]
df1 = pd.read_csv('MasterSP.csv')
df2 = pd.read_csv('WorkerSP.csv')

y_2 = list(df1['schedule_overhead'])
y_3 = list(df2['schedule_overhead'])
for index in range(len(y_2)):
    y_2[index] = np.log10(y_2[index])+3
for index in range(len(y_3)):
    y_3[index] = np.log10(y_3[index])+3

#ax1.bar(x-1.5*bar_width, y_1, bar_width, color="#76180E", align="center", label="HyperFlow-serverless solo-run",edgecolor='black',linewidth=2)
ax1.bar(x-0.5*bar_width, y_2, bar_width, color="#74a9cf", align="center", label="MasterSP (HyperFlow-serverless)",edgecolor='black',linewidth=2)
ax1.bar(x+0.5*bar_width, y_3, bar_width, color="#9bbb59", align="center", label="WorkerSP (FaaSFlow)",edgecolor='black',linewidth=2)
#ax1.bar(x+1.5*bar_width, y_4, bar_width, color="#FFFED5", align="center", label="FaaSFlow-FaaStore co-run",edgecolor='black',linewidth=2)
#F7903D#59A95A#4D85BD

ax1.set_ylim(0,4.4)
ax1.tick_params(labelsize=32)
ax1.set_xticklabels(tick_label, fontsize=32)
ax1.set_ylabel('The scheduling overhead\n in the e2e latency(s) ', fontsize=32)
plt.yticks([0, 1, 2,3,4], ["0.001","0.01" , "0.1", "1","10"],fontsize=32)

plt.xticks(x, tick_label,rotation=0)
ax1.axhline(y=1, color='tab:grey', linestyle='--')
ax1.axhline(y=2, color='tab:grey', linestyle='--')
ax1.axhline(y=3, color='tab:grey', linestyle='--')
ax1.axhline(y=4, color='tab:grey', linestyle='--')
ax1.legend(ncol=1,loc='upper right',fontsize=26)


# 设置子图之间的间距，默认值为1.08
plt.tight_layout(pad=0)  
fig.savefig("schedule_overhead.pdf", bbox_inches='tight')
plt.show()
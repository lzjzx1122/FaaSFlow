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

RPMs = {'gen-25': ['2/min', '4/min', '6/min', '8/min'], 'gen-50':['2/min', '4/min', '6/min', '8/min', '10/min'], 
'gen-75': ['2/min', '4/min', '6/min', '8/min', '10/min'], 'gen-100': ['2/min', '4/min', '6/min', '8/min', '10/min'],
'vid-25': ['4/min', '8/min', '16/min', '24/min'], 'vid-50': ['8/min', '16/min', '24/min', '32/min', '40/min'], 
'vid-75': ['8/min', '16/min', '24/min', '32/min', '40/min'], 'vid-100': ['8/min', '16/min', '24/min', '32/min', '40/min']}

def draw(file_name, y_master, y_worker):

    for i in range(len(y_master)):
        if y_master[i] == 'timeout':
            y_master[i] = 60
        else:
            y_master[i] = float(y_master[i])

    for i in range(len(y_worker)):
        if y_worker[i] == 'timeout':
            y_worker[i] = 60
        else:
            y_worker[i] = float(y_worker[i])

    y_master = np.array(y_master)
    y_worker = np.array(y_worker)

    fig = plt.figure(figsize=(12, 6))
    tick_label = RPMs[file_name]

    gs = gridspec.GridSpec(1, 2, width_ratios=[6, 1]) 
    # 建立子图
    ax1 = fig.add_subplot(gs[0])   # 2*1
    # 第一个图为
    plt.rcParams.update({'font.size': 24})
    x = np.arange(len(y_master))

    bar_width = 0.24

    #ax1.bar(x-1.5*bar_width, y_1, bar_width, color="#76180E", align="center", label="HyperFlow-serverless solo-run",edgecolor='black',linewidth=2)
    ax1.bar(x-0.5*bar_width, y_master, bar_width, color="#74a9cf", align="center", label="HyperFlow-serverless",edgecolor='black',linewidth=2)
    ax1.bar(x+0.5*bar_width, y_worker, bar_width, color="#9bbb59", align="center", label="FaaSFlow-FaaStore",edgecolor='black',linewidth=2)
    #ax1.bar(x+1.5*bar_width, y_4, bar_width, color="#FFFED5", align="center", label="FaaSFlow-FaaStore co-run",edgecolor='black',linewidth=2)
    #F7903D#59A95A#4D85BD

    ax1.set_ylim(0,65)
    ax1.tick_params(labelsize=27)
    ax1.set_xticklabels(tick_label, fontsize=28)
    # ax1.set_ylabel('The 99%-ile latency ', fontsize=32)


    plt.xticks(x, tick_label,rotation=0)
    ax1.axhline(y=20, color='tab:grey', linestyle='--')
    ax1.axhline(y=40, color='tab:grey', linestyle='--')
    ax1.axhline(y=60, color='tab:grey', linestyle='--')
    ax1.axhline(y=80, color='tab:grey', linestyle='--')
    ax1.legend(ncol=1,loc='upper left',fontsize=30)


    # 设置子图之间的间距，默认值为1.08
    plt.tight_layout(pad=0)  
    fig.savefig(f"{file_name}MB.pdf", bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    df1 = pd.read_csv('raw_genome_25MB.csv')
    df2 = pd.read_csv('optimized_genome_25MB.csv')
    draw('gen-25', list(df1['tail_latency']), list(df2['tail_latency']))

    df1 = pd.read_csv('raw_genome_50MB.csv')
    df2 = pd.read_csv('optimized_genome_50MB.csv')
    draw('gen-50', list(df1['tail_latency']), list(df2['tail_latency']))

    df1 = pd.read_csv('raw_genome_75MB.csv')
    df2 = pd.read_csv('optimized_genome_75MB.csv')
    draw('gen-75', list(df1['tail_latency']), list(df2['tail_latency']))

    df1 = pd.read_csv('raw_genome_100MB.csv')
    df2 = pd.read_csv('optimized_genome_100MB.csv')
    draw('gen-100', list(df1['tail_latency']), list(df2['tail_latency']))

    df1 = pd.read_csv('raw_video_25MB.csv')
    df2 = pd.read_csv('optimized_video_25MB.csv')
    draw('vid-25', list(df1['tail_latency']), list(df2['tail_latency']))

    df1 = pd.read_csv('raw_video_50MB.csv')
    df2 = pd.read_csv('optimized_video_50MB.csv')
    draw('vid-50', list(df1['tail_latency']), list(df2['tail_latency']))

    df1 = pd.read_csv('raw_video_75MB.csv')
    df2 = pd.read_csv('optimized_video_75MB.csv')
    draw('vid-75', list(df1['tail_latency']), list(df2['tail_latency']))

    df1 = pd.read_csv('raw_video_100MB.csv')
    df2 = pd.read_csv('optimized_video_100MB.csv')
    draw('vid-100', list(df1['tail_latency']), list(df2['tail_latency']))
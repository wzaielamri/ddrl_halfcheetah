import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

"""
    Visualizes the learning performances over time, taken from the rllib logs.
    The measure calculates the running mean over all training epochs of returns.
    Taken from Andrychowicz et al. (2020): What Matters In On-Policy Reinforcement Learning? A Large-Scale Empirical Study.
    Google Brain Research: "We then average these score to obtain a single performance score of the seed which is proportional to the area under the learning curve. This ensures we assign higher scores to agents that learn quickly. The performance score of a hyperparameter configuration is finally set to the median performance score across the 3 seeds."
    
    Here, run on the system trained on flat terrain.
"""

# These are the "Tableau 20" colors as RGB.    
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)] 
# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.    
for i in range(len(tableau20)):    
    r, g, b = tableau20[i]    
    tableau20[i] = (r / 255., g / 255., b / 255.) 
    
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams['axes.edgecolor']='#333F4B'
plt.rcParams['axes.linewidth']=0.8
plt.rcParams['xtick.color']='#333F4B'
plt.rcParams['ytick.color']='#333F4B'

# Remove Type 3 fonts for latex
plt.rcParams['pdf.fonttype'] = 42
# matplotlib.rcParams['ps.fonttype'] = 42

# Log file directories
# exp_path = [os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results/1_flat_QuantrupedMultiEnv_Centralized',
#     os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results/1_flat_QuantrupedMultiEnv_Local']
# 
# exp_path = [os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_Freitag/exp1_10_flat_QuantrupedMultiEnv_Centralized', 
#     os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_Freitag/exp1_10_flat_QuantrupedMultiEnv_FullyDecentral', 
#     os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_Freitag/exp1_10_flat_QuantrupedMultiEnv_Local', 
#     os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_Freitag/exp1_10_flat_QuantrupedMultiEnv_SingleDiagonal', 
#     os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_Freitag/exp1_10_flat_QuantrupedMultiEnv_SingleNeighbor', 
#     os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_Freitag/exp1_10_flat_QuantrupedMultiEnv_TwoDiags'] 
# #    os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_Freitag/exp1_10_flat_QuantrupedMultiEnv_TwoSides']

exp_path = [os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_hf/exp_hf_06_QuantrupedMultiEnv_Centralized',
    os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_11_02/exp1_20_flat_QuantrupedMultiEnv_Centralized',
    os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_hf/exp_hf_06_QuantrupedMultiEnv_FullyDecentral',
    os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_11_02/exp1_20_flat_QuantrupedMultiEnv_FullyDecentral',
    os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_hf/exp_hf_06_QuantrupedMultiEnv_Local',
    os.getenv("HOME") + '/Desktop/gpu_cluster/ray_results_11_02/exp1_20_flat_QuantrupedMultiEnv_Local']
        
experiment_dirs = [[os.path.join(exp_path_item,dI) for dI in os.listdir(exp_path_item) if os.path.isdir(os.path.join(exp_path_item,dI))] for exp_path_item in exp_path]

all_exp_data = []
for exp_dir in experiment_dirs:
    for i in range(0, len(exp_dir)):
        df = pd.read_csv(exp_dir[i]+'/progress.csv')
        rew_new =(df.iloc[:,2].values)
        mean_cum_rew_new = np.cumsum(rew_new)/np.arange(1,rew_new.shape[0]+1)
        if i==0:
            mean_cum_rew = np.vstack([mean_cum_rew_new])
            time_steps = (df.iloc[:,6].values)
        else:
            mean_cum_rew = np.vstack([mean_cum_rew,mean_cum_rew_new])
    mc_rew_mean = np.mean(mean_cum_rew, axis=0)
    mc_rew_std = np.std(mean_cum_rew, axis=0)
    mc_rew_lower_std = mc_rew_mean - mc_rew_std
    mc_rew_upper_std = mc_rew_mean + mc_rew_std
    all_exp_data.append( [mc_rew_mean, mc_rew_std, mc_rew_lower_std, mc_rew_upper_std] )
    print("Loaded ", exp_dir)

# Plotting functions
fig = plt.figure(figsize=(12, 8))
# Remove the plot frame lines. They are unnecessary chartjunk.  
ax_arch = plt.subplot(111)  
ax_arch.spines["top"].set_visible(False)  
ax_arch.spines["right"].set_visible(False) 

#ax_arch.set_yscale('log')
ax_arch.set_xlim(0, 2e7)
#ax_arch.set_ylim(0, 800)  

for i in range(0, len(all_exp_data)):
    # Use matplotlib's fill_between() call to create error bars.   
    plt.fill_between(time_steps, all_exp_data[i][2],  
                     all_exp_data[i][3], color=tableau20[i*2 + 1], alpha=0.25)  
    plt.plot(time_steps, all_exp_data[i][0], color=tableau20[i*2], lw=1, label=exp_path[i].split('_')[-1])
    #print("Mean reward for ", i, ": ", all_exp_data[i][0][-1], " - at iter 625: ", all_exp_data[i][0][624])
    print(exp_path[i].split('_')[-1], f' && {all_exp_data[i][0][311]:.2f} & ({all_exp_data[i][1][311]:.2f}) && {all_exp_data[i][0][624]:.2f} & ({all_exp_data[i][1][624]:.2f}) && {all_exp_data[i][0][1249]:.2f} & ({all_exp_data[i][1][1249]:.2f})')
ax_arch.set_xlabel('timesteps', fontsize=14)
ax_arch.set_ylabel('Learning Performance \n Mean Return per Episode', fontsize=14)
plt.legend(loc="lower right")
#plt.plot([0,500], [200,200], color=tableau20[6], linestyle='--')

plt.show()
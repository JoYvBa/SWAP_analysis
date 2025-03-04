# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 14:59:39 2025

@author: Jorrit Bakker
"""

import tools as tools
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#%%
# Relative file path to the excel file with the data
file_path = "./S9081 HMVT CR1000X_measurements.dat"

# The correction factor with regards to 3M KCl electrode reference
correction = 200

# Load in the file as Excel and clean it up into a seperate dataframe for temperature and redox data
df_redox, df_temp = tools.cleanup_redox(file_path,
                                        correction = correction,
                                        rename = tools.CW_rename
                                        )

#%%
# The nodes you want to plot for the redox plot using node_dictionary
redox_nodes = tools.node_dictionary["CW2_80cm"]
# Or alternatively by manually choosing the redox nodes
#redox_nodes = ["CW3S1-4", "CW3S2-4", "CW3S3-4", "CW3S4-4"]

# The nodes you want to plot for the temperature plot
temp_nodes  = ['CW1S1', 'CW1S2', 'CW1S3', 'CW1S4', 'CW2S1', 'CW2S2', 'CW2S3', 'CW2S4', 'CW3S1', 'CW3S2', 'CW3S3']
# The start and end date of the data you want to plot, as 'YYYY-MM-DD hh-mm-ss'. Hour, minute and second specification is optional
start_date, end_date  = '2024-09-01', '2025-03-04'

# Plots the redox data
fig, ax = tools.plot_redox(df_redox,
                 redox_nodes,
                 start_date,
                 end_date,
                 ylimit = (-300, -200),
                 )
fig.legend(bbox_to_anchor = (0.985, 0.97))
plt.show()

# Plots the temperature data
fig, ax = tools.plot_temp(df_temp,
                 temp_nodes,
                 start_date,
                 end_date,
                 )
fig.legend(bbox_to_anchor = (0.985, 0.97))
plt.show() 

#%%
# Alternatively, plot temperature and redox in the same figure:
fig, ax1 = tools.plot_redox(df_redox,
                 redox_nodes,
                 start_date,
                 end_date,
                 ylimit = (-300, -200)
                 )

# Twinning the x-axis to allow for second y-axis.
ax2 = ax1.twinx()

# Pass the twinned axes object to the plot_temperature function to plot it on the second y-axis.
ax2 = tools.plot_temp(df_temp,
                 temp_nodes,
                 start_date,
                 end_date,
                 mean = True,
                 ax = ax2,
                 color = "black",
                 alpha = 0.8,
                 )
fig.legend(bbox_to_anchor = (0.985, 0.97))
plt.show()

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 14:45:13 2025

@author: Jorrit Bakker
"""

import pandas as pd
pd.options.mode.chained_assignment = None
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def cleanup_redox(file_path : str,
                  correction : float = 200,
                  rename : dict = None,
                  ):
    """ Takes an Excel sheet of SWAP sensor data and seperates it into two 
    dataframes for redox and temperature that can be used for data analysis.

    Parameters
    ----------
    file_path : str
        Path to excel or csv file containing redox data.
    correction : float, optional
        The correction factor with regards to 3M KCl electrode reference for the redox data. Default is 200
    rename : dictionary, optional
        Dictionary for renaming the SWAP nodes. With initial name as key and new name as value. Default is none.

    Returns
    -------
    df_redox : pd.Dataframe
        A cleaned up dataframe containing the redox data from the input Excel sheet.
    df_temp : pd.Dataframe
        A cleaned up dataframe containing the soil temperature data from the input Excel sheet.
    """
    
    if file_path.endswith("xlsx") or file_path.endswith("xls"):
        dataframe = pd.read_excel(file_path, sheet_name = 0)
    else:
        try:
            dataframe = pd.read_csv(file_path, skiprows = [0], header = None)
        except:
            IOError("File type is not of the expected type or recognized. File should be a csv or Excel")
    
    drop_cols = ['batt_volt_Avg', 'RECORD', 'TIMESTAMP']
    
    header = dataframe[dataframe.iloc[:,0] == "TIMESTAMP"].index[0]
    dataframe.columns = dataframe.iloc[header]
    start_data = dataframe[dataframe.loc[:,"RECORD"] == "0"].index[0]
    dataframe = dataframe.drop(range(0,start_data))
    
    # Time column is set to datatime datatype and moved to first column of dataframe for ease of reading.
    dataframe['Time'] = pd.to_datetime(dataframe['TIMESTAMP'])
    move_col = dataframe.pop("Time")
    dataframe.insert(0, "Time", move_col)
    dataframe = dataframe.drop(drop_cols, axis = 1)
    
    # Split dataframe into redox and temperature by selecting on the beginning of the column names.
    df_redox = dataframe.filter(regex='^redox')
    df_redox = pd.concat([dataframe['Time'], df_redox], axis = 1)
    df_temp = dataframe.filter(regex='^temp')
    df_temp = pd.concat([dataframe['Time'], df_temp], axis = 1)
    
    # Column names are changed to more concise names for ease of understanding.
    if rename:
        df_redox.rename(columns = rename, inplace = True)
        df_temp.rename(columns = rename, inplace = True)
    
    # For analysis, datatype has to be set to floats
    df_redox.loc[:, df_redox.columns != 'Time'] = df_redox.loc[:, df_redox.columns != 'Time'].apply(pd.to_numeric, errors='coerce') + correction
    df_temp.loc[:, df_temp.columns != 'Time'] = df_temp.loc[:, df_temp.columns != 'Time']. apply(pd.to_numeric, errors='coerce')
    
    df_redox = df_redox.set_index("Time")
    df_redox = df_redox.apply(pd.to_numeric, errors='coerce')
    df_temp = df_temp.set_index("Time")
    df_temp = df_temp.apply(pd.to_numeric, errors='coerce')
    
    date_range_redox = pd.date_range(df_redox.index[0], df_redox.index[-1], freq = "h")
    date_range_temp = pd.date_range(df_temp.index[0], df_temp.index[-1], freq = "h")
    
    df_redox = df_redox.reindex(date_range_redox, fill_value=np.nan)
    df_temp = df_temp.reindex(date_range_temp, fill_value=np.nan)

    return(df_redox, df_temp)

def plot_redox(df_redox : pd.DataFrame(),
               redox_nodes : list,
               start_date : str,
               end_date : str,
               ylimit : tuple = None,  
               **kwargs
               ):
    """ Plot redox potential and optionally rainfall data for selected nodes in a timeframe.
    

    Parameters
    ----------
    df_redox : pd.DataFrame
        Dataframe with SWAP redox data
    redox_nodes : List
        List with nodes from the dataframe to be plotted
    start_date : str
        The start date of the data to be plotted, as "YYYY-MM-DD"
    end_date : str
        The end date of the data to be plotted, as "YYYY-MM-DD"
    ylimit_redox : tuple, optional
        Manually set y-axis range for the redox data, as (min_y, max_y). The default is None.
    **kwargs :
        Keyword arguments for plt.plot()

    Returns
    -------
    fig : obj
        Figure object of matplotlib
    ax : obj
        Axes object of matplotlib
    """
    
    mask = (df_redox.index > start_date) & (df_redox.index <= end_date)
    df_redox_plot = df_redox[mask]

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    for i, node in enumerate(redox_nodes):
        ax.plot(df_redox_plot.index, df_redox_plot[node],
                label = node,
                **kwargs)

    ax.set_xlabel("Time")
    ax.set_ylabel("Redox potential [mV]")
    
    if ylimit:
        try:
            ax.set_ylim(ylimit)
        except:
            print("ylimits_redox is not of the correct format and is thus ignored.")
    
    ax.set_xlabel('Date')
    ax.set_ylabel(r'Redox potential [$mV$]')
    
    # Modify axis ticks with the goal to make it more readable.
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    ax.tick_params(axis='x', rotation=0, pad=15)

    ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    ax.tick_params(axis='x', which='minor', length=4, width=1)
    
    fig.tight_layout()
    
    return(fig, ax)

def plot_temp(df_temp : pd.DataFrame(),
              temp_nodes : list,
              start_date : str,
              end_date : str,
              mean : bool = False,
              ylimit : tuple = None,
              ax = None,
              **kwargs
              ):
    """ Plot temperature for a selection of nodes in a specified timeframe.
    

    Parameters
    ----------
    df_temp : pd.DataFrame
        Dataframe with temperature data
    temp_nodes : List
        List with nodes from the dataframe to be plotted
    start_date : str
        The start date of the data to be plotted, as "YYYY-MM-DD"
    end_date : str
        The end date of the data to be plotted, as "YYYY-MM-DD"
    mean : Bool, optional
        When set to True, plots the mean soil temperature of the given nodes. The default is False.
    ylimit : tuple, optional
        Manually set y-axis range for the redox data, as (min_y, max_y). The default is False.
    ax : obj, optional
        Axes object of matplotlib, specify when adding this to a pre-exisiting plot. Default is None.
    **kwargs :
        Keyword arguments for plt.plot()

    Returns
    -------
    fig : obj
        Figure object of matplotlib
    ax : obj
        Axes object of matplotlib

    """
    mask = (df_temp.index > start_date) & (df_temp.index <= end_date)
    df_temp = df_temp[mask]
    if mean:
        mean_temp = df_temp.loc[:,temp_nodes].mean(axis=1)
        df_temp['mean_temperature'] = mean_temp
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    else:
        fig = None
    
    if mean:
            ax.plot(df_temp.index, df_temp["mean_temperature"],
                    label = "Mean temperature",
                    **kwargs
                    )

    else:
        for i, node in enumerate(temp_nodes):
            ax.plot(df_temp.index, df_temp[node],
                    label = node,
                    **kwargs
                    )

    if ylimit:
        try:
            ax.set_ylim(ylimit)
        except:
            print("ylimits is not of the correct format and is thus ignored.")
            
    ax.set_xlabel('Date')
    ax.set_ylabel('Temperature (ºC)')

    # Modify axis ticks to make it more readable.    
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    ax.tick_params(axis='x', rotation=0, pad=15)

    ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
    ax.tick_params(axis='x', which='minor', length=4, width=1)
    
    if fig is None:
        return(ax)
    else:
        fig.tight_layout() 
        return(fig, ax)


# Dictionary which renames each soil node for the Constructed Wetland pilot study
CW_rename = {
    'redox_raw_Avg(1)'  : 'CW1S1-1', 'redox_raw_Avg(2)'   : 'CW1S1-2', 'redox_raw_Avg(3)'   : 'CW1S1-3', 'redox_raw_Avg(4)'   : 'CW1S1-4',
    'redox_raw_Avg(5)'  : 'CW1S2-1', 'redox_raw_Avg(6)'   : 'CW1S2-2', 'redox_raw_Avg(7)'   : 'CW1S2-3', 'redox_raw_Avg(8)'   : 'CW1S2-4',
    'redox_raw_Avg(9)'  : 'CW1S3-1', 'redox_raw_Avg(10)'  : 'CW1S3-2', 'redox_raw_Avg(11)'  : 'CW1S3-3', 'redox_raw_Avg(12)'  : 'CW1S3-4',
    'redox_raw_Avg(13)' : 'CW1S4-1', 'redox_raw_Avg(14)'  : 'CW1S4-2', 'redox_raw_Avg(15)'  : 'CW1S4-3', 'redox_raw_Avg(16)'  : 'CW1S4-4',
    'redox_raw_Avg(17)' : 'CW2S1-1', 'redox_raw_Avg(18)'  : 'CW2S1-2', 'redox_raw_Avg(19)'  : 'CW2S1-3', 'redox_raw_Avg(20)'  : 'CW2S1-4',
    'redox_raw_Avg(21)' : 'CW2S2-1', 'redox_raw_Avg(22)'  : 'CW2S2-2', 'redox_raw_Avg(23)'  : 'CW2S2-3', 'redox_raw_Avg(24)'  : 'CW2S2-4',
    'redox_raw_Avg(25)' : 'CW2S3-1', 'redox_raw_Avg(26)'  : 'CW2S3-2', 'redox_raw_Avg(27)'  : 'CW2S3-3', 'redox_raw_Avg(28)'  : 'CW2S3-4',
    'redox_raw_Avg(29)' : 'CW2S4-1', 'redox_raw_Avg(30)'  : 'CW2S4-2', 'redox_raw_Avg(31)'  : 'CW2S4-3', 'redox_raw_Avg(32)'  : 'CW2S4-4',
    'redox_raw_Avg(33)' : 'CW3S1-1', 'redox_raw_Avg(34)'  : 'CW3S1-2', 'redox_raw_Avg(35)'  : 'CW3S1-3', 'redox_raw_Avg(36)'  : 'CW3S1-4',
    'redox_raw_Avg(37)' : 'CW3S2-1', 'redox_raw_Avg(38)'  : 'CW3S2-2', 'redox_raw_Avg(39)'  : 'CW3S2-3', 'redox_raw_Avg(40)'  : 'CW3S2-4',
    'redox_raw_Avg(41)' : 'CW3S3-1', 'redox_raw_Avg(42)'  : 'CW3S3-2', 'redox_raw_Avg(43)'  : 'CW3S3-3', 'redox_raw_Avg(44)'  : 'CW3S3-4',
    'redox_raw_Avg(45)' : 'CW3S4-1', 'redox_raw_Avg(46)'  : 'CW3S4-2', 'redox_raw_Avg(47)'  : 'CW3S4-3', 'redox_raw_Avg(48)'  : 'CW3S4-4',
    'temp_C_Avg(1)'     : 'CW1S1', 'temp_C_Avg(2)'        : 'CW1S2', 'temp_C_Avg(3)'        : 'CW1S3', 'temp_C_Avg(4)'        : 'CW1S4',
    'temp_C_Avg(5)'     : 'CW2S1', 'temp_C_Avg(6)'        : 'CW2S2', 'temp_C_Avg(7)'        : 'CW2S3', 'temp_C_Avg(8)'        : 'CW2S4',
    'temp_C_Avg(9)'     : 'CW3S1', 'temp_C_Avg(10)'       : 'CW3S2', 'temp_C_Avg(11)'       : 'CW3S3', 'temp_C_Avg(12)'       : 'CW3S4'
    }

# Dictionary with nodes for each wetland and depth in the Constructed Wetland pilot study
node_dictionary = {
    "CW1_20cm" : ["CW1S1-1", "CW1S2-1", "CW1S3-1", "CW1S4-1"],
    "CW1_40cm" : ["CW1S1-2", "CW1S2-2", "CW1S3-2", "CW1S4-2"],
    "CW1_60cm" : ["CW1S1-3", "CW1S2-3", "CW1S3-3", "CW1S4-3"],
    "CW1_80cm" : ["CW1S1-4", "CW1S2-4", "CW1S3-4", "CW1S4-4"],
    "CW2_20cm" : ["CW2S1-1", "CW2S2-1", "CW2S3-1", "CW2S4-1"],
    "CW2_40cm" : ["CW2S1-2", "CW2S2-2", "CW2S3-2", "CW2S4-2"],
    "CW2_60cm" : ["CW2S1-3", "CW2S2-3", "CW2S3-3", "CW2S4-3"],
    "CW2_80cm" : ["CW2S1-4", "CW2S2-4", "CW2S3-4", "CW2S4-4"],
    "CW3_20cm" : ["CW3S1-1", "CW3S2-1", "CW3S3-1", "CW3S4-1"],
    "CW3_40cm" : ["CW3S1-2", "CW3S2-2", "CW3S3-2", "CW3S4-2"],
    "CW3_60cm" : ["CW3S1-3", "CW3S2-3", "CW3S3-3", "CW3S4-3"],
    "CW3_80cm" : ["CW3S1-4", "CW3S2-4", "CW3S3-4", "CW3S4-4"]
    }


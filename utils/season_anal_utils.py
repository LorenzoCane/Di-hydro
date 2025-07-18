'''
'''


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def inspect_missing(df, plot=True, plot_title= ' Missing Value Heatmap', top_n = 10):
    '''
        Inspect missing values in a DataFrame. Can generate summary plots.
    
        Parameters:
        -----------
        df:  pandas.DataFrame
            The DataFrame to inspect.
        plot: bool, opt
            If True, shows a heatmap (default : True).
        plot_title: str, opt
            Title of the heatmap created if plot = true
        top_n : int, opt 
            Number of top columns with missing values to print (default : 10). 
    
        Returns:
        -------
            summary:  pandas.Series
                Missing value counts per column.   
    '''

    #Total number if missing
    total_missing = df.isnull().sum()
    #Check if there are missing
    missing_check = total_missing[total_missing > 0]

    if missing_check.empty:
        print("No missing values found in the DataFrame.")
        return None
    
    print(f'Found {len(missing_check)} columns with missing values:')
    print(missing_check.sort_values(ascending=False).head(top_n))

    if plot:
        plt.figure(figsize=(12,6))
        sns.heatmap(df.isnull(), cbar=False, yticklabels=False)
        plt.title(plot_title)
        plt.xlabel('Columns')
        plt.show()
    
    return missing_check

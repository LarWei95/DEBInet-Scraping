'''
Created on 03.01.2022

@author: larsw
'''
from control.datacontrol import WebScraper
import matplotlib.pyplot as plt
import numpy as np

def plot_scatter_comparison (df, first_category, second_category):
    
    
    first_df = df[first_category]
    second_df = df[second_category]
    
    first_ingredients = first_df.columns
    second_ingredients = second_df.columns
    
    first_count = len(first_ingredients)
    second_count = len(second_ingredients)
    
    i = 1
    
    for first_ingredient in first_ingredients:
        first_values = first_df[first_ingredient].values
        
        for second_ingredient in second_ingredients:
            second_values = second_df[second_ingredient].values
            
            plt.subplot(first_count, second_count, i)
            
            plt.scatter(first_values, second_values, s=1)
            
            plt.xlabel(first_ingredient)
            plt.ylabel(second_ingredient)
            
            plt.grid(True, alpha=0.5)
            
            i += 1
            
    plt.gcf().set_size_inches((100.0, 50.0))
    plt.tight_layout()
    
    plt.savefig("comparison.png")
    plt.close("all")
    
def plot_correlation_matrix (df):
    correlations = df.corr()
    
    print(correlations)
    
    labels = correlations.index.get_level_values(1)
    xyrange = np.arange(0, len(labels))
    
    plt.matshow(correlations)
    
    plt.xticks(xyrange, labels, rotation=90)
    plt.yticks(xyrange, labels)
    
    plt.grid(True)
    
    plt.gcf().set_size_inches((19.0, 19.0))
    plt.tight_layout()
    
    plt.savefig("correlations.png")
    plt.close("all")

def main(first_category, second_category):
    df = WebScraper.get_saved_csv_data("./data.csv")
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    
    plot_correlation_matrix(df)
    plot_correlation_matrix(df)

if __name__ == '__main__':
    FIRST_CATEGORY = "Main Ingredients"
    SECOND_CATEGORY = "Main Ingredients"
    
    main(FIRST_CATEGORY, SECOND_CATEGORY)
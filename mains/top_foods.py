'''
Created on 03.01.2022

@author: larsw
'''
from control.datacontrol import WebScraper
import os
import os.path as osp

def main ():
    results_folder = "./TopFoods"
    
    df = WebScraper.get_saved_csv_data("./data.csv")
    
    categories = df.index.levels[0]
    ingredient_categories = df.columns.levels[0]
    
    for category in categories:
        sel1_df = df.loc[category]
        
        for ingredient_cat in ingredient_categories:
            sel2_df = sel1_df[ingredient_cat]
            
            ingredients = sel2_df.columns
            
            for ingredient in ingredients:
                sel3_df = sel2_df[ingredient].sort_values()
                sel3_df = sel3_df.dropna()
                
                lowest = sel3_df.iloc[:20]
                highest = sel3_df.iloc[-20:]
                
                path = osp.join(results_folder, category, ingredient_cat, ingredient)
                path = path.replace(":","").replace(";","")
                
                os.makedirs(path, exist_ok=True)
                
                low_path = osp.join(path, "Lowest.csv")
                high_path = osp.join(path, "Highest.csv")
                
                lowest.to_csv(low_path, sep=";")
                highest.to_csv(high_path, sep=";")
        

if __name__ == '__main__':
    main()
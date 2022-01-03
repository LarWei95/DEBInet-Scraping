'''
Created on 03.01.2022

@author: larsw

Scraping script for loading the data from the website and saving it locally,
both as JSON and CSV. All weight units are converted to grams.
'''
from control.datacontrol import WebScraper
    
def main ():
    data = WebScraper.get_and_save_data("./data.json")
    df = WebScraper.json_to_pandas(data)
    df.to_csv("./data.csv", sep=";")
    
if __name__ == '__main__':
    main()
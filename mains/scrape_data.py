'''
Created on 03.01.2022

@author: larsw
'''
import json
from control.datacontrol import WebScraper
    
def main ():
    WebScraper.get_and_save_data("./data.json")
    
if __name__ == '__main__':
    main()
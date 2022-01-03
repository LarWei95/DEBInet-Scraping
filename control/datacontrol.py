'''
Created on 03.01.2022

@author: larsw
'''
from bs4 import BeautifulSoup
import requests
import numpy as np
import os
import os.path as osp
import json
import traceback as tb
import pandas as pd

class WebScraper(object):
    @classmethod
    def parse_categories (cls, html):
        html = html.find("div", {"class" : "list-group"})
        categories = html.find_all("a", {"class" : "list-group-item"})
        
        categories = {
                x.string : "https://www.ernaehrung.de/lebensmittel/en/"+x["href"]
                for x in categories
            }
        
        return categories
    
    @classmethod
    def get_categories (cls):
        url = "https://www.ernaehrung.de/lebensmittel/en/kategorien.php"
        html = BeautifulSoup(requests.get(url).content, "html.parser")
        return cls.parse_categories(html)
        
    @classmethod
    def parse_products (cls, html):
        html = html.find("div", {"class" : "list-group"})
        products = html.find_all("a", {"class" : "list-group-item"})
        
        products = {
                x.string : x["href"]
                for x in products
            }
        
        return products
    
    @classmethod
    def get_products (cls, url):
        html = BeautifulSoup(requests.get(url).content, "html.parser")
        return cls.parse_products(html)
    
    @classmethod
    def get_all (cls):
        categories = WebScraper.get_categories()
    
        all_data = {}
        
        for category in categories:
            url = categories[category]
            
            products = WebScraper.get_products(url)
            
            category_data = {}
            
            for product in products:
                product_url = products[product]
                
                try:
                    stats = WebScraper.get_product_details(product_url)
                    category_data[product] = stats
                except:
                    print("Error at {:s}".format(product_url))
                    tb.print_exc()
                
            all_data[category] = category_data
            
        return all_data
    
    @classmethod
    def unify_mass (cls, mass, unit):
        # Normalize all convertable masses to g
        mass = float(mass.strip().replace(",", "."))
        
        if unit is not None:
            unit_binary = bytes(unit, "utf-8")
            
            if unit == "kg":
                mass *= 1e3
            elif unit == "mg":
                mass /= 1e3
            elif unit_binary == b'\xc2\xb5g':
                mass /= 1e6
            elif unit == "nm":
                mass /= 1e9
                
        return mass
    
    @classmethod
    def parse_product_details (cls, html):
        details = html.find_all("div", {"class" : "panel-default"})
        
        stats = {}
        
        for detail_table in details:
            heading = detail_table.find("div", {"class" : "panel-heading"})
            
            if heading is None:
                continue
            
            heading = heading.get_text().strip()
            
            data = detail_table.find("div", {"class" : "table-responsive"}).find_all("tr")
        
            detail_stats = {}
            
            for tr in data:
                td = tr.find_all("td")
                
                if len(td) == 3:
                    ingredient = td[0].string
                    mass = td[1].string                
                    unit = td[2].string
                    
                    if ingredient: ingredient = ingredient.strip()
                    
                    if unit: unit = unit.strip()
                    
                    if mass: mass = cls.unify_mass(mass, unit)
                    
                    detail_stats[ingredient] = mass
                    
            stats[heading] = detail_stats
            
        return stats
    
    @classmethod
    def get_product_details (cls, url):
        html = BeautifulSoup(requests.get(url).content, "html.parser")
        return cls.parse_product_details(html)
        
    @classmethod
    def get_and_save_data (cls, out_path):
        out_path = osp.abspath(out_path)
        os.makedirs(osp.dirname(out_path), exist_ok=True)
        
        all_data = cls.get_all()
        
        with open(out_path, "w") as f:
            json.dump(all_data, f, indent=3)
        
        return all_data
    
    @classmethod
    def get_saved_json_data (cls, path):
        with open(path, "r") as f:
            data = json.load(f)
            
        return data
    
    @classmethod
    def get_saved_csv_data (cls, path):
        index_cols = [0, 1]
        col_indices = [0, 1]
        
        df = pd.read_csv(path, sep=";", index_col=index_cols,
                         header=col_indices)
        return df
    
    @classmethod
    def attributes_to_series (cls, attributes_dict):
        new_attributes = {}
        
        for attribute_key in attributes_dict:
            value = attributes_dict[attribute_key]
                
            new_attributes[attribute_key] = value
        
        return pd.Series(new_attributes)
    
    @classmethod
    def json_to_pandas (cls, data):
        used_cats = []
        all_data = []
        
        for cat in data:
            products = data[cat]
            
            new_cat_products = []
            
            for product in products:
                stats = products[product]
                
                product_stats = []
                
                for stat_cat in stats:
                    attributes = stats[stat_cat]
                    
                    new_attributes = cls.attributes_to_series(attributes)
                    
                    indx = new_attributes.index.values
                    stat_cat_indx = np.repeat(stat_cat, len(indx))
                    
                    indx = pd.MultiIndex.from_arrays([stat_cat_indx, indx], names=["Category", "Ingredient"])
                    new_attributes.index = indx
                    
                    product_stats.append(new_attributes)
                
                product_stats = pd.concat(product_stats).to_frame(product)
                new_cat_products.append(product_stats)
            
            if len(new_cat_products) != 0:
                new_cat_products = pd.concat(new_cat_products, axis=1)
                new_cat_products = new_cat_products.transpose()
                
                used_cats.append(cat)
                all_data.append(new_cat_products)
            
        all_data = pd.concat(all_data, keys=used_cats)
        return all_data
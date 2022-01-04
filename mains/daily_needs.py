'''
Created on 03.01.2022

@author: larsw
'''

from control.datacontrol import WebScraper

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

# https://www.nhs.uk/live-well/eat-well/what-are-reference-intakes-on-food-labels/
DAILY_NEEDS = {
        "Kilocalories" : 2000,
        "Fat" : 35, # Below 70g
        "Saturated fatty acids" : 10, # Below 20g
        "Carbohydrates" : 260,
        "Total sugar content" : 90, # ???
        "Protein" : 50,
        "Sodium chloride" : 3, # Below 6g
        
        "Biotin" : 30 * 1e-6,
        # "Vitamin A Retinol" : 600 * 1e-6,
        "Vitamin B1" : 1.4 * 1e-3,
        "Vitamin B2" : 1.6 * 1e-3,
        "Niacinequivalent" : 18 * 1e-3,
        "Vitamin B12" : 6 * 1e-3,
        "Vitamin C" : 75 * 1e-3,
        "Vitamin D" : 5 * 1e-6,
        "Vitamin E activ." : 10 * 1e-3,
        "Vitamin K" : 80 * 1e-6
    }
FOODS = [
        "Wholemeal noodles cooked",
        "Fruit-Muesli",
        "Pineapple tinned drained",
        "Apple fresh",
        "Banana fresh",
        "Citrus fruit",
        "Salmon",
        "Sweet cherry fresh",
        "Wholemeal multi-grain bread"
    ]

DAILY_NEEDS_DF = pd.Series({
        k : DAILY_NEEDS[k]
        for k in sorted(list(DAILY_NEEDS.keys()))
    })

def get_relevant_data ():
    df = WebScraper.get_saved_csv_data("./data.csv")
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    return df

def cut_data (df):
    df = df.droplevel(0, axis=0)
    df = df.droplevel(0, axis=1)
    
    required_attributes = sorted(list(DAILY_NEEDS.keys()))
    
    df = df[required_attributes]
    df = df.loc[FOODS]
    
    return df

def calculate_nutrition (input_values, weights):
    repeated_weights = tf.repeat(weights[:,tf.newaxis], input_values.shape[1], axis=1)
    
    out_value = input_values * tf.abs(repeated_weights)
    out_value = tf.reduce_sum(out_value, axis=0)
    return out_value

def optimize_mass (df, target_df):
    values = df.values.astype(np.float64)
    target_values = target_df.values.astype(np.float64)
    
    # Weighting column-wise losses by the inverse of their max
    # Causes more optimization on low-value attributes
    loss_weights = tf.constant(1 / tf.reduce_max(df, axis=0))
    
    input_values = tf.constant(values)
    target_values = tf.constant(target_values)
    
    lr = 1e-2
    
    weights = tf.Variable(np.full(input_values.shape[0], 0.01, dtype=np.float64))
    
    for i in range(10000):
        with tf.GradientTape() as gt:
            nutrition = calculate_nutrition(input_values, weights)
            loss_piecewise = tf.pow((nutrition - target_values), 2.0) * loss_weights
            loss = tf.reduce_mean(loss_piecewise)
            
        gradients = gt.gradient(loss, [weights])[0]
        
        weights.assign(weights - lr * gradients)
        
        if i % 1000 == 0:
            masses = pd.Series(tf.abs(weights.numpy()), index=df.index.values) * 100 # Each unit is 100g
            nutrition = nutrition.numpy()
            
            nutrition = pd.Series(nutrition, index=target_df.index.values)
            losses_df = pd.Series(loss_piecewise.numpy(), index=target_df.index.values)
            nutrition = pd.concat(
                [nutrition, target_df, losses_df], 
                axis=1, 
                keys=["Achieved", "Required", "Losses"])
            
            print(masses.round(5))
            print(nutrition.round(5))
            print(loss.numpy())
    
    masses = pd.Series(tf.abs(weights.numpy()), index=df.index.values) * 100 # Each unit is 100g
    masses = masses.sort_values()

    nutrition = calculate_nutrition(input_values, weights).numpy()
    nutrition = pd.Series(nutrition, index=target_df.index.values)
    
    plt.subplot(2, 1, 1)
    plt.title("Food mass to eat")
    plt.bar(masses.index.values, masses.values)
    plt.grid(True, alpha=0.5)
    plt.ylabel("Mass (in gramm)")
    
    plt.subplot(2, 1, 2)
    plt.title("Nutrient requirements fulfilled")
    
    fulfillment = nutrition / target_df * 100.0
    
    plt.bar(fulfillment.index.values, fulfillment.values)
    plt.grid(True, alpha=0.5)
    plt.ylabel("Fulfillment (in %)")
    
    plt.tight_layout()
    plt.show()
    
    
def main ():
    full_df = get_relevant_data()
    df = cut_data(full_df)
    
    optimize_mass(df, DAILY_NEEDS_DF)
    
    
if __name__ == '__main__':
    main()
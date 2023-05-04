import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

# In this file, we explore the open-source data of Instacart 2017 transactions. https://www.instacart.com/datasets/grocery-shopping-2017


if __name__ == "__main__":
    local_path = "USE YOUR OWN PATH TO THE DATA"

    products = pd.read_csv(local_path+"/instacart transactions/products.csv")
    aisles = pd.read_csv(local_path+"/instacart transactions/aisles.csv")
    departments = pd.read_csv(local_path+"/instacart transactions/departments.csv")
    orders_products = pd.read_csv(local_path+"instacart transactions/orders_products.csv").sort_values(by="user_id")
    orders_products["user_id"] = orders_products["user_id"].astype('int')
    orders_products["product_id"] = orders_products["product_id"].apply(lambda cell:''.join(c for c in cell if c not in "'[]").split(', '))

    # Explore basic information about the dataset
    obs = len(orders_products)
    users = len(orders_products["user_id"].unique())
    n_products = len(products["product_id"].unique())
    n_aisles = len(aisles)

    print("The Instacart Dataset has " + str(obs) + " observations.")
    print("The Instacart Dataset has " + str(users) + " users.")
    print("The Instacart Dataset has " + str(n_products) + " products.")
    print("The Instacart Dataset has " + str(n_aisles) + " categories.")

    # Explore the number of transactions per user with the help of a histogram
    counts, bins = np.histogram(orders_products["user_id"].value_counts(), bins=100)
    plt.stairs(counts, bins)
    plt.hist(bins[:-1], bins, weights=counts)

    plt.show()

    # Explore the number of products purchased per transaction with the help of a histogram
    orders_products["n_products"] = orders_products["product_id"].apply(lambda x: len(x))

    counts, bins = np.histogram(orders_products["n_products"], bins=orders_products["n_products"].max())
    plt.stairs(counts, bins)
    plt.hist(bins[:-1], bins, weights=counts)

    plt.show()

    # Explore the number of times a product has been purchased with the help of a boxplot
    s = orders_products['product_id'].explode().dropna().value_counts()
    plt.boxplot(s)

    plt.show()

    # Explore the number of times a product has been purchased with the help of a boxplot for products that have been purchased a low amount of times
    s = s[ s <= 1000 ] 
    plt.boxplot(s)

    plt.show()

    # Explore the popularity of the different aisles (categories)
    orders_products_aisles = orders_products.merge(products[['product_id','aisle_id','department_id']], how = 'inner', on = 'product_id')

    plt.bar(orders_products_aisles.groupby('aisle')['product_id'].count().sort_values(ascending = False).reset_index()[0:10])
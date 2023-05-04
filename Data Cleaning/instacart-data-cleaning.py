import pandas as pd
import numpy as np
from tqdm import tqdm


if __name__ == "__main__":

    local_path = "USE YOUR OWN PATH TO THE DATA"

    orders = pd.read_csv(local_path+"instacart transactions/orders.csv").sort_values(by=["order_id"])
    users = orders.user_id.unique()
    products = pd.read_csv(local_path+"/instacart transactions/products.csv")

    orders_products_prior = pd.read_csv(local_path+"instacart transactions/order_products__prior.csv")
    orders_products_train = pd.read_csv(local_path+"instacart transactions/order_products__train.csv")

    orders_products = pd.concat([orders_products_prior,orders_products_train], ignore_index=True)

    orders_products = orders_products.groupby('order_id')['product_id'].apply(list).reset_index()

    orders_products['user_id'] = np.nan
    i = 0
    for x in tqdm(orders_products["order_id"]):
        try:
           user_id = orders.loc[orders['order_id'] == x]["user_id"]
        except:
            user_id = np.nan
        orders_products.at[i, "user_id"] = user_id
        i+=1
    
    print(orders_products)

    orders_products.to_csv(local_path+"/instacart transactions/orders_products.csv", index=False)
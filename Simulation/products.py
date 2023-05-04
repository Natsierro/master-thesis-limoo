import pandas as pd
import numpy as np
from tqdm import tqdm

#This function calculates the interest of a specific community for a specific product
def interest(population, product_id, basket, all_orders):
    n_interest = 0

    #For each user of the population in the cluster, we look at their past purchases and if one of the past purchase has a lift above 1 with the product of interest, we consider that they are interested.
    for index, row in population.iterrows():
        user_id = row["user_id"]
        all_products = all_orders.loc[(all_orders["user_id"] == user_id), "product_id"].unique().tolist()

        for product in all_products:
            try:
                l = basket.loc[(basket["item_A"] == product) & (basket["item_B"] == product_id), basket.columns.get_loc("lift")]
            except:
                l = 0
            
            if l > 1:
                print(l)
                n_interest += 1
                break
    #We return the share of users who are interested in this product
    return float(n_interest/len(population))

#To simplify the simulation and since this step is not crucial, we decided that the probability to make a purchase for an interested community is 50%
#In reality it is a complex and dynamic process in community group buying
def probability_purchase(users, product_id, basket, all_orders):
    return 0.5

#To simulate the demand for a product in a specific scenario, we use this function that outputs the population again but with a new column with the demand for the specific product
def simulate_demand(product_id, population, all_orders, products, basket, cutoff):
    clusters = population["cluster"].unique().tolist()
    name_row = "productID_" + str(product_id)
    population[name_row] = 0

    for i in clusters:
        #With the above mentioned function, we calculate the share of the cluster that is interested in the product
        x = interest(population.loc[population["cluster"] == i], product_id, basket, all_orders)

        if (x != 0.0):
            #If this share is above the cutoff defined in the simulation, we add the probability of purchase to the users in this cluster
            if(x >= cutoff):
                population.loc[population["cluster"] == i, name_row] = probability_purchase(population.loc[population["cluster"] == i], product_id, basket, all_orders)

        else:
            #If it was not possible to calculate the interest with the lift values in the dataset, we calculate the interest based on the category of the product and if the past purchases of the users in this category is higher than the cutoff
            users = population.loc[population["cluster"] == i, "user_id"].tolist()
            department_share = all_orders[all_orders["user_id"].isin(users)].groupby('department_id')['add_to_cart_order'].sum().reset_index()
            department_share['department_share'] = department_share['add_to_cart_order']
            department_share['department_share'] = department_share['department_share'].apply(lambda x: x / department_share['add_to_cart_order'].sum())            

            department_id = products.loc[products["product_id"]==product_id, "department_id"].values
            try:
                share = department_share.loc[department_share["department_id"]==department_id[0], "department_share"].values[0]
            except:
                share = 0
            if(share >= cutoff):
                population.loc[population["cluster"] == i, name_row] = probability_purchase(population.loc[population["cluster"] == i], product_id, basket, all_orders)

    return population           
        
if __name__ == "__main__":
    #For this second step of the simulation, we need to use the output of the clustering file in the "local_path_code"
    local_path_code = "USE YOUR OWN PATH TO THE OUTPUT OF THE SIMULATION"
    local_path_data = "USE YOUR OWN PATH TO THE DATA"
    print("Importing initial data...")

    basket = pd.read_csv(local_path_code+"basket.csv", index_col=0)
    basket = basket.loc[basket["lift"]>1]

    #load instacart data
    path = local_path_data + 'instacart transactions/'
    aisles = pd.read_csv(path+'aisles.csv')
    departments = pd.read_csv(path+'departments.csv')
    prior = pd.read_csv(path+'order_products__prior.csv')
    train = pd.read_csv(path+'order_products__train.csv')
    orders = pd.read_csv(path+'orders.csv')
    products = pd.read_csv(path+'products.csv')

    orders_products = pd.read_csv(path+"orders_products.csv").sort_values(by="user_id")
    orders_products["user_id"] = orders_products["user_id"].astype('int')

    users = orders_products["user_id"].unique().tolist()

    all_orders = pd.concat([prior,train],axis = 0)
    all_orders = all_orders.merge(products[['product_id','aisle_id','department_id']], how = 'inner', on = 'product_id')
    all_orders = all_orders.merge(aisles, on = 'aisle_id')
    all_orders = all_orders.merge(departments, on = 'department_id')
    all_orders = all_orders.merge(orders[['order_id','user_id']], on = 'order_id')

    scenarios =[
        {
        'lat': 46.52266,
        'lng': 6.62024,
        'size': 1,
        'share_users': 0.1,
        'max_housing': 100,
        'min_housing': 10,
        'max_distance': 1,
        'name': 'Lausanne'
        },
        {
        'lat': 47.37333,
        'lng': 8.51789,
        'size': 1,
        'share_users': 0.1,
        'max_housing': 100,
        'min_housing': 10,
        'max_distance': 1,
        'name': 'Zurich'
        },
        {
        'lat': 46.21011,
        'lng': 6.12828,
        'size': 1,
        'share_users': 0.1,
        'max_housing': 100,
        'min_housing': 10,
        'max_distance': 1,
        'name': 'Geneva'
        },
        {
        'lat': 46.55259,
        'lng': 6.66717,
        'size': 1,
        'share_users': 0.1,
        'max_housing': 100,
        'min_housing': 10,
        'max_distance': 1,
        'name': 'Epalinges'
        },
        {
        'lat': 47.34520,
        'lng': 8.57400,
        'size': 1,
        'share_users': 0.1,
        'max_housing': 100,
        'min_housing': 10,
        'max_distance': 1,
        'name': 'Weinegg'
        },
        {
        'lat': 46.17921,
        'lng': 6.10743,
        'size': 1,
        'share_users': 0.1,
        'max_housing': 100,
        'min_housing': 10,
        'max_distance': 1,
        'name': 'Grand-Lancy'
        },
        {
        'lat': 46.64424,
        'lng': 6.63436,
        'size': 25,
        'share_users': 0.1,
        'max_housing': 100,
        'min_housing': 10,
        'max_distance': 1,
        'name': 'Echallens'
        },
        {
        'lat': 47.42964,
        'lng': 8.74184,
        'size': 25,
        'share_users': 0.1,
        'max_housing': 100,
        'min_housing': 10,
        'max_distance': 1,
        'name': 'Weisslingen'
        },
        {
        'lat': 46.44401,
        'lng': 6.18574,
        'size': 25,
        'share_users': 0.1,
        'max_housing': 100,
        'min_housing': 10,
        'max_distance': 1,
        'name': 'St-Cergue'
        }
    ]

    #The defined cutoff to calcute which community or cluster would be willing to buy a specific product. In this case if 10% of the cluster has a strong interest for the product, we decide that they participate in the group buying process
    cutoff = 0.1

    # 30 products are taken to simulate the demand. In our case we take 10 of the most ordered products, 10 of middle demand and 10 of low demand. All of this randomly.
    list_products_orders_high = all_orders.groupby('product_id')['add_to_cart_order'].sum().sort_values(ascending = False)[0:1000].sample(10).index.tolist()
    list_products_orders_medium = all_orders.groupby('product_id')['add_to_cart_order'].sum().sort_values(ascending = False)[1001:3000].sample(10).index.tolist()
    list_products_orders_low = all_orders.groupby('product_id')['add_to_cart_order'].sum().sort_values(ascending = False)[3001:7000].sample(10).index.tolist()
    
    products_list = list_products_orders_high + list_products_orders_medium + list_products_orders_low
    random_products = products[products['product_id'].isin(products_list)]

    #For each scenario, we calculate the demand for each product and output it to the "populated_products_clusters.csv" in each folder for each scenario
    for parameters in scenarios:
        print("Creating product recommendations for " + parameters['name'])
        cluster = pd.read_csv(local_path_code+parameters['name']+"/populated_cluster.csv", index_col=0)
        for index, row in tqdm(random_products.iterrows(), total=random_products.shape[0]):
            cluster = simulate_demand(row["product_id"], cluster, all_orders, products, basket, cutoff)
        cluster.to_csv(local_path_code+parameters['name']+"/populated_products_cluster.csv")
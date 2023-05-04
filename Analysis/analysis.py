import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl

 
if __name__ == "__main__":
    local_path_code = "USE YOUR OWN PATH TO THE OUTPUT OF THE SIMULATION"
    local_path_data = "USE YOUR OWN PATH TO THE DATA"

    #Importing data
    print()
    print("Importing initial data...")
    print("--------------------------------------")

    basket = pd.read_csv(local_path_code+"basket.csv", index_col=0)
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
    all_orders = all_orders.merge(products[['product_id','product_name']], on = 'product_id')

    #The different scenarios that have been developed for the thesis
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

    #For the analysis, we group the different restults files together
    df = pd.DataFrame(columns=["product_id", "location", "distance_group", "distance_group_last_mile", "distance_no_group"])

    for parameters in scenarios:
        df = pd.concat([df,pd.read_csv(local_path_code+parameters["name"]+"/results.csv",usecols=range(1,6))], ignore_index=True)

    df_nonEmpty = df.loc[df["distance_group"] != 0.000000, :].copy()

    print()
    print("Sharing results...")
    print("--------------------------------------")
    print("Share of non-null observations: " + str(round(100*len(df_nonEmpty)/df.shape[0])) + " %")

    # The full distance for group buying is the sum of the last mile pickup and the VRP
    df_nonEmpty.loc[:,'full_distance_grouped'] = df.loc[:,('distance_group','distance_group_last_mile')].sum(axis=1)

    #Sustainability and Logistics results
    print()
    print("Sharing results about sustainability and logistics...")
    print("--------------------------------------")

    #Boxplot about the distances for community group buying and classic online retailing
    df_temporary = df_nonEmpty.rename(columns={'distance_group': 'Community Group Buying', 'distance_no_group': 'Classic online retailing'})
    df_temporary[['Community Group Buying','Classic online retailing']].plot(kind='box')
    plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    plt.ylabel('meters (m)')
    plt.savefig(local_path_code + "0_analysis/" +'boxplot_distance.png')
    print("Exported: " + local_path_code + "0_analysis/" +'boxplot_distance.png')

    #Histogram with the same data
    df_nonEmpty[['distance_group','distance_no_group']].plot(kind='hist', alpha=0.5)
    plt.savefig(local_path_code + "0_analysis/" +'hist_distance.png')
    print("Exported: " + local_path_code + "0_analysis/" +'hist_distance.png')

    #Histogram adding the last mile pickup distance
    df_nonEmpty[['distance_group','distance_no_group','distance_group_last_mile']].plot(kind='hist', alpha=0.5, bins=30)
    plt.savefig(local_path_code + "0_analysis/" +'hist_distance_lastmile.png')
    print("Exported: " + local_path_code + "0_analysis/" +'hist_distance_lastmile.png')
    
    #Boxplote comparing the full distance that has been grouped compared with the classic online retailing model
    df_temporary = df_nonEmpty.rename(columns={'full_distance_grouped': 'Community Group Buying with last mile', 'distance_no_group': 'Classic online retailing'})
    df_temporary[['Community Group Buying with last mile','Classic online retailing']].plot(kind='box')
    plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    plt.ylabel('meters (m)')
    plt.savefig(local_path_code + "0_analysis/" +'boxplot_distance_lastmile.png', bbox_inches = 'tight')
    print("Exported: " + local_path_code + "0_analysis/" +'boxplot_distance_lastmile.png')

    #We calculate the relative sustainability improvements 
    sustainability_improvement_group = ((df_nonEmpty["distance_group"]-df_nonEmpty["distance_no_group"])/df_nonEmpty["distance_no_group"]).mean()
    sustainability_improvement_group_last_mile = ((df_nonEmpty["full_distance_grouped"]-df_nonEmpty["distance_no_group"])/df_nonEmpty["distance_no_group"]).mean()

    print("Grouping the demand REDUCES the distance of delivery by: " + str(round(-100*sustainability_improvement_group)) + " % on average")

    print("Grouping the demand INCREASES the distance of delivery by: " + str(round(100*sustainability_improvement_group_last_mile)) + " % on average taking into account the last mile pickup of customers")

    #Communities results
    print()
    print("Sharing results about communities...")
    print("--------------------------------------")
    
    #We create a dictionnary with the different community average sizes and display it
    data = {}
    for parameters in scenarios:
        df_communities = pd.read_csv(local_path_code+parameters["name"]+"/populated_cluster.csv")
        clusters_size = df_communities.groupby('cluster').count().reset_index()
        size = clusters_size["Unnamed: 0"].mean()
        data[parameters["name"]] = size

    keys = list(data.keys())
    values = list(data.values())
    fig, ax = plt.subplots()
    ax.bar(np.arange(len(keys)), values)

    ax.set_xlabel("Scenario Location")
    ax.set_ylabel("Average community size")
    ax.set_title("The average community size in different scenarios")
    ax.set_xticks(np.arange(len(keys)), keys, rotation = 90)

    plt.savefig(local_path_code + "0_analysis/" +'community_size.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'community_size.png')


    #Products and recommendation results
    print()
    print("Sharing results about products and recommendation system...")
    print("--------------------------------------")

    products_id = df["product_id"].unique().tolist()
    products_name = products.loc[products['product_id'].isin(products_id),'product_name'].tolist()
    
    #We calculate the share of the product present in the overall dataset
    product_share = all_orders.groupby('product_name')['add_to_cart_order'].sum().reset_index()
    product_share['product_share'] = product_share['add_to_cart_order']
    product_share['product_share'] = product_share['product_share'].apply(lambda x: x / product_share['add_to_cart_order'].sum())

    data = product_share.sort_values(by = 'product_share',ascending = False, ignore_index=True)[product_share['product_name'].isin(products_name)]

    #We display the different products that have been used in the simulation and their share of ordering in the overall dataset
    keys = data['product_name'].tolist()
    values = data['product_share'].tolist()
    fig, ax = plt.subplots()
    ax.bar(np.arange(len(keys)), values, width = 0.2)

    ax.set_xlabel("Product Name")
    ax.set_ylabel("Unit Share")
    ax.set_title("Popularity of products used in the recommendation system")
    ax.set_xticks(np.arange(len(keys)), keys, rotation = 90)

    plt.savefig(local_path_code + "0_analysis/" +'product_share.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'product_share.png')

    data = product_share.sort_values(by = 'product_share',ascending = False, ignore_index=True)[product_share['product_name'].isin(products_name)]

    #We display the same but deleted the first product which had a much higher share
    keys = data['product_name'][1:].tolist()
    values = data['product_share'][1:].tolist()
    fig, ax = plt.subplots()
    ax.bar(np.arange(len(keys)), values, width = 0.2)

    ax.set_xlabel("Product Name")
    ax.set_ylabel("Unit Share")
    ax.set_title("Popularity of products used in the recommendation system")
    ax.set_xticks(np.arange(len(keys)), keys, rotation = 90)
    plt.ticklabel_format(style='plain', axis='y')

    plt.savefig(local_path_code + "0_analysis/" +'product_share_2.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'product_share_2.png')

    #We explore the missing data and if there is a relation between a product not being recommended and its share in the dataset
    keys = data['product_name'].tolist()
    data = []
    for prod in products_id:
        data.append(len(df.loc[(df["distance_group"] != 0.000000) & (df["product_id"] == prod),:]))

    
    fig, ax = plt.subplots()
    ax.bar(np.arange(len(keys)), data, width = 0.2)

    ax.set_xlabel("Product Name")
    ax.set_ylabel("Times Recommended")
    ax.set_title("Number of times a product has been recommended to a community")
    ax.set_xticks(np.arange(len(keys)), keys, rotation = 90)
    plt.ticklabel_format(style='plain', axis='y')

    plt.savefig(local_path_code + "0_analysis/" +'product_recommended.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'product_recommended.png')

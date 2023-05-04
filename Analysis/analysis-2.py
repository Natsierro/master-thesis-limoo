import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

 
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

    #This time, we differentiate between the different housing densities in the different scenarios
    scenarios_city =[
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
        }
    ]

    scenarios_suburbs =[
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
        }
    ]

    scenarios_remote =[
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


    df = pd.DataFrame(columns=["product_id", "location", "distance_group", "distance_group_last_mile", "distance_no_group"])

    #For each of the scenarios in the cities, suburbs and remote areas, we display the same graphs (boxplot and histograms) about the different distances as well as the sustainability improvements like in the analysis.py file

    #Cities results
    for parameters in scenarios_city:
        df = pd.concat([df,pd.read_csv(local_path_code+parameters["name"]+"/results.csv",usecols=range(1,6))], ignore_index=True)

    df_nonEmpty = df.loc[df["distance_group"] != 0.000000, :].copy()

    print()
    print("Sharing results for city centers...")
    print("--------------------------------------")
    print("Share of non-null observations: " + str(round(100*len(df_nonEmpty)/df.shape[0])) + " %")

    df_nonEmpty.loc[:,'full_distance_grouped'] = df.loc[:,('distance_group','distance_group_last_mile')].sum(axis=1)

    
    print()
    print("Sharing results about sustainability and logistics...")
    print("--------------------------------------")
    df_nonEmpty[['distance_group','distance_no_group']].plot(kind='box')
    plt.savefig(local_path_code + "0_analysis/city_" +'boxplot_distance.png')
    print("Exported: " + local_path_code + "0_analysis/city_" +'boxplot_distance.png')

    df_nonEmpty[['distance_group','distance_no_group']].plot(kind='hist', alpha=0.5)
    plt.savefig(local_path_code + "0_analysis/city_" +'hist_distance.png')
    print("Exported: " + local_path_code + "0_analysis/city_" +'hist_distance.png')

    df_nonEmpty[['distance_group','distance_no_group','distance_group_last_mile']].plot(kind='hist', alpha=0.5, bins=30)
    plt.savefig(local_path_code + "0_analysis/city_" +'hist_distance_lastmile.png')
    print("Exported: " + local_path_code + "0_analysis/city_" +'hist_distance_lastmile.png')
    
    df_nonEmpty[['full_distance_grouped','distance_no_group']].plot(kind='box')
    plt.savefig(local_path_code + "0_analysis/city_" +'boxplot_distance_lastmile.png')
    print("Exported: " + local_path_code + "0_analysis/city_" +'boxplot_distance_lastmile.png')

    sustainability_improvement_group = ((df_nonEmpty["distance_group"]-df_nonEmpty["distance_no_group"])/df_nonEmpty["distance_no_group"]).mean()
    sustainability_improvement_group_last_mile = ((df_nonEmpty["full_distance_grouped"]-df_nonEmpty["distance_no_group"])/df_nonEmpty["distance_no_group"]).mean()

    print("Grouping the demand REDUCES the distance of delivery in city centers by: " + str(round(-100*sustainability_improvement_group)) + " % on average")

    print("Grouping the demand INCREASES the distance of delivery in city centers by: " + str(round(100*sustainability_improvement_group_last_mile)) + " % on average taking into account the last mile pickup of customers")


    #Suburbs results
    df = pd.DataFrame(columns=["product_id", "location", "distance_group", "distance_group_last_mile", "distance_no_group"])

    for parameters in scenarios_suburbs:
        df = pd.concat([df,pd.read_csv(local_path_code+parameters["name"]+"/results.csv",usecols=range(1,6))], ignore_index=True)

    df_nonEmpty = df.loc[df["distance_group"] != 0.000000, :].copy()

    print()
    print("Sharing results for suburbs...")
    print("--------------------------------------")
    print("Share of non-null observations: " + str(round(100*len(df_nonEmpty)/df.shape[0])) + " %")

    df_nonEmpty.loc[:,'full_distance_grouped'] = df.loc[:,('distance_group','distance_group_last_mile')].sum(axis=1)

    print()
    print("Sharing results about sustainability and logistics...")
    print("--------------------------------------")
    df_nonEmpty[['distance_group','distance_no_group']].plot(kind='box')
    plt.savefig(local_path_code + "0_analysis/suburbs_" +'boxplot_distance.png')
    print("Exported: " + local_path_code + "0_analysis/suburbs_" +'boxplot_distance.png')

    df_nonEmpty[['distance_group','distance_no_group']].plot(kind='hist', alpha=0.5)
    plt.savefig(local_path_code + "0_analysis/suburbs_" +'hist_distance.png')
    print("Exported: " + local_path_code + "0_analysis/suburbs_" +'hist_distance.png')

    df_nonEmpty[['distance_group','distance_no_group','distance_group_last_mile']].plot(kind='hist', alpha=0.5, bins=30)
    plt.savefig(local_path_code + "0_analysis/suburbs_" +'hist_distance_lastmile.png')
    print("Exported: " + local_path_code + "0_analysis/suburbs_" +'hist_distance_lastmile.png')
    
    df_nonEmpty[['full_distance_grouped','distance_no_group']].plot(kind='box')
    plt.savefig(local_path_code + "0_analysis/suburbs_" +'boxplot_distance_lastmile.png')
    print("Exported: " + local_path_code + "0_analysis/suburbs_" +'boxplot_distance_lastmile.png')

    sustainability_improvement_group = ((df_nonEmpty["distance_group"]-df_nonEmpty["distance_no_group"])/df_nonEmpty["distance_no_group"]).mean()
    sustainability_improvement_group_last_mile = ((df_nonEmpty["full_distance_grouped"]-df_nonEmpty["distance_no_group"])/df_nonEmpty["distance_no_group"]).mean()

    print("Grouping the demand REDUCES the distance of delivery in suburbs by: " + str(round(-100*sustainability_improvement_group)) + " % on average")

    print("Grouping the demand INCREASES the distance of delivery in suburbs by: " + str(round(100*sustainability_improvement_group_last_mile)) + " % on average taking into account the last mile pickup of customers")


    #Remote areas results
    df = pd.DataFrame(columns=["product_id", "location", "distance_group", "distance_group_last_mile", "distance_no_group"])

    for parameters in scenarios_remote:
        df = pd.concat([df,pd.read_csv(local_path_code+parameters["name"]+"/results.csv",usecols=range(1,6))], ignore_index=True)

    df_nonEmpty = df.loc[df["distance_group"] != 0.000000, :].copy()

    print()
    print("Sharing results for remote areas...")
    print("--------------------------------------")
    print("Share of non-null observations: " + str(round(100*len(df_nonEmpty)/df.shape[0])) + " %")

    df_nonEmpty.loc[:,'full_distance_grouped'] = df.loc[:,('distance_group','distance_group_last_mile')].sum(axis=1)

    print()
    print("Sharing results about sustainability and logistics...")
    print("--------------------------------------")
    df_nonEmpty[['distance_group','distance_no_group']].plot(kind='box')
    plt.savefig(local_path_code + "0_analysis/remote_" +'boxplot_distance.png')
    print("Exported: " + local_path_code + "0_analysis/remote_" +'boxplot_distance.png')

    df_nonEmpty[['distance_group','distance_no_group']].plot(kind='hist', alpha=0.5)
    plt.savefig(local_path_code + "0_analysis/remote_" +'hist_distance.png')
    print("Exported: " + local_path_code + "0_analysis/remote_" +'hist_distance.png')

    df_nonEmpty[['distance_group','distance_no_group','distance_group_last_mile']].plot(kind='hist', alpha=0.5, bins=30)
    plt.savefig(local_path_code + "0_analysis/remote_" +'hist_distance_lastmile.png')
    print("Exported: " + local_path_code + "0_analysis/remote_" +'hist_distance_lastmile.png')
    
    df_nonEmpty[['full_distance_grouped','distance_no_group']].plot(kind='box')
    plt.savefig(local_path_code + "0_analysis/remote_" +'boxplot_distance_lastmile.png')
    print("Exported: " + local_path_code + "0_analysis/remote_" +'boxplot_distance_lastmile.png')
 
    sustainability_improvement_group = ((df_nonEmpty["distance_group"]-df_nonEmpty["distance_no_group"])/df_nonEmpty["distance_no_group"]).mean()
    sustainability_improvement_group_last_mile = ((df_nonEmpty["full_distance_grouped"]-df_nonEmpty["distance_no_group"])/df_nonEmpty["distance_no_group"]).mean()

    print("Grouping the demand REDUCES the distance of delivery in remote areas by: " + str(round(-100*sustainability_improvement_group)) + " % on average")

    print("Grouping the demand INCREASES the distance of delivery in remote areas by: " + str(round(100*sustainability_improvement_group_last_mile)) + " % on average taking into account the last mile pickup of customers")


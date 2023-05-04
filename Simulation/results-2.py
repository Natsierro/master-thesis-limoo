import pandas as pd
import numpy as np
from tqdm import tqdm

import os
from geopy import distance

#Utility function to calculate the distance of a VRP
def distance_calc(depot, l):
    if(len(l)>0):
        d = distance.distance((depot[0],depot[1]), (l[0][0],l[0][1])).m

        for i in range(len(l)-1):
            d += distance.distance((l[i][0],l[i][1]),(l[i+1][0],l[i+1][1])).m
        
        d += distance.distance((l[-1][0],l[-1][1]), (depot[0],depot[1])).m
    else:
        d = 0

    return d

#Like in the results.py file, this function calculates the distances of the different VRPs for community group buying and classical deliveries
#However we add the distances based on the different willingness for users to travel using soft mobility
def results(product, cluster, depot, name):
    name_product = "productID_"+str(product)
    name_vrp = "vrp_productID_"+str(product)
    name_vrp_no_centers = "no_groups_vrp_productID_"+str(product)

    l = cluster.loc[cluster[name_vrp]!=0].sort_values(by=name_vrp).loc[:,["latitude","longitude"]].values.tolist()
    distance_group = distance_calc(depot, l)

    l = cluster.loc[cluster[name_vrp_no_centers]!=0].sort_values(by=name_vrp_no_centers).loc[:,["latitude","longitude"]].values.tolist()
    distance_no_group = distance_calc(depot, l)

    distance_group_last_mile = 0
    for index, row in cluster.loc[cluster[name_product]!=0].iterrows():
        latitude = cluster.loc[(cluster["cluster"] == row["cluster"]) & (cluster["distance_center"] == 0.0), "latitude"].values
        longitude = cluster.loc[(cluster["cluster"] == row["cluster"]) & (cluster["distance_center"] == 0.0), "longitude"].values
        distance_group_last_mile += 2 * distance.distance((row["latitude"],row["longitude"]),(latitude,longitude)).m

    data = {
        "product_id": [product],
        "location": [name],
        "distance_group": [distance_group],
        "distance_group_last_mile": [distance_group_last_mile],
        "distance_no_group": [distance_no_group]
    }

    #We range over the different potential willingness to travel using soft mobility
    cutoff = range(100,3001,100)
    for i in cutoff:
        distance_group_last_mile = 0
        for index, row in cluster.loc[cluster[name_product]!=0].iterrows():
            latitude = cluster.loc[(cluster["cluster"] == row["cluster"]) & (cluster["distance_center"] == 0.0), "latitude"].values
            longitude = cluster.loc[(cluster["cluster"] == row["cluster"]) & (cluster["distance_center"] == 0.0), "longitude"].values
            d = 2 * distance.distance((row["latitude"],row["longitude"]),(latitude,longitude)).m

            #All the distances above the maximum willingness to travel using soft mobility are taken into account in the last-mile pickup
            #The ones that are below are not taken into account since they are 0 CO2 emitting paths
            if d > i:
                distance_group_last_mile += d

        data["distance_group_last_mile_cutoff_"+str(i)] = distance_group_last_mile
    dataframe = pd.DataFrame(data)
    return dataframe

if __name__ == "__main__":
    local_path_code = "USE YOUR OWN PATH TO THE OUTPUT OF THE SIMULATION"
    local_path_data = "USE YOUR OWN PATH TO THE DATA"

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

    #We calucalte and output the results of the distances traveled for each scenario and each product. This is then output in the "reults-cutoff-lastmile.csv" which is used in the analysis section.
    for parameters in scenarios:
        print("Creating results for " + parameters['name'])
        depot = (parameters["lat"], parameters["lng"])
        cluster = pd.read_csv(local_path_code+parameters['name']+"/populated_products_vrp_cluster.csv", index_col=0)
        products = [x[10:] for x in cluster.columns.values.tolist() if x.startswith('productID_')]
        
        path = os.path.dirname(os.path.realpath(__file__))+"/output/"+parameters['name']+"/vrp"

        if not os.path.exists(path):
            os.makedirs(path)

        j = 0
        for product in tqdm(products):

            df2 = results(product, cluster, depot, parameters['name'])
            if(j==0):
                df = df2
            if(j!=0):
                df = pd.concat([df2, df])
            j += 1
            
        
        df.to_csv(os.path.dirname(os.path.realpath(__file__))+"/output/"+parameters['name']+"/results-cutoff-lastmile.csv")
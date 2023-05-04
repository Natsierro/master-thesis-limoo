import pandas as pd
import numpy as np
from tqdm import tqdm
import random

from geopy import distance

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

#Our distance matrix between each node in our space
def distance_matrix(centers, depot):
    dep = pd.DataFrame([[depot[0],depot[1]]], columns=["latitude","longitude"])
 
    dataframe = pd.concat([dep, centers[["latitude","longitude"]]], axis=0)

    d = [[0] * len(dataframe) for _ in range(len(dataframe))]

    for i in range(len(dataframe)):
        for j in range(len(dataframe)):
            if (j!=i and j<i):
                dist = distance.distance((dataframe.iloc[i][0],dataframe.iloc[i][1]), (dataframe.iloc[j][0],dataframe.iloc[j][1])).m
                d[i][j] = dist
                d[j][i] = dist
    return d

#The routing algorithm from Google OR Tools
#The depot is the coordinates given in the scenario
def route(df, depot):
    data = {}
    data['distance_matrix'] = distance_matrix(df, depot)
    data['num_vehicles'] = 1
    data['depot'] = 0
    
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                       data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    solution = routing.SolveWithParameters(search_parameters)
    
    #If there is a solution, we output the order to which to deliver the products for the specific product and return it as a dataframe
    if solution:
        i = 1
        result = pd.DataFrame(0.0, index=np.arange(len(df)), columns=["vrp"])      
        index = routing.Start(0)
        while not routing.IsEnd(index):
            if (manager.IndexToNode(index) == 0):
                index = solution.Value(routing.NextVar(index))
                continue
            else:                
                result.iloc[manager.IndexToNode(index)-1, result.columns.get_loc("vrp")] = float(i)
                i += 1
                index = solution.Value(routing.NextVar(index))
    else:
        result = pd.DataFrame(0.0, index=np.arange(len(df)), columns=["vrp"])
    return result

#The VRP function has the objective to create the community grouping as well as classic vrp based on the scenario and the product
def vrp(product, cluster, depot):
    name = "productID_"+str(product)
    name_vrp = "vrp_productID_"+str(product)
    name_vrp_no_centers = "no_groups_vrp_productID_"+str(product)

    #Based on the probability of purchase, we make deterministic demand with the random.random() function
    for index, row in cluster.iterrows():
        if (random.random() < float(row[name])):
            cluster.iloc[index, cluster.columns.get_loc(name)] = 1
        else:
            cluster.iloc[index, cluster.columns.get_loc(name)] = 0
    
    clusters_participating = cluster.groupby("cluster")[name].sum().replace(0, np.nan).dropna(how='all', axis=0).index.tolist()

    if (len(clusters_participating)!= 0):
        cluster[name_vrp] = 0
        cluster[name_vrp_no_centers] = 0
        centers = cluster.loc[cluster["cluster"].isin(clusters_participating) & (cluster["distance_center"]==0.0)]

        #VRP for the community group buying method. The VRP is done only to the community centers of participating communities
        cluster.loc[centers.index,name_vrp] = route(centers, depot).values.tolist()

        #VRP for the classical method wiht delivery to each node. The VRP is done to all users with a demand of 1
        cluster.loc[cluster[name]==1,name_vrp_no_centers] = route(cluster.loc[cluster[name]==1,:], depot).values.tolist()
        
    else:
        cluster[name_vrp] = 0
        cluster[name_vrp_no_centers] = 0


    return cluster
if __name__ == "__main__":
    local_path_code = "USE YOUR OWN PATH TO THE OUTPUT OF THE SIMULATION"
    local_path_data = "USE YOUR OWN PATH TO THE DATA"
    print("Importing initial data...")

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

    #for each scenario and each product, create the VRP and outputs it to the "populated_products_vrp_cluster.csv" file
    for parameters in scenarios:
        print("Creating vrp for " + parameters['name'])
        depot = (parameters["lat"], parameters["lng"])
        cluster = pd.read_csv(local_path_code+parameters['name']+"/populated_products_cluster.csv", index_col=0)
        products = [x[10:] for x in cluster.columns.values.tolist() if x.startswith('productID_')]

        for product in tqdm(products):
            cluster = vrp(product, cluster, depot)
        cluster.to_csv(local_path_code+parameters['name']+"/populated_products_vrp_cluster.csv")
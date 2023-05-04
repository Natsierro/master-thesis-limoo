import pandas as pd
import numpy as np
from tqdm import tqdm
import gmplot
import random
import os
from geopy import distance

#This function plots the different users as well as the delivery path for the community group buying model
def draw(product, cluster, depot, path):
    apikey = 'YOUR GOOGLE MAPS API KEY' # (your API key here: https://developers.google.com/maps)
    gmap = gmplot.GoogleMapPlotter(depot[0], depot[1], 16, apikey=apikey)

    name = "productID_"+str(product)
    name_vrp = "vrp_productID_"+str(product)

    clusters_participating = cluster.groupby("cluster")[name].sum().replace(0, np.nan).dropna(how='all', axis=0).index.tolist()

    colors = ['aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','cyan','darkblue','darkcyan','darkgoldenrod','darkgreen','darkgrey','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategrey','darkturquoise','darkviolet','deeppink','deepskyblue','dimgrey','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','green','greenyellow','grey','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgray','lightgreen','lightgrey','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategrey','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','slategrey','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
    colors_k = random.sample(colors, len(cluster["cluster"].unique().tolist()))
    
    if (len(clusters_participating)!= 0):        
        X = cluster.loc[cluster["cluster"].isin(clusters_participating) & (cluster[name]!=0),:]
        centers = cluster.loc[cluster["cluster"].isin(clusters_participating) & (cluster[name_vrp]!=0),:]

        
        for index, row in X.iterrows():
            gmap.marker(row['latitude'], row['longitude'], color=colors_k[int(row["cluster"])])
        
        gmap.scatter(centers['latitude'],centers['longitude'], marker = False, symbol = 'x', s=15, ew=6, c = [colors_k[int(x)] for x in centers["cluster"].tolist()])

        gmap.scatter([depot[0]],[depot[1]], marker = False, symbol = 'x', s=25, ew=10, c = 'red')

        gmap.plot([depot[0]]+centers.sort_values(by=name_vrp).loc[:,"latitude"].values.tolist()+[depot[0]], [depot[1]]+centers.sort_values(by=name_vrp).loc[:,"longitude"].values.tolist()+[depot[1]], 'black', edge_width = 10)

    else:
        pass

    # Draw the map to an HTML file:
    gmap.draw(path+'/map_'+product+'.html')
    return True

#This function plots the different users as well as the delivery path for the classic delivery to each individual
def draw_no_group(product, cluster, depot, path):
    apikey = 'YOUR GOOGLE MAPS API KEY' # (your API key here: https://developers.google.com/maps)
    gmap = gmplot.GoogleMapPlotter(depot[0], depot[1], 16, apikey=apikey)

    name = "productID_"+str(product)
    name_vrp = "no_groups_vrp_productID_"+str(product)

    clusters_participating = cluster.groupby("cluster")[name].sum().replace(0, np.nan).dropna(how='all', axis=0).index.tolist()

    colors = ['aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','cyan','darkblue','darkcyan','darkgoldenrod','darkgreen','darkgrey','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategrey','darkturquoise','darkviolet','deeppink','deepskyblue','dimgrey','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','green','greenyellow','grey','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgray','lightgreen','lightgrey','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategrey','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','slategrey','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']
    colors_k = random.sample(colors, len(cluster["cluster"].unique().tolist()))
    
    if (len(clusters_participating)!= 0):        
        X = cluster.loc[cluster["cluster"].isin(clusters_participating) & (cluster[name]!=0),:]
        centers = cluster.loc[cluster["cluster"].isin(clusters_participating) & (cluster[name_vrp]!=0),:]
        
        for index, row in X.iterrows():
            gmap.marker(row['latitude'], row['longitude'], color=colors_k[int(row["cluster"])])

        gmap.scatter([depot[0]],[depot[1]], marker = False, symbol = 'x', s=25, ew=10, c = 'red')

        gmap.plot([depot[0]]+centers.sort_values(by=name_vrp).loc[:,"latitude"].values.tolist()+[depot[0]], [depot[1]]+centers.sort_values(by=name_vrp).loc[:,"longitude"].values.tolist()+[depot[1]], 'black', edge_width = 10)

    else:
        pass

    # Draw the map to an HTML file:
    gmap.draw(path+'/map_no_groups_'+product+'.html')
    return True

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

#Function that takes the users and a specific product and outputs the results to a file with the different distances of community group buying, last mile pickup and classical delivery to each consumer
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
    dataframe = pd.DataFrame(data)
    return dataframe

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

    #We calucalte and output the results of the distances traveled for each scenario and each product.
    for parameters in scenarios:
        print("Creating results for " + parameters['name'])
        depot = (parameters["lat"], parameters["lng"])
        cluster = pd.read_csv(local_path_code+parameters['name']+"/populated_products_vrp_cluster.csv", index_col=0)
        products = [x[10:] for x in cluster.columns.values.tolist() if x.startswith('productID_')]
        
        path = os.path.dirname(os.path.realpath(__file__))+"/output/"+parameters['name']+"/vrp"

        if not os.path.exists(path):
            os.makedirs(path)

        df = pd.DataFrame(columns=["product_id", "location","distance_group", "distance_group_last_mile", "distance_no_group"])
        for product in tqdm(products):
            draw(product, cluster, depot, path)
            draw_no_group(product, cluster, depot, path)

            df2 = results(product, cluster, depot, parameters['name'])
            df = pd.concat([df2, df])
        
        df.to_csv(os.path.dirname(os.path.realpath(__file__))+"/output/"+parameters['name']+"/results.csv")
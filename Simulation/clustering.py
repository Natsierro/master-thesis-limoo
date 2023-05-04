import pandas as pd
import numpy as np

import random
import math
import os
import json
from datetime import datetime
from tqdm import tqdm
from geopy import distance
import gmplot

from k_means_constrained import KMeansConstrained
from kneed import KneeLocator
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import pairwise_distances_argmin_min

#Utility function to translate MN95 geographical data to latitude and longitude
def MN95_to_latlng(E = 2679520.05, N = 1212273.44):

    Y = float(E)/1000000 - 2.6
    X = float(N)/1000000 - 1.2

    l = 2.6779094 + 4.728982 * Y + 0.791484 * Y * X + 0.1306 * Y * np.power(X,2) - 0.0436 * np.power(Y,3)
    p = 16.9023892 + 3.238272 * X - 0.270978 * np.power(Y,2) - 0.002528 * np.power(X,2) - 0.0447 * np.power(Y,2) * X - 0.0140 * np.power(X,3)

    lng = l * 100 / 36
    lat = p * 100 / 36

    return lat, lng

#Utility function to translate latitude and longitude to MN95 geographical data
def latlng_to_MN95(lat = 47.05671263483547, lng = 8.485306671781533):

    p = float(lat) * 0.36 - 16.902866 
    l = float(lng) * 0.36 - 2.67825

    E = 2600072.37 + 211455.93 * l - 10938.51 * l * p - 0.36 * l * np.power(p,2) - 44.54 * np.power(l,3)
    N = 1200147.07 + 308807.95 * p + 3745.25 * np.power(l,2) + 76.63 * np.power(p,2) - 194.56 * np.power(l,2) * p + 119.79 * np.power(p,3)

    return E, N

#The function that takes care of creating the space of users based on the center of the cluster, its size, the housing dataset and the share of housings using the product
def clustering(lat, lng, df, s = 1, share_users = 1):
    # The cluster is defined by its center with the latitude and longitude point, as well as the length of the side of the square in km
    E, N = latlng_to_MN95(lat, lng)

    E_center = int(E/100) * 100
    N_center = int(N/100) * 100

    n = int(np.power(s * 100, 0.5))

    range_E = range(E_center - int(n/2)*100, E_center + (n - int(n/2))*100, 100)
    range_N = range(N_center + (n - int(n/2))*100, N_center - int(n/2)*100, -100)

    cluster = pd.DataFrame(columns=['E_KOORD','N_KOORD', 'latitude', 'longitude'])

    for i in range(n):
        for j in range(n):
            row = df.loc[(df['E_KOORD'] == range_E[i]) & (df['N_KOORD'] == range_N[j])]
            if not(row.empty):                
                for _ in range(int(row['WTOT'])):
                    #In order to randomise the users and also take care of the potential problems with rouding of small numers, the random.random() function is used
                    #Moreover, to not have all users in a ha at the same point, we randomise the E and N coordinates in that specific ha.
                    if random.random() < share_users:
                        E = range_E[i] + random.randint(0,100)
                        N = range_N[j] + random.randint(0,100)
                        lat, lng = MN95_to_latlng(E,N)
                        cluster = pd.concat([pd.DataFrame([[E,N,lat,lng]], columns=cluster.columns), cluster], ignore_index=True)
    return cluster

#Populating the clusters means allocating real Instacart users to the datapoints from the space out of the clustering function
def populate(cluster, users):
    houses = len(cluster.index)

    selected_users = random.sample(users, houses)

    cluster["user_id"] = selected_users

    return cluster

#This is the ML function that takes care of creating the communities or clusters out of the users data
#It takes as the geographical but also preferential data from users to apply a clustering method
#The clustering method is KMeans but it is constrained with the minimum and maximum number of housings per cluster
#Different numbers of clusters, based on the minimum and maximum housings per community are testing
#And using the KneeFunction we find the most optimal number of cluster which is the one that is output.
def communities(populated_cluster, max_housing, min_housing):
    min_clusters = int(math.ceil(len(populated_cluster)/max_housing))
    max_clusters = int(math.ceil(len(populated_cluster)/min_housing))
    range_clusters = range(min_clusters,max_clusters,1)

    X = populated_cluster.loc[:,['latitude','longitude','PCA_1','PCA_2','PCA_3','PCA_4','PCA_5']]
    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(X.to_numpy())
    X = pd.DataFrame(df_scaled, columns=['latitude','longitude','PCA_1','PCA_2','PCA_3','PCA_4','PCA_5'])
    if(len(populated_cluster) < max_housing):
        max_housing = None
    sse = {}
    for k in tqdm(range_clusters):
        clf = KMeansConstrained(n_clusters=k, size_min = min_housing, size_max = max_housing, random_state=0)
        clf.fit_predict(X)

        centers = clf.cluster_centers_
        labels = clf.labels_
        inertia = clf.inertia_
        sse[k] = inertia

    kn = KneeLocator(x=list(sse.keys()), y=list(sse.values()), curve='convex', direction='decreasing')

    clf = KMeansConstrained(n_clusters=kn.knee, size_min = min_housing, size_max = max_housing, random_state=0)
    clf.fit_predict(X)

    centers = clf.cluster_centers_
    closest, _ = pairwise_distances_argmin_min(centers, X)

    labels = clf.labels_

    return closest, labels, kn.knee

#This function draws, thanks to the Google Maps API, the different maps with the users and the clusters.
def draw(lat, lng, populated_cluster, knee, centers, labels, path = ''):
    apikey = 'YOUR GOOGLE MAPS API KEY' # (your API key here: https://developers.google.com/maps)
    gmap = gmplot.GoogleMapPlotter(lat, lng, 16, apikey=apikey)

    colors = ['aliceblue','antiquewhite','aqua','aquamarine','azure','beige','bisque','blanchedalmond','blue','blueviolet','brown','burlywood','cadetblue','chartreuse','chocolate','coral','cornflowerblue','cornsilk','crimson','cyan','darkblue','darkcyan','darkgoldenrod','darkgreen','darkgrey','darkkhaki','darkmagenta','darkolivegreen','darkorange','darkorchid','darkred','darksalmon','darkseagreen','darkslateblue','darkslategrey','darkturquoise','darkviolet','deeppink','deepskyblue','dimgrey','dodgerblue','firebrick','floralwhite','forestgreen','fuchsia','gainsboro','ghostwhite','gold','goldenrod','green','greenyellow','grey','honeydew','hotpink','indianred','indigo','ivory','khaki','lavender','lavenderblush','lawngreen','lemonchiffon','lightblue','lightcoral','lightcyan','lightgoldenrodyellow','lightgray','lightgreen','lightgrey','lightpink','lightsalmon','lightseagreen','lightskyblue','lightslategrey','lightsteelblue','lightyellow','lime','limegreen','linen','magenta','maroon','mediumaquamarine','mediumblue','mediumorchid','mediumpurple','mediumseagreen','mediumslateblue','mediumspringgreen','mediumturquoise','mediumvioletred','midnightblue','mintcream','mistyrose','moccasin','navajowhite','navy','oldlace','olive','olivedrab','orange','orangered','orchid','palegoldenrod','palegreen','paleturquoise','palevioletred','papayawhip','peachpuff','peru','pink','plum','powderblue','purple','red','rosybrown','royalblue','saddlebrown','salmon','sandybrown','seagreen','seashell','sienna','silver','skyblue','slateblue','slategray','slategrey','snow','springgreen','steelblue','tan','teal','thistle','tomato','turquoise','violet','wheat','white','whitesmoke','yellow','yellowgreen']

    colors_k = random.sample(colors, knee)

    X = populated_cluster.loc[:,['latitude','longitude']]
    # Creates the markers for each individual users
    for index, row in X.iterrows():
        gmap.marker(row['latitude'], row['longitude'], color=colors_k[labels[index]])

    # Creates the community centers
    gmap.scatter(X.loc[centers]['latitude'],X.loc[centers]['longitude'], marker = False, symbol = 'x', s=25, ew=6, c = 'black')
    gmap.scatter(X.loc[centers]['latitude'],X.loc[centers]['longitude'], marker = False, symbol = 'x', s=25, ew=4, c = colors_k)

    # Draw the map to an HTML file:
    gmap.draw(path+'map.html')

    return

#Function used as data cleaning and preparation to find the shares of the Aisle parameter in the products history of users
def instacart_data_prep(all_orders, populated_cluster_users):
    aisle_hist = all_orders[all_orders['user_id'].isin(populated_cluster_users)][['user_id','add_to_cart_order','aisle']].groupby(['user_id','aisle']).sum().reset_index()

    user_volume = aisle_hist.groupby('user_id')['add_to_cart_order'].sum()
    user_volume = user_volume.reset_index().rename(columns = {'add_to_cart_order':'volume'})
    aisle_hist = aisle_hist.merge(user_volume, how = 'inner', on = 'user_id')

    aisle_hist['aisle_share'] = aisle_hist['add_to_cart_order'] / aisle_hist['volume']

    aisle_vol_pivot = aisle_hist[['user_id','aisle','add_to_cart_order']].pivot(index = 'user_id', columns = 'aisle', values = 'add_to_cart_order')
    aisle_share_pivot = aisle_hist[['user_id','aisle','aisle_share']].pivot(index = 'user_id', columns = 'aisle', values = 'aisle_share')
    
    aisle_vol_pivot = aisle_vol_pivot.fillna(value = 0)
    aisle_share_pivot = aisle_share_pivot.fillna(value = 0)

    return aisle_share_pivot

#The PCA function has the role to reduce the number of aisle parameters that should be taken into account for the cluster to only the 5 most relevant parameters
#It is a dimension reduction algorithm and more information can be found here: https://www.geeksforgeeks.org/ml-principal-component-analysispca/
def pca(populated_cluster, aisle_share_pivot, weights_PCA = 1):
    pca = PCA(n_components = 30)
    principalComponents = pca.fit_transform(aisle_share_pivot)

    PCA_components = pd.DataFrame(principalComponents)

    for i in range(5):
        populated_cluster['PCA_'+str(i+1)] = PCA_components[i] * weights_PCA

    return populated_cluster

#Finds the maximum distance that a user has to travel to the community center to pick up their groceries.        
def max_distance_to_center(centers, df):
    df["distance_to_center"] = 0
    clusters = df["cluster"].unique().tolist()

    for c in clusters:
        center_lat = df.loc[centers[c]]['latitude']
        center_lng = df.loc[centers[c]]['longitude']
        df["distance_to_center"] = df.apply(lambda x: distance.distance((x['latitude'],x['longitude']), (center_lat,center_lng)).km if x["cluster"] == c else x["distance_to_center"], 1)
    
    return df["distance_to_center"]

#Exporting function to export the results of the algorithm
def export(df, parameters, now = str(datetime.now())):
    path = os.path.dirname(os.path.realpath(__file__))+"/output/"+now+"/"

    if not os.path.exists(path):
        os.makedirs(path)

    df.to_csv(path+"populated_cluster.csv")

    with open(path+'parameters.txt', 'w') as file:
        file.write(json.dumps(parameters))

    return path

if __name__ == "__main__":
    local_path = "USE YOUR OWN PATH TO THE DATA"

    print("Importing initial data...")
    #load geographical data
    housings = pd.read_csv(local_path+"statistics housings/GWS2021.csv", delimiter=";")

    #load instacart data
    path = local_path + 'instacart transactions/'
    aisles = pd.read_csv(path+'aisles.csv')
    departments = pd.read_csv(path+'departments.csv')
    prior = pd.read_csv(path+'order_products__prior.csv')
    train = pd.read_csv(path+'order_products__train.csv')
    orders = pd.read_csv(path+'orders.csv')
    products = pd.read_csv(path+'products.csv')

    orders_products = pd.read_csv(local_path+"instacart transactions/orders_products.csv").sort_values(by="user_id")
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

    for parameters in scenarios:
        #Creating the initial cluster with all the users
        print("Creating initial clusters for " + parameters['name'])
        cluster = clustering(parameters['lat'], parameters['lng'], housings, parameters['size'], parameters['share_users'])

        print("Populating initial clusters...")
        populated_cluster = populate(cluster, users)

        populated_cluster_users = populated_cluster["user_id"].to_list()

        #instacart data preparation
        aisle_share_pivot = instacart_data_prep(all_orders, populated_cluster["user_id"].to_list())

        #Doing pca to reduce the number of components for clustering
        print("PCA reducing the number of components...")
        populated_cluster_pca = pca(populated_cluster.copy(), aisle_share_pivot.loc[populated_cluster["user_id"].to_list()])

        #Doing the clustering and finding the labels, the optimum number of clusters and the centers of clusters
        print("KMeans is starting...")
        centers, labels, knee  = communities(populated_cluster_pca, parameters['max_housing'], parameters['min_housing'])
        populated_cluster['cluster'] = labels

        populated_cluster['distance_center'] = max_distance_to_center(centers, populated_cluster.copy())

        path = export(populated_cluster, parameters, parameters['name'])
        #Drawing the clusters on an HTML file looking like a Google Maps
        draw(parameters['lat'], parameters['lng'], populated_cluster, knee, centers, labels, path)
        print("Done!")
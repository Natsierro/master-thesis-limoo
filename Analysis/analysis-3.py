import pandas as pd
import numpy as np
from geopy import distance

import matplotlib.pyplot as plt

#This function calculates the distances of the VRPs with the depot as an input as well as the list of the stops
def distance_calc(depot, l):
    d = []
    if(len(l)>0):
        d.append(distance.distance((depot[0],depot[1]), (l[0][0],l[0][1])).m)

        for i in range(len(l)-1):
            d.append(distance.distance((l[i][0],l[i][1]),(l[i+1][0],l[i+1][1])).m)
        
        d.append(distance.distance((l[-1][0],l[-1][1]), (depot[0],depot[1])).m)

    return d 

#This function calculates the last mile pickup distance for the specific product being delivered in a specific cluster
def results(product, cluster):
    name_product = "productID_"+str(product)

    distance_group_last_mile = []
    for index, row in cluster.loc[cluster[name_product]!=0].iterrows():
        latitude = cluster.loc[(cluster["cluster"] == row["cluster"]) & (cluster["distance_center"] == 0.0), "latitude"].values
        longitude = cluster.loc[(cluster["cluster"] == row["cluster"]) & (cluster["distance_center"] == 0.0), "longitude"].values
        distance_group_last_mile.append(2 * distance.distance((row["latitude"],row["longitude"]),(latitude,longitude)).m)

    return distance_group_last_mile

if __name__ == "__main__":
    local_path_code = "USE YOUR OWN PATH TO THE OUTPUT OF THE SIMULATION"
    local_path_data = "USE YOUR OWN PATH TO THE DATA"

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

    #In this file we calculate once again differentiating the different scenarios and their densities. We try to understant the impact of the last mile pickup on the sustainabilty of the community group buying model

    #We therefore calculate the different cutoffs in terms of distance and what would be the total distance of delivery, taking into account the last mile pickup, if users were willing to use soft mobility for 100 - 3000 meters
    j = 0
    for parameters in scenarios_city:
        print("Creating results for " + parameters['name'])
        cluster = pd.read_csv(local_path_code+parameters['name']+"/populated_products_vrp_cluster.csv", index_col=0)
        results_cutoff = pd.read_csv(local_path_code+parameters['name']+"/results-cutoff-lastmile.csv", index_col=0)
        products = [x[10:] for x in cluster.columns.values.tolist() if x.startswith('productID_')]
        distances_list_city = []
        cutoff_list_city = []
        for product in products:
            distances_list_city += results(product, cluster)
            distance_no_group = results_cutoff.loc[results_cutoff["product_id"] == int(product), "distance_no_group"].values[0]
            cutoff = range(100,3001,100)
            for i in cutoff:
                x = results_cutoff.loc[(results_cutoff["product_id"] == int(product)), "distance_group_last_mile_cutoff_"+str(i)].values[0]
                if x < distance_no_group:
                    cutoff_list_city.append(i)
                    break

        if(j==0):
            df_cutoffs_city = results_cutoff
        if(j!=0):
            df_cutoffs_city = pd.concat([results_cutoff, df_cutoffs_city])
        j += 1

    j = 0
    for parameters in scenarios_suburbs:
        print("Creating results for " + parameters['name'])
        cluster = pd.read_csv(local_path_code+parameters['name']+"/populated_products_vrp_cluster.csv", index_col=0)
        results_cutoff = pd.read_csv(local_path_code+parameters['name']+"/results-cutoff-lastmile.csv", index_col=0)
        products = [x[10:] for x in cluster.columns.values.tolist() if x.startswith('productID_')]
        distances_list_suburbs = []
        cutoff_list_suburbs = []
        for product in products:
            distances_list_suburbs += results(product, cluster)
            distance_no_group = results_cutoff.loc[results_cutoff["product_id"] == int(product), "distance_no_group"].values[0]
            cutoff = range(100,3001,100)
            for i in cutoff:
                x = results_cutoff.loc[(results_cutoff["product_id"] == int(product)), "distance_group_last_mile_cutoff_"+str(i)].values[0]
                if x < distance_no_group:
                    cutoff_list_suburbs.append(i)
                    break

        if(j==0):
            df_cutoffs_suburbs = results_cutoff
        if(j!=0):
            df_cutoffs_suburbs = pd.concat([results_cutoff, df_cutoffs_suburbs])
        j += 1

    j = 0
    for parameters in scenarios_remote:
        print("Creating results for " + parameters['name'])
        cluster = pd.read_csv(local_path_code+parameters['name']+"/populated_products_vrp_cluster.csv", index_col=0)
        results_cutoff = pd.read_csv(local_path_code+parameters['name']+"/results-cutoff-lastmile.csv", index_col=0)
        products = [x[10:] for x in cluster.columns.values.tolist() if x.startswith('productID_')]
        distances_list_remote = []
        cutoff_list_remote = []
        for product in products:
            distances_list_remote += results(product, cluster)
            distance_no_group = results_cutoff.loc[results_cutoff["product_id"] == int(product), "distance_no_group"].values[0]
            cutoff = range(100,3001,100)
            for i in cutoff:
                x = results_cutoff.loc[(results_cutoff["product_id"] == int(product)), "distance_group_last_mile_cutoff_"+str(i)].values[0]
                if x < distance_no_group:
                    cutoff_list_remote.append(i)
                    break

        if(j==0):
            df_cutoffs_remote = results_cutoff
        if(j!=0):
            df_cutoffs_remote = pd.concat([results_cutoff, df_cutoffs_remote])
        j += 1

    #After calculating the different cutoffs and the distances, we can analyse the results using classic boxplots and histograms
    plt.boxplot([distances_list_city,distances_list_suburbs,distances_list_remote], labels=["City centers","Suburbs","Remote areas"])
    plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    plt.ylabel('meters (m)')
    plt.savefig(local_path_code + "0_analysis/" +'boxplot_last_mile_distances_scenarios.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'boxplot_last_mile_distances_scenarios.png')

    zipped = list(zip(cutoff_list_city, cutoff_list_suburbs, cutoff_list_remote))
    df = pd.DataFrame(zipped, columns=['City centers', 'Suburbs', 'Remote areas'])  
    df[['City centers', 'Suburbs', 'Remote areas']].plot(kind='hist', alpha=0.5, bins=30)
    plt.savefig(local_path_code + "0_analysis/" +'histogram_cutoffs_scenarios.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'histogram_cutoffs_scenarios.png')

    df[['City centers']].plot(kind='hist', bins=30)
    plt.savefig(local_path_code + "0_analysis/" +'histogram_cutoffs_city.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'histogram_cutoffs_city.png')

    df[['Suburbs']].plot(kind='hist', bins=30)
    plt.savefig(local_path_code + "0_analysis/" +'histogram_cutoffs_suburbs.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'histogram_cutoffs_suburbs.png')

    df[['Remote areas']].plot(kind='hist', bins=30)
    plt.savefig(local_path_code + "0_analysis/" +'histogram_cutoffs_remote.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'histogram_cutoffs_remote.png')

    distance_gains_city = []
    distance_gains_suburbs = []
    distance_gains_remote = []

    #We now calculate the different gains of distances for each density type and scenario to further analyse the cufoff impact
    cutoff = range(100,3001,100)
    for i in cutoff:
        distance_gains_city.append(((df_cutoffs_city["distance_group"]+df_cutoffs_city["distance_group_last_mile_cutoff_"+str(i)]-df_cutoffs_city["distance_no_group"])/df_cutoffs_city["distance_no_group"]).mean())
        distance_gains_suburbs.append(((df_cutoffs_suburbs["distance_group"]+df_cutoffs_suburbs["distance_group_last_mile_cutoff_"+str(i)]-df_cutoffs_suburbs["distance_no_group"])/df_cutoffs_suburbs["distance_no_group"]).mean())
        distance_gains_remote.append(((df_cutoffs_remote["distance_group"]+df_cutoffs_remote["distance_group_last_mile_cutoff_"+str(i)]-df_cutoffs_remote["distance_no_group"])/df_cutoffs_remote["distance_no_group"]).mean())

    #We plot multiple boxplots and scatter plots showing the distance gains or losses for the different densities
    plt.clf()
    plt.scatter(range(100,3001,100), [-x for x in distance_gains_city])
    plt.savefig(local_path_code + "0_analysis/" +'savings_cities_cutoffs.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'savings_cities_cutoffs.png')

    plt.clf()
    plt.scatter(range(100,3001,100), [-x for x in distance_gains_city])
    ax = plt.gca()
    ax.set_ylim([0, None])
    plt.savefig(local_path_code + "0_analysis/" +'savings_cities_cutoffs_positive.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'savings_cities_cutoffs_positive.png')

    plt.clf()
    plt.scatter(range(100,3001,100), [-x for x in distance_gains_suburbs])
    plt.savefig(local_path_code + "0_analysis/" +'savings_suburbs_cutoffs.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'savings_suburbs_cutoffs.png')

    plt.clf()
    plt.scatter(range(100,3001,100), [-x for x in distance_gains_suburbs])
    ax = plt.gca()
    ax.set_ylim([0, None])
    plt.savefig(local_path_code + "0_analysis/" +'savings_suburbs_cutoffs_positive.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'savings_suburbs_cutoffs_positive.png')

    plt.clf()
    plt.scatter(range(100,3001,100), [-x for x in distance_gains_remote])
    plt.savefig(local_path_code + "0_analysis/" +'savings_remote_cutoffs.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'savings_remote_cutoffs.png')

    plt.clf()
    plt.scatter(range(100,3001,100), [-x for x in distance_gains_remote])
    ax = plt.gca()
    ax.set_ylim([0, None])
    plt.savefig(local_path_code + "0_analysis/" +'savings_remote_cutoffs_positive.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'savings_remote_cutoffs_positive.png')

    plt.clf()
    plt.plot(range(100,3001,100), [-100*x for x in distance_gains_city], label = "City centers")
    plt.plot(range(100,3001,100), [-100*x for x in distance_gains_suburbs], label = "Suburbs")
    plt.plot(range(100,3001,100), [-100*x for x in distance_gains_remote], label = "Remote areas")
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter())
    plt.xlabel('Maximum distance willingness to use soft mobility or public transports (m)')
    plt.ylabel('Savings (%)')
    plt.legend()
    plt.savefig(local_path_code + "0_analysis/" +'savings_all_cutoffs.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'savings_all_cutoffs.png')

    plt.clf()
    plt.plot(range(100,3001,100), [-100*x for x in distance_gains_city], label = "City centers")
    plt.plot(range(100,3001,100), [-100*x for x in distance_gains_suburbs], label = "Suburbs")
    plt.plot(range(100,3001,100), [-100*x for x in distance_gains_remote], label = "Remote areas")
    ax = plt.gca()
    ax.set_ylim([0, None])
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.ticker.StrMethodFormatter('{x:,.0f}'))
    plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter())
    plt.xlabel('Maximum distance willingness to use soft mobility or public transports (m)')
    plt.ylabel('Savings (%)')
    plt.legend()
    plt.savefig(local_path_code + "0_analysis/" +'savings_all_cutoffs_positive.png',bbox_inches='tight')
    print("Exported: " + local_path_code + "0_analysis/" +'savings_all_cutoffs_positive.png')

    #Here are the dicts of the sustainability gains in percentage based on the different cutoffs of willingness to use soft mobility to travel 
    dict_cities = {list(range(100,3001,100))[i]: -100*distance_gains_city[i] for i in range(len(distance_gains_city))}
    dict_suburbs = {list(range(100,3001,100))[i]: -100*distance_gains_suburbs[i] for i in range(len(distance_gains_suburbs))}
    dict_remote = {list(range(100,3001,100))[i]: -100*distance_gains_remote[i] for i in range(len(distance_gains_remote))}

    print("cities-----------------------------------------------")
    print(dict_cities)

    print("suburbs-----------------------------------------------")
    print(dict_suburbs)

    print("remote-----------------------------------------------")
    print(dict_remote)
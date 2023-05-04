# Simulation
Code used to perform the simulation based on the data in the "Data" folder.

1) The first step is the clustering.py file which takes the raw data and creates, based on the different chosen scenarios, the spaces and communities (clusters) and outputs csv files of these clusters information as well as google maps HTML files to display them.

2) The second step is the products.py file which takes the output of the clustering.py file (the clustered users) and takes random products to simulate the demand of the users for these specific products. It then outputs, for each scenario, a file with the demand (in terms of probability of purchase) of each user for each product.

3) The third step is the vrp.py file which takes the output of product.py file (the demand probability for each product and user in different clusters) and creates the Routing Optimisation for the delivery of those products. Two VRPs (Vehicle Routing Problems) are made, one for the community group buying delivery model, and one for the classical delivery to each individual node. It then outputs, for each scenario, a file with the VRPs of each product (as a list of the order of users to deliver to).

Then the files "results.py" and "results-2.py" calculate different distances used in the analysis to observe the sustainability gains of the different business models
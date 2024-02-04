import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder
from scipy.spatial import distance
import numpy as np
from datetime import time
from datetime import datetime
import requests
import json

restaurant_url = 'http://127.0.0.1:5000/get_restaurants'
response1 = requests.get(restaurant_url)

users_url = 'http://127.0.0.1:5000/get_users?name=Alice'
response2 = requests.get(users_url)

# data_dict = json.loads(response1)
data_dict = response1.json()

restaurants = pd.DataFrame(data_dict['restaurants'])

# data_dict1 = json.loads(response2)
data_dict1 = response2.json()
# print(data_dict1['users'][0])
user_preferences = data_dict1['users'][0]

current_time = datetime.now().time()
open_restaurants = restaurants[(restaurants['start_time'] <= user_preferences['current_time']) & (restaurants['end_time'] > user_preferences['current_time'])]


if open_restaurants.empty:
    print("No restaurants are open at this time.")
    #
else:
    enc = OneHotEncoder()
    restaurant_features = enc.fit_transform(restaurants[['preferred_cuisines', 'budget', 'city', 'state', 'preferred_ambiance', 'dietary_restrictions']]).toarray()

    # Convert user_preferences to DataFrame and transform
    user_preferences_adjusted = {
        'preferred_cuisines': user_preferences['preferred_cuisines'][0],
        'budget': user_preferences['budget'],
        'city': user_preferences['city'],
        'state': user_preferences['state'],
        'preferred_ambiance': user_preferences['preferred_ambiance'],
        'dietary_restrictions': user_preferences['dietary_restrictions'][0]
    }
    user_df_adjusted = pd.DataFrame([user_preferences_adjusted])
    user_features = enc.transform(user_df_adjusted).toarray()

    # Calculate cosine similarity for categorical features
    similarity_scores = cosine_similarity(user_features, restaurant_features[open_restaurants.index])

    # Apply feature importance weights
    for feature, enc_feature in zip(['preferred_cuisines', 'budget', 'city', 'state', 'preferred_ambiance', 'dietary_restrictions'], enc.get_feature_names_out()):
        weight = user_preferences['feature_importance'][feature] / 5  # Normalize weights to be between 0 and 1
        feature_index = np.where(enc_feature == feature)[0]  # Get the column index of the feature
        if feature_index.size > 0:
            similarity_scores[:, feature_index] *= weight

    # Re-normalize the similarity scores
    similarity_scores = similarity_scores / np.max(similarity_scores)

    # Calculate Euclidean distance for coordinates and filter based on a radius
    user_location = np.array(user_preferences['location_preference'])
    restaurant_locations = np.stack(open_restaurants['coordinates'])
    location_distances = distance.cdist([user_location], restaurant_locations, 'euclidean')[0]

    # Normalize distances
    max_distance = np.max(location_distances)
    normalized_distances = location_distances / max_distance

    # Filter based on a radius
    max_radius = 10  # Example radius in km or miles, depending on your coordinate unit
    filtered_restaurants_index = location_distances <= max_radius
    filtered_restaurants = open_restaurants[filtered_restaurants_index]

    # Add similarity score to DataFrame
    filtered_restaurants['similarity_score'] = similarity_scores[0][filtered_restaurants_index]

    # Sort restaurants based on similarity score
    recommended_restaurants = filtered_restaurants.sort_values(by='similarity_score', ascending=False)

    # Display top N recommendations
    N = 3
    print(recommended_restaurants.head(N))

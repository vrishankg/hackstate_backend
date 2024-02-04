from models.User import User
from models.Activities import Activities
from models.Restaurant import Restaurant
from flask import  Flask,redirect, request, url_for, render_template, jsonify
import pymongo
from pymongo import MongoClient

app = Flask(__name__)

uri = "mongodb+srv://ayushlanka106:jQ380711mrAeupZg@cluster0.sxjgrop.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri,connectTimeoutMS=30000, socketTimeoutMS=None, connect=False, maxPoolsize=1)
Auth = client.Auth
users = Auth.Users
restaurants = client.Data.Restaurants
activities = client.Data.Activities

@app.route('/')
def index():
    return 'hi'

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
     if request.method == 'POST':

        username = request.form["username"]
        password = request.form["password"]
        user = users.find_one({"username": username, "password": password})

        if user:
            return "user found"
        else:
            return "user not found"



@app.route('/signup', methods=['POST'])
def signup():
    
    user_data = request.json

    new_user = User(
    id=user_data.get('id'),
    password = user_data.get('password'),
    name=user_data.get('name'),
    preferred_cuisines=user_data.get('preferred_cuisines', []),
    budget=user_data.get('budget'),
    preferred_ambiance=user_data.get('preferred_ambiance'),
    location_preference=user_data.get('location_preference', (0.0, 0.0)),
    dietary_restrictions=user_data.get('dietary_restrictions', []),
    city=user_data.get('city'),
    state=user_data.get('state'),
    preferred_language=user_data.get('preferred_language'),
    current_time = user_data.get('current_time'),
    feature_importance = user_data.get('feature_importance')

)

  
    
    result = users.insert_one(new_user.to_dict())

    print(result)
    return "200"

@app.route('/add_restaurant', methods=['POST'])
def add_restaurant():
    restaurant_data = request.json

    new_restaurant = Restaurant(
    name=restaurant_data.get('name'),
    preferred_cuisines=restaurant_data.get('preferred_cuisines'),
    budget=restaurant_data.get('budget'),
    city=restaurant_data.get('city'),
    state=restaurant_data.get('state'),
    coordinates=restaurant_data.get('coordinates'),
    preferred_ambiance=restaurant_data.get('preferred_ambiance'),
    dietary_restrictions=restaurant_data.get('dietary_restrictions'),
    menu_url=restaurant_data.get('menu_url'),
    start_time=restaurant_data.get('start_time'),
    end_time=restaurant_data.get('end_time')
)

    result = restaurants.insert_one(new_restaurant.to_dict())
    return "200"



@app.route('/add_activities', methods=['POST'])
def add_activities():
    activities_data = request.json
    
    new_event = Activities(
            name=activities_data.get('name'),
            location=activities_data.get('location'),
            date=activities_data.get('date'),
            time=activities_data.get('time'),
            description=activities_data.get('description')
        )

    result = activities.insert_one(new_event.to_dict())
    return "200"

@app.route('/get_restaurants', methods=['GET'])
def get_restaurants():
    try:
        # Query all data from the MongoDB collection
        cursor = restaurants.find({})
        restaurant_data = list(cursor)

        # Convert the data to a list of dictionaries
        restaurants_list = []
        for restaurant in restaurant_data:
            restaurants_list.append({
                'name': restaurant.get('name'),
                'preferred_cuisines': restaurant.get('preferred_cuisines'),
                'budget': restaurant.get('budget'),
                'city': restaurant.get('city'),
                'state': restaurant.get('state'),
                'coordinates': restaurant.get('coordinates'),
                'preferred_ambiance': restaurant.get('preferred_ambiance'),
                'dietary_restrictions': restaurant.get('dietary_restrictions', []),
                'menu_url': restaurant.get('menu_url'),
                'start_time': restaurant.get('start_time'),
                'end_time': restaurant.get('end_time')
            })

        # Return the restaurant data as JSON
        return jsonify({'restaurants': restaurants_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500




@app.route('/get_users', methods=['GET'])
def get_users():
    try:
        # Check if the 'name' parameter is provided in the query string
        search_name = request.args.get('name')

        # Define the query based on whether 'name' parameter is provided
        query = {} if search_name is None else {'name': {'$regex': search_name, '$options': 'i'}}

        # Query data from the MongoDB collection
        cursor = users.find(query)
        user_data = list(cursor)

        # Convert the data to a list of dictionaries
        users_list = []
        for user in user_data:
            users_list.append({
                'id': user.get('id'),
                'password': user.get('password'),
                'name': user.get('name'),
                'preferred_cuisines': user.get('preferred_cuisines', []),
                'budget': user.get('budget'),
                'preferred_ambiance': user.get('preferred_ambiance'),
                'location_preference': user.get('location_preference', (0.0, 0.0)),
                'dietary_restrictions': user.get('dietary_restrictions', []),
                'city': user.get('city'),
                'state': user.get('state'),
                'preferred_language': user.get('preferred_language'),
                'current_time' : user.get('current_time'),
                'feature_importance' : user.get('feature_importance')
            })

        # Return the user data as JSON
        return jsonify({'users': users_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
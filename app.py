import os
import requests


from flask import Flask, g, render_template, request, flash, redirect, session, abort
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError


from models import db, connect_db, User, City, State, Location, Favorite
from forms import UserAddForm, LoginForm, FavoriteForm, AddressForm
from secret import MQ_SECRET_KEY, RM_SECRET_KEY


MQ_API_BASE_URL = "https://www.mapquestapi.com/geocoding/v1"
RM_API_BASE_URL = "https://realty-mole-property-api.p.rapidapi.com/zipCodes"
key_mq = MQ_SECRET_KEY
key_rm = RM_SECRET_KEY

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///moveIn'))


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', "this is wildly unpredictable")
toolbar = DebugToolbarExtension(app)

connect_db(app)


#########################################################################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    maybe_user_id = session.get(CURR_USER_KEY)
    if maybe_user_id is not None:
        g.user = db.session.get(User, maybe_user_id)
    # if CURR_USER_KEY in session:
    #     g.user = db.session.get(User, CURR_USER_KEY)
    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,

            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/search")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/search")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You've logged out of MoveIn.")

    return redirect('/login')

#########################################################################################################################
# Display location on Map via:
# Mapquest API geocoding
# Google Maps API marker


def get_coords(address):
    """Get coordinates from address search."""
    res = requests.get(f"{MQ_API_BASE_URL}/address",
                       params={'key': key_mq, 'location': address})
    data = res.json()
    lat = data['results'][0]['locations'][0]['latLng']['lat']
    lng = data['results'][0]['locations'][0]['latLng']['lng']
    coords = {'lat': lat, 'lng': lng}
    return coords


def get_batch_coords(addresses):
    """Return nested dictionary of coordinates like:
    {
            position: { lat: 34.8791806, lng: -111.8265049 },
            title: "Boynton Pass",
        },
        {
            position: { lat: 34.8559195, lng: -111.7988186 },
            title: "Airport Mesa",
        }
            }
            """

    params = {'key': key_mq}
    params['location'] = addresses
    print(params)
    res = requests.get(f"{MQ_API_BASE_URL}/batch",
                       params=params)
    data = res.json()
    position_dict = {}
    for i in range(len(data['results'])):
        lat_lng_dict = {}
        position_dict[i] = lat_lng_dict
        # {position: [value]}
        for j in range(len(position_dict)):
            lat_lng_dict['lat'] = data['results'][i]['locations'][0]['latLng']['lat']
            lat_lng_dict['lng'] = data['results'][i]['locations'][0]['latLng']['lng']
            # print(f"Position dictionary in get_batch_coords: {position_dict}")
    return position_dict


def get_realty_data(zip_code):
    res = requests.get(f"{RM_API_BASE_URL}/{zip_code}",
                       headers={'X-RapidAPI-Key': key_rm, 'X-RapidAPI-Host': "realty-mole-property-api.p.rapidapi.com", 'Content-Type': 'application/json'})
    print(res)
    if res.ok:
        print('OK!')
        data = res.json()
        return data
    else:
        error_message = flash(
            "Unable to find rental data for that location.", "danger")
        print('Boo!')
        return error_message

    # ENDPOINTS
# ***************************************************************************


@app.route('/')
def initiate():
    return redirect('/search')


@ app.route('/search')
def show_mapping():

    if not g.user:
        flash("Access unauthorized. Please log in.", "danger")
        return redirect("/login")

    form = AddressForm()
    return render_template("address_form.html", form=form)


@ app.route('/api/geocode', methods=["GET", "POST"])
def locate_on_map():
    data = request.json
    print(data)
    address = data['address']
    coords = get_coords(address)
    return coords


@app.route('/api/rental-data', methods=["POST"])
def get_rental_data():
    print(request)
    data = request.json
    print(f"This is /api/rental-data data: {data}")
    zip_code = data['zipcode']
    print(zip_code)
    rental_data = get_realty_data(zip_code)
    if rental_data is None:
        return "error"
    else:
        return rental_data


@ app.route('/adddata', methods=["GET", "POST"])
def save_search_to_db():
    data = request.json
    print(data)

    state = data['state'].capitalize()
    print(state)
    city = data['city'].capitalize()
    address = data['address']
    zipcode = data['zipcode']
    bedrooms = data['bedrooms']

    # add form value for state to DB
    # state_exists = db.session.query(State.name).filter_by(name=state).first()
    state_exists = State.query.filter_by(name=state).first()
    new_state = ""
    if state_exists is None:
        new_state = State(name=state)
        db.session.add(new_state)
        db.session.commit()
        print(f" This is {new_state.name}")
    else:
        # state = state_exists
        print("State already exists in the database.")
    print(new_state)

    # add form value for city to DB
    city_exists = City.query.filter_by(name=city).first()
    new_city = ""
    if city_exists is None:
        if new_state == "":
            state_obj = State.query.filter_by(name=state).first()
        else:
            state_obj = State.query.filter_by(name=new_state.name).first()
        print(state_obj)
        new_city = City(name=city, state_id=state_obj.id)
        db.session.add(new_city)
        db.session.commit()
    else:
        # city = city_exists
        print("City already exists in the database.")
    print(new_city)

    # add location to Db
    location_exists = Location.query.filter_by(street_address=address).first()
    new_location = ""
    if location_exists is None:
        if new_city == "":
            city_obj = City.query.filter_by(name=city).first()
        else:
            city_obj = City.query.filter_by(name=new_city.name).first()
        print(city_obj)
        new_location = Location(street_address=address,
                                zip_code=zipcode, city_id=city_obj.id, bedrooms=bedrooms, user_id=g.user.id)
        db.session.add(new_location)
        db.session.commit()
    else:
        # location = location_exists
        print("Location already exists in database.")
    return data


@app.route('/api/batchgeocode', methods=["GET", "POST"])
def get_favorites_coords():
    addresses = []
    favorites = Favorite.query.all()
    for favorite in favorites:
        location = Location.query.filter_by(id=favorite.location_id).first()
        print(f"This is /api/batchgeocode location matching: {location.id}")
        # location_id = db.session.query(Location.id).filter_by(
        #     id=favorite.location_id).first()
        # location = Location.query.get(location_id)
        address = f"{location.street_address} {location.zip_code}"
        if address not in addresses:
            addresses.append(address)
    print(f"This is the list of addresses in /api/batchgeocode: {addresses}")
    coords = get_batch_coords(addresses)
    return coords


@app.route('/favorites')
def display_favorites():

    if not g.user:
        flash("Access unauthorized. Please log in.", "danger")
        return redirect("/login")

    return render_template("favs_map.html")


@app.route('/favorites/add', methods=["GET", "POST"])
def add_favorites():

    data = request.json
    print(data)

    average = data['average']
    address = data['address']

    location = Location.query.filter_by(street_address=address).first()
    print(f"The location ID for {location.street_address} is {location.id}")
    # IF location_id.id IN favorites.location_id
    favorite_location_id_exists = Favorite.query.filter_by(
        location_id=location.id).first()
    if favorite_location_id_exists is None:
        location_obj = Location.query.filter_by(street_address=address).first()
        print(location_obj)
        new_favorite = Favorite(rent_average=average,
                                user_id=g.user.id, location_id=location_obj.id)
        db.session.add(new_favorite)
        db.session.commit()
    else:
        print("Already a favorite.")
    return render_template('favs_map.html', average=average)


@app.route('/favorites/data')
def get_favorites_data():
    favorites = Favorite.query.all()
    addresses = []
    for favorite in favorites:
        print(favorite)
        location_id = db.session.query(Location.id).filter_by(
            id=favorite.location_id).first()
        location = Location.query.get(location_id)
        rent = favorite.rent_average
        address = f"{location.street_address} {location.zip_code} Bedrooms: {location.bedrooms} Rent: {rent}"
        if address not in addresses:
            addresses.append(address)
    return addresses

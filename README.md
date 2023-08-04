# Move In.

A web application for finding and visualizing rental averages by search area. 

**What it does:**



1. Signup and authentication: Users sign up and their credentials are encrypted and saved to the database. 
2. Search: Users search by address and number of bedrooms for rental averages in that zipcode. Searches are saved to the database. 
3. Map: The search values are used to call the Google Maps API, which displays the address searched for on an interactive map.   
4. Rental Averages: The search values are used to call the Realty Mole API, which will display the rental average for the zipcode and the number of bedrooms. 
5. Save to Favorites: Users are able to save their favorite searches to the database.
6. View Favorites: Users can view a map with markers for each of their Favorites, labeled with the address, number of bedrooms, and the rental average for that zip code. 

**Features:**



1. Limited search area to U.S. states – if a search is out of bounds, the user will be informed that MoveIn is unable to display rental information for that area.
2. Favoriting – Users are able to save and view searches that they want to have on hand. 
3. Encrypted login – bcrypt encryption ensures users’ privacy. 
4. Interactive maps – calling the Google Maps JS API to display searches and favorites allows the user to view the area they are searching about. 

**Tech Stack: **

**	**Python, Flask, Flask-SQLAlchemy, SQLAlchemy, Javascript, JQuery, HTML, CSS, WTForm

**APIs used:** 

MapQuest Geocoding API: [https://www.mapquestapi.com/geocoding/v1](https://www.mapquestapi.com/geocoding/v1)

	Make individual and batch geocoding requests for specific coordinates of addresses.

Realty Mole Rental Data API: [https://realty-mole-property-api.p.rapidapi.com/zipCodes](https://realty-mole-property-api.p.rapidapi.com/zipCodes)

	Make requests for rental averages by zipcode. Returns JSON response with current and historical rental data for zipcode area, organized by number of bedrooms. 

Google Maps Javascript API:

	Used to create both a display map for address search page and a map with custom markers in the ‘/favorites’ endpoint, displaying markers for each ‘Favorite’ saved to the DB.

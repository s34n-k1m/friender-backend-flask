# Friender - Backend Flask

Friender is an app that helps people make friends and connect with others based on geographic proximity and hobbies/interests.  

Frontend and backend repositories were split for deployment. The frontend repository can be found [here](https://github.com/s34n-k1m/friender-frontend-react).

Deployed demo can be seen [here](https://friender.demo.seanmkim.com/).

* Backend built with:
    * Flask
    * Flask WTForms
    * PostgreSQL database
    * SQL Alchemy
    * AWS S3
    * Mapbox
    * Geopy
* Frontend built with:
    * React

# Features:
* Login/authentication
* Users can sign up with: username, email, password, first name, last name, hobbies, interests, location (zip code), and friend radius (in miles)
* Users can edit their profile and optionally upload photos (Images are stored to Amazon S3).
* Users are shown a potential friends list and can like or dislike each potential friend.
* Users are shown other users (name, hobbies, interests, pics) who meet the following criteria:
    1. Other user's location is within friend radius
    2. User's location is within other user's friend radius
    3. User has not yet liked or disliked the other user
    4. User has not been disliked yet by the other user

# Getting Started on the Server-side

1. Clone the [frontend repository](https://github.com/s34n-k1m/friender-frontend-react)  
2. `cd friender-backend-flask`
3. Create the virtual environment
* `python3 -m venv venv`
* `source venv/bin/activate`
* `pip3 install -r requirements.txt`
4. Create the database
* `createdb friender`
* `python3 seed.py`
5. Start the server
* `flask run`

# Getting Started on the Client-side

1. Clone this repository
2. `cd friender-frontend-react`
3. `npm install`
4. `npm start`

# Authors
My pair for this project was @clairelcasey 

# Future Add-ons:
* Add testing
* Messages
    * If two users both say yes for friend match, they should be able to message each other
* Image uploads    
    * Drag and drop file upload
* Add option to see Friends List
    * Unlike already liked person
    * Like already unliked person
* Search by hobbies/interests
* Add map of potential friends
    * Pin on the potential friend's zip code center 
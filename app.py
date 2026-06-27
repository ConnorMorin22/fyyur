#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import psycopg2 as pg
from datetime import datetime
import babel
import dateutil.parser

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(), nullable=True)

    # relationship with Show model
    show = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(), nullable=True)

    # relationship with Show model
    show = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
   __tablename__ = 'Show'
   
   id = db.Column(db.Integer, primary_key=True)
   start_time = db.Column(db.DateTime, nullable=False)
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data= {}

  venues = Venue.query.all()

  for venue in venues:
    if venue.city not in data:
      data[venue.city] = {
          "state": venue.state,
          "venues": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
          }]
        }
      
    else:
      data[venue.city]['venues'].append({
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
          })
  
  data = [{"city": k, "state": v["state"], "venues": v["venues"]} for k, v in data.items()]

  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')
  response = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()

  count = len(response)
  response = {
     "count": count, 
     "data":[{
        "id": v.id, 
        "name": v.name, 
        "num_upcoming_shows": Show.query.filter(Show.venue_id == v.id, 
                                                Show.start_time > datetime.now()).count()
     } for v in response]
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  past_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time < datetime.now()).all()
  upcoming_shows = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).all()

  data = {
     "id": venue.id,
     "name": venue.name,
     "genres": venue.genres.split(",") if venue.genres else [], #check genre layout on frontend 
     "city": venue.city,
     "phone": venue.phone,
     "website": venue.website_link,
     "facebook_link": venue.facebook_link,
     "seeking_talent": venue.seeking_talent,
     "seeking_description": venue.seeking_description, 
     "image_link": venue.image_link,
     "past_shows": [{
        "artist_id": s.artist.id,
        "artist_name": s.artist.name,
        "artist_image_link": s.artist.image_link,
        "start_time": str(s.start_time)
     } for s in past_shows],
     "upcoming_shows": [{
        "artist_id": s.artist.id,
        "artist_name": s.artist.name,
        "artist_image_link": s.artist.image_link,
        "start_time": str(s.start_time)
     } for s in upcoming_shows],
     "past_shows_count": len(past_shows),
     "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  
  error = False
  try: 
     data = Venue(
        name = request.form.get("name"),
        city = request.form.get("city"),
        state = request.form.get("state"),
        address = request.form.get("address"),
        phone = request.form.get("phone"),
        genres = ",".join(request.form.getlist("genres")),
        image_link = request.form.get("image_link"),
        facebook_link = request.form.get("facebook_link"),
        website_link = request.form.get("website_link"),
        seeking_talent = request.form.get("seeking_talent") == 'y',
        seeking_description = request.form.get("seeking_description")
     )
     db.session.add(data)
     db.session.commit()
  except Exception as e:
    print(e)
    error = True
    flash('An error occurred. Venue ' + request.form.get('name', '') + ' could not be listed.')
    db.session.rollback()
  finally:
     db.session.close()
  
  if not error:
    flash(f'Venue ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  venue_to_delete = Venue.query.get(venue_id)
  error = False

  try: 
     db.session.delete(venue_to_delete)
     db.session.commit()
  except Exception as e:
     print(e)
     error = True
     db.session.rollback()
     flash("Venue does not exist")
  finally:
    db.session.close()
  
  if not error:
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artist = Artist.query.all()
  data=[{
     "id": a.id,
     "name": a.name
  } for a in artist]
  
  return render_template('pages/artists.html', artists=data)
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  
  count = len(data)
  response = {
     "count": count,
     "data": [{
        "id": a.id,
        "name": a.name,
        "num_upcoming_shows": Show.query.filter(Show.artist_id == a.id, Show.start_time > datetime.now()).count(),
     } for a in data]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)
  past_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).all()
  upcoming_shows = Show.query.filter(Show.artist_id == artist_id, Show.start_time > datetime.now()).all()

  data = {
     "id": artist.id,
     "name": artist.name,
     "genres": artist.genres.split(",") if artist.genres else [],
     "city": artist.city,
     "state": artist.state,
     "phone": artist.phone,
     "website": artist.website_link,
     "facebook_link": artist.facebook_link,
     "seeking_venue": artist.seeking_venue,
     "seeking_description": artist.seeking_description,
     "image_link": artist.image_link,
     "past_shows": [{
        "venue_id": p.venue.id,
        "venue_name": p.venue.name,
        "venue_image": p.venue.image_link,
        "start_time": str(p.start_time)
     } for p in past_shows],
     "upcoming_shows": [{
        "venue_id": p.venue.id,
        "venue_name": p.venue.name,
        "venue_image": p.venue.image_link,
        "start_time": str(p.start_time)
     } for p in upcoming_shows],
     "past_shows_count": len(past_shows),
     "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  error = False
  try: 
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get("name")
    artist.city = request.form.get("city")
    artist.state = request.form.get("state")
    artist.phone = request.form.get("phone")
    artist.genres = ",".join(request.form.getlist("genres"))
    artist.image_link = request.form.get("image_link")
    artist.facebook_link = request.form.get("facebook_link")
    artist.website_link = request.form.get("website_link")
    artist.seeking_venue = request.form.get("seeking_talent") == 'y'
    artist.seeking_description = request.form.get("seeking_description")
    
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    flash('An error occurred. Artist could not be updated.')
    db.session.rollback()
  finally:
     db.session.close()
  if not error:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  error = False

  try: 
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get("name")
    venue.city = request.form.get("city")
    venue.state = request.form.get("state")
    venue.phone = request.form.get("phone")
    venue.genres = ",".join(request.form.getlist("genres"))
    venue.image_link = request.form.get("image_link")
    venue.facebook_link = request.form.get("facebook_link")
    venue.website_link = request.form.get("website_link")
    venue.seeking_talent = request.form.get("seeking_talent") == 'y'
    venue.seeking_description = request.form.get("seeking_description")
    
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    flash('An error occurred. Artist could not be updated.')
    db.session.rollback()
  finally:
     db.session.close()
  if not error:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  error = False

  try:
    data = Artist(
        name = request.form.get("name"),
        city = request.form.get("city"),
        state = request.form.get("state"),
        phone = request.form.get("phone"),
        genres = ",".join(request.form.getlist("genres")),
        image_link = request.form.get("image_link"),
        facebook_link = request.form.get("facebook_link"),
        website_link = request.form.get("website_link"),
        seeking_venue = request.form.get("seeking_venue") == 'y',
        seeking_description = request.form.get("seeking_description")
     )
    db.session.add(data)
    db.session.commit()
  except Exception as e:
    print(e)
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
  
  if not error:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = Show.query.all()
  data = [{
     "venue_id": s.venue.id,
     "venue_name": s.venue.name,
     "artist_name": s.artist.name,
     "artist_id": s.artist.id,
     "artist_image_link": s.artist.image_link,
     "start_time": str(s.start_time)
  } for s in shows]
  return render_template('pages/shows.html', shows=data)
  

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  
  error = False

  try:
     show = Show(
        artist_id = request.form.get("artist_id"),
        venue_id = request.form.get("venue_id"),
        start_time = request.form.get("start_time")
     )
     db.session.add(show)
     db.session.commit()
     flash('Show was successfully listed!')
  except Exception as e:
     print(e)
     error = True
     db.session.rollback()
     flash('An error occurred. Show could not be listed.')
  finally:
     db.session.close()
  
  if not error:
     return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

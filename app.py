#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migration = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
  __tablename__ = 'show'
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
  start_time = db.Column(db.DateTime)
  artist = db.relationship("Artist", back_populates="venue")
  venue = db.relationship("Venue", back_populates="artist")

  def __repr__(self):
      return f'<Shows {self.venue.name} {self.artist.name} {self.start_time}>'


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    artist = db.relationship('Show', back_populates='venue')

    def __repr__(self):
          return f'<Venue {self.name}>'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    venue = db.relationship('Show', back_populates='artist')

    def __repr__(self):
          return f'<Artist {self.name}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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

  locations = Venue.query.with_entities(Venue.city, Venue.state, func.count(Venue.city)).group_by(Venue.city, Venue.state).all()
  data = []

  for location in locations:
      venues = Venue.query.filter(Venue.city == location[0]).all()
      venues_list = []
      for venue in venues:
          venue_dict = {
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(venue.artist)
          }
          venues_list.append(venue_dict)

      location_dict = {}
      location_dict['city'] = location[0]
      location_dict['state'] = location[1]
      location_dict['venues'] = venues_list
      data.append(location_dict)

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  response = {}
  search_term = request.form['search_term']
  search_query = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()

  data = []
  for result in search_query:
    data_dict = {
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': Show.query.filter(Show.venue_id == result.id).count()
    }
    data.append(data_dict)

  response["count"] = len(search_query)
  response["data"] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  venue = Venue.query.filter(Venue.id == venue_id).one_or_none()
  
  print(datetime.datetime.today())
  if venue is None:
      not_found_error()
  else:
      data = {
          'id': venue.id,
          'name': venue.name,
          'address': venue.address,
          'city': venue.city,
          'state': venue.state,
          'phone': venue.phone,
          'website': venue.website,
          'facebook_link': venue.facebook_link,
          'seeking_talent': venue.seeking_talent,
          'seeking_description': venue.seeking_description,
          'image_link': venue.image_link
      }

  # select all show with venue_id
  show = Show.query.filter(Show.venue_id == venue_id).all()

  # past shows
  past = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.datetime.today())
  past_shows_data = []
  for show in past:
      artist = Artist.query.get(show.artist_id)
      past_dict = {
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M")
      }
      past_shows_data.append(past_dict)

  # upcoming shows
  upcoming = Show.query.filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.datetime.today())
  upcoming_shows_data = []
  for show in upcoming:
      artist = Artist.query.get(show.artist_id)
      upcoming_dict = {
          "artist_id": show.artist_id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M")
      }
      upcoming_shows_data.append(upcoming_dict)

  data["past_shows"] = past_shows_data
  data["upcoming_shows"] = upcoming_shows_data
  data["past_shows_count"] = past.count()
  data["upcoming_shows_count"] = upcoming.count()

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    address = request.form.get('address', '')
    phone = request.form.get('phone', '')
    genres = request.form.get('genres', '')
    facebook_link = request.form.get('facebook_link', '')

    venue = Venue(
      name = name,
      city = city,
      state = state,
      address = address,
      phone = phone,
      genres = genres,
      facebook_link = facebook_link
    )

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)

  try:
    Show.query.filter(Show.venue_id == venue.id).delete()
    venue.delete()
    db.session.commit()
  except:
    db.rollback()
    flash('An error occurred. Venue ' + venue_id + ' could not be deleted.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  data = []
  artists = Artist.query.all()

  for artist in artists:
      artist_dict = {
          "id": artist.id,
          "name": artist.name
      }
      data.append(artist_dict)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  response = {}
  search_term = request.form['search_term']
  search_query = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()

  data = []
  for result in search_query:
      data_dict = {
          'id': result.id,
          'name': result.name,
          'num_upcoming_shows': Show.query.filter(Show.artist_id == result.id).count()
      }
      data.append(data_dict)

  response["count"] = len(search_query)
  response["data"] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  if artist is None:
      not_found_error()
  else:
      data = {
          'id': artist.id,
          'name': artist.name,
          'city': artist.city,
          'state': artist.state,
          'phone': artist.phone,
          'website': artist.website,
          'facebook_link': artist.facebook_link,
          'seeking_venue': artist.seeking_venue,
          'seeking_description': artist.seeking_description,
          'image_link': artist.image_link,
          'genres': ['Rock and Roll']
      }

  # select all show with artist_id
  show = Show.query.filter(Show.artist_id == artist_id).all()

  # past shows
  past = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.datetime.today())
  past_shows_data = []
  for show in past:
      venue = Venue.query.get(show.artist_id)
      past_dict = {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M")
      }
      past_shows_data.append(past_dict)

  # upcoming shows
  upcoming = Show.query.filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.datetime.today())
  upcoming_shows_data = []
  for show in upcoming:
      venue = Venue.query.get(show.venue_id)
      upcoming_dict = {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M")
      }
      upcoming_shows_data.append(upcoming_dict)

  data["past_shows"] = past_shows_data
  data["upcoming_shows"] = upcoming_shows_data
  data["past_shows_count"] = past.count()
  data["upcoming_shows_count"] = upcoming.count()

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    artist = Artist.query.get(artist_id)

    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.address = request.form.get('address', '')
    artist.phone = request.form.get('phone', '')
    artist.genres = request.form.get('genres', '')
    artist.facebook_link = request.form.get('facebook_link', '')

    db.session.commit()
    flash('Successully updated')
  except:
    db.session.rollback()
    flash('There was a problem updating the Artist' + artist.name + ', please try again')
  finally: 
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    venue = Venue.query.get(venue_id)

    venue.name = request.form.get('name', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.address = request.form.get('address', '')
    venue.phone = request.form.get('phone', '')
    venue.genres = request.form.get('genres', '')
    venue.facebook_link = request.form.get('facebook_link', '')

    db.session.commit()
    flash('Sucessfully updated')
  except:
    db.session.rollback()
    flash('There was a problem updating the Artist' + artist.name + ', please try again')
  finally: 
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = request.form.get('genres', '')
    facebook_link = request.form.get('facebook_link', '')
    
    artist = Artist(
      name = name,
      city = city,
      state = state,
      phone = phone,
      gerens = genres,
      facebook_link = facebook_link
    )

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + name + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = []
  for show in shows:
      show_dict = {
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          'artist_image_link': show.artist.image_link,
          "start_time": (show.start_time).strftime("%m/%d/%Y, %H:%M")
      }
      data.append(show_dict)
      
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    artist_id = request.form.get('artist_id')
    venue_id = request.form.get('venue_id')
    start_time = request.form.get('start_time')
    
    show = Show(
      artist_id = artist_id,
      venue_id = venue_id,
      start_time = start_time
    )

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollbakc()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

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

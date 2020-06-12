#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
migrate = Migrate(app, db)
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
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venues', lazy=True)

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
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists', lazy=True)

class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

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
  # get all areas by city and state
  areas = Venue.query.with_entities(Venue.city, Venue.state, func.count(Venue.id)) \
    .group_by(Venue.city, Venue.state).all()

  # format data as needed
  data = []
  current_time = datetime.now()
  for area in areas:
    venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_infor = []
    for venue in venues:
      shows = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time > current_time).all()
      venue_infor.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(shows)
      })
    data.append({
      "city": area.city,
      "state": area.state,
      "venues": venue_infor
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # get all venues based on search_term
  search_term = request.form['search_term']  
  venues = Venue.query.filter(Venue.name.ilike(r'%{}%'.format(search_term))).all()

  # format data as needed
  data = []
  current_time = datetime.now()
  for venue in venues:
    shows = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time > current_time).all()
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(shows)
    })
  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # retrieve venue based on ID
  venue = Venue.query.filter_by(id=venue_id).all()[0]
  # collect past shows
  current_time = datetime.now()
  past_shows_infor = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time < current_time).all()
  # format past shows
  past_shows = []
  for show in past_shows_infor:
    artist = Artist.query.filter_by(id=show.artist_id).all()[0]
    start_time = show.start_time.strftime('%Y-%m-%dT%H:%M:%SZ'); print(start_time)
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": start_time
    })
  # collect upcoming shows
  upcoming_shows_infor = Show.query.filter(Show.venue_id==venue.id).filter(Show.start_time >= current_time).all()
  # format upcoming shows
  upcoming_shows = []
  for show in upcoming_shows_infor:
    artist = Artist.query.filter_by(id=show.artist_id).all()[0]
    start_time = show.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": start_time
    })
  # format data as needed
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
  error = 0
  try:
    # retrieve information from form request
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    genres = ','.join(request.form.getlist('genres'))
    seeking_talent = 'seeking_talent' in request.form and request.form['seeking_talent'] == 'y'
    seeking_description = request.form['seeking_description']

    # check if conflict with Venue in db with same name
    item = Venue.query.filter_by(name=name).all()
    if len(item): error = 1 # Venue already exists!
    else:
      # add it
      item = Venue(name=name, city=city, state=state, address=address, phone=phone,
                  image_link=image_link, facebook_link=facebook_link, website=website,
                  genres=genres, seeking_talent=seeking_talent, seeking_description=seeking_description)
      db.session.add(item)
      db.session.commit()
  except:
    error = 4 # a dummy code for other db errors
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # error handling
  if error == 1:
    flash('An error occurred. Venue ' + request.form['name'] + ' already exists.')
  elif error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  if error:
    return redirect(url_for('create_venue_submission'))
  else:
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  
  error = 0
  try:
    # delete corresponding shows first
    db.session.query(Show).filter(Show.venue_id==venue_id).delete()
    db.session.commit()
    # delete venue based on id
    db.session.query(Venue).filter(Venue.id==venue_id).delete()
    db.session.commit()
  except:
    error = 4
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # error handling
  if error:
    flash('An error occurred. Venue {} could not be deleted.'.format(venue_id))
  else:
    flash('Venue {} was successfully deleted!'.format(venue_id))

  return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():  
  # retrieve all artists
  artists = Artist.query.all()
  # format data as needed
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # retrieve all artists based on search_term
  search_term = request.form['search_term']  
  artists = Artist.query.filter(Artist.name.ilike(r'%{}%'.format(search_term))).all()

  # format data as needed
  data = []
  current_time = datetime.now()
  for artist in artists:
    shows = Show.query.filter(Show.artist_id==artist.id).filter(Show.start_time > current_time).all()
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(shows)
    })
  response={
    "count": len(artists),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # get artist based on ID
  artist = Artist.query.filter_by(id=artist_id).all()[0]
  # collect past shows
  current_time = datetime.now()
  past_shows_infor = Show.query.filter(Show.artist_id==artist.id).filter(Show.start_time < current_time).all()
  # format past shows
  past_shows = []
  for show in past_shows_infor:
    venue = Venue.query.filter_by(id=show.venue_id).all()[0]
    start_time = show.start_time.strftime('%Y-%m-%dT%H:%M:%SZ'); print(start_time)
    past_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": start_time
    })
  # collect upcoming shows
  upcoming_shows_infor = Show.query.filter(Show.artist_id==artist.id).filter(Show.start_time >= current_time).all()
  # format upcoming shows
  upcoming_shows = []
  for show in upcoming_shows_infor:
    venue = Venue.query.filter_by(id=show.venue_id).all()[0]
    start_time = show.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    upcoming_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": start_time
    })
  # format data as needed
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # retrieve artist based on ID
  form = ArtistForm()
  artist=Artist.query.filter_by(id=artist_id).first()
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = 0
  try:
    # retrieve artist based on ID
    item = db.session.query(Artist).filter(Artist.id==artist_id).first()
    # modify its content based on editings
    item.name = request.form['name']
    item.city = request.form['city']
    item.state = request.form['state']
    item.phone = request.form['phone']
    item.facebook_link = request.form['facebook_link']
    item.genres = ','.join(request.form.getlist('genres'))
    item.website = request.form['website']
    item.image_link = request.form['image_link']
    item.seeking_venue = 'seeking_venue' in request.form and request.form['seeking_venue'] == 'y'
    item.seeking_description = request.form['seeking_description']
    # commit the changes
    db.session.commit()
  except:
    error = 4
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # error handling
  if error:
    flash('An error occurred. failed to update Artist ID = {}'.format(artist_id))
  else:
    flash('Artist ID = {} was successfully updated!'.format(artist_id))

  if error:
    return redirect(url_for('create_artist_submission'))
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # retrieve venue based on ID
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = 0
  try:
    # retrieve venue based on ID
    item = db.session.query(Venue).filter(Venue.id==venue_id).first()
    # update its content based on editings
    item.name = request.form['name']
    item.city = request.form['city']
    item.state = request.form['state']
    item.address = request.form['address']
    item.phone = request.form['phone']
    item.image_link = request.form['image_link']
    item.facebook_link = request.form['facebook_link']
    item.website = request.form['website']
    item.genres = ','.join(request.form.getlist('genres'))
    item.seeking_talent = 'seeking_talent' in request.form and request.form['seeking_talent'] == 'y'
    item.seeking_description = request.form['seeking_description']
    # commit the changes
    db.session.commit()
  except:
    error = 4
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # error handling
  if error:
    flash('An error occurred. failed to update Venue ID = {}'.format(venue_id))
  else:
    flash('Venue  ID = {} was successfully updated!'.format(venue_id))

  if error:
    return redirect(url_for('edit_venue_submission'))
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = 0
  try:
    # collect all information about the new artist
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    facebook_link = request.form['facebook_link']
    genres = ','.join(request.form.getlist('genres'))
    website = request.form['website']
    image_link = request.form['image_link']
    seeking_venue = 'seeking_venue' in request.form and request.form['seeking_venue'] == 'y'
    seeking_description = request.form['seeking_description']
    # check if already exist
    item = Artist.query.filter_by(name=name).all()
    if len(item): error = 1 # Artist already exists!
    else:
      # create it in DB
      item = Artist(name=name, city=city, state=state, phone=phone,
                  image_link=image_link, facebook_link=facebook_link, website=website,
                  genres=genres, seeking_venue=seeking_venue, seeking_description=seeking_description)
      db.session.add(item)
      db.session.commit()
  except:
    error = 4
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # error handling
  if error == 1:
    flash('An error occurred. Artist ' + request.form['name'] + ' already exists.')
  elif error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  if error:
    return redirect(url_for('create_artist_submission'))
  else:
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # retrieve all shows from DB
  shows = Show.query.all()

  # format data as needed
  data = []
  for show in shows:
    venue = Venue.query.filter_by(id=show.venue_id).all()[0]
    artist = Artist.query.filter_by(id=show.artist_id).all()[0]
    start_time = show.start_time.strftime('%Y-%m-%dT%H:%M:%SZ'); print(start_time)
    data.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": start_time
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = 0
  try:
    # collect all information about the new show
    start_time = request.form['start_time']
    venue_id = request.form['venue_id']
    artist_id = request.form['artist_id']
    # check if already exist
    item = Show.query.filter_by(start_time=start_time, venue_id=venue_id, artist_id=artist_id).all()
    if len(item): error = 1 # Show already exists!
    else:
      # create it in DB
      item = Show(start_time=start_time, venue_id=venue_id, artist_id=artist_id)
      db.session.add(item)
      db.session.commit()
  except:
    error = 4
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  # error handling
  if error == 1:
    flash('An error occurred. This show already exists.')
  elif error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')

  if error:
    return redirect(url_for('create_show_submission'))
  else:
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

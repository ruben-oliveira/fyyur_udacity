#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from sqlalchemy import exc, func
from sqlalchemy.orm import load_only
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.sql.expression import true
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# Models and DB creation moved to models.py, so the DB needs to be initialized here after imports
db.init_app(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  #
  # To aggregate venues per city, first we get all the venues ordered by city,
  # then we'll be appending each venue to the variable 'venues_by_city' till the next row is for a new city
  # if the next row is a different city then we'll append this 'venues_by_city' and some venue info to 'data'
  # this process is repeated for each city
  venues = Venue.query.order_by('city').all()
  all_upcoming_shows = Venue.query.join(Show).filter(func.date(Show.start_time) >= datetime.now().replace(tzinfo=None))
  venues_lenght = len(venues)
  venues_index = 0
  data = []
  venues_by_city = []
  for venue in venues: 
    venue_num_upcoming_shows = all_upcoming_shows.filter(Venue.id == venue.id).count()
    print("UPCOMING SHOWS: ", venue_num_upcoming_shows, " for id: ", venue.id)
    venues_by_city.append(
      {
        "id" : venue.id,
        "name" : venue.name,
        "num_upcoming_shows": venue_num_upcoming_shows
      }
    )
    if (venues_index+1) < venues_lenght:
      next_venue_city= venues[venues_index+1].city
    else:
      next_venue_city= ''
    if venue.city != next_venue_city:
      data.append(
        {
        "city": venue.city,
        "state": venue.state,
        "venues": venues_by_city
        }
      )
      venues_by_city = []
    venues_index += 1
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #
  # search term formated for an ilike filter
  search = "%{}%".format(request.form['search_term'])
  data = Venue.query.filter(Venue.name.ilike(search))
  response={
    "count": data.count(),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #
  # get the info for the specified venue
  # get all the shows in this venue
  # check if the show' starting time is higher or lower than the current time
  # and add it repectively to a past_shows or upcoming_shows dictionary
  # in the end merge the venue info with the past and upcoming shows info
  data = {}
  past_shows_list = []
  past_shows_count = 0
  upcoming_shows_list = []
  upcoming_shows_count = 0
  venue_ = Venue.query.get(venue_id)
  venue_shows = Show.query.filter(Show.venue_id == venue_id)
  for show in venue_shows:
    if show.start_time < datetime.now().replace(tzinfo=None):
      interface_list = past_shows_list
      past_shows_count+=1
    else:
      interface_list = upcoming_shows_list
      upcoming_shows_count+=1
    interface_list.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })
  data.update(
    venue_.__dict__,
    past_shows = past_shows_list,
    upcoming_shows = upcoming_shows_list,
    past_shows_count = past_shows_count,
    upcoming_shows_count = upcoming_shows_count
  )
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
  error = False
  try:
      form = VenueForm(request.form)
      data = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        website=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data,
      )
      if form.validate():
        db.session.add(data)
        db.session.commit()
      else:
        error = True
  except (exc.SQLAlchemyError, Exception) as e:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed. Errors: ' + str(form.errors))
      return render_template('errors/500.html')
  else:
      # on successful db insert, flash success
      flash('Venue ' + form.name.data + ' was successfully listed!')
      return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except (exc.SQLAlchemyError, Exception) as e:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
      return render_template('errors/500.html')
  else:
      # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully deleted!')
      return render_template('pages/home.html')  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=Artist.query.options(load_only('id', 'name'))
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  #
  # search term formated for an ilike filter
  search = "%{}%".format(request.form['search_term'])
  data = Artist.query.filter(Artist.name.ilike(search))
  response={
    "count": data.count(),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  #
  # get the info for the specified artist
  # get all the artist' shows
  # check if the show' starting time is higher or lower than the current time
  # and add it repectively to a past_shows or upcoming_shows dictionary
  # in the end merge the artist info with the past and upcoming shows info
  data = {}
  past_shows_list = []
  past_shows_count = 0
  upcoming_shows_list = []
  upcoming_shows_count = 0
  artist_ = Artist.query.get(artist_id)
  artist_shows = Show.query.filter(Show.artist_id == artist_id)
  for show in artist_shows:
    if show.start_time < datetime.now().replace(tzinfo=None):
      interface_list = past_shows_list
      past_shows_count+=1
    else:
      interface_list = upcoming_shows_list
      upcoming_shows_count+=1
    interface_list.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    })
  data.update(
    artist_.__dict__,
    past_shows = past_shows_list,
    upcoming_shows = upcoming_shows_list,
    past_shows_count = past_shows_count,
    upcoming_shows_count = upcoming_shows_count
  )
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  #form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artist = Artist.query.get(artist_id)
    form_data = request.form
    for key, value in form_data.items():
      if key == 'seeking_venue':
        value = bool(value)
      setattr(artist, key, value)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
      return render_template('errors/500.html')
  else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully edited!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    venue = Venue.query.get(venue_id)
    form_data = request.form
    for key, value in form_data.items():
      if key == 'seeking_talent':
        value = bool(value)
      #if value != '':
      setattr(venue, key, value)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
      return render_template('errors/500.html')
  else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully edited!')
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
    form = ArtistForm(request.form)
    data = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website=form.website_link.data,
      seeking_venue=form.seeking_venue.data,
      seeking_description=form.seeking_description.data,
    )
    if form.validate():
      db.session.add(data)
      db.session.commit()
    else:
      error = True
  except (exc.SQLAlchemyError, Exception) as e:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + form.name.data + ' could not be created. Errors: ' + str(form.errors))
      return render_template('errors/500.html')
  else:
      # on successful db insert, flash success
      flash('Artist ' + form.name.data + ' was successfully created!')
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  all_shows = Show.query.all()
  data = []
  for show in all_shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })
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
      data = Show(
        artist_id=request.form['artist_id'], 
        venue_id=request.form['venue_id'], 
        start_time=request.form['start_time']
      )
      db.session.add(data)
      db.session.commit()
  except (exc.SQLAlchemyError, Exception) as e:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Show could not be listed.')
      return render_template('errors/500.html')
  else:
      flash('Show was successfully listed!')
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

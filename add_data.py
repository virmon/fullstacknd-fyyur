from app import shows, Artist, Venue, db

venues=[{
    "id": 1,
    "name": "The Musical Hop",
    "address": "1015 Folsom Street",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  },{
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "address": "335 Delancey Street",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"
  },{
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "address": "34 Whiskey Moore Ave",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80"
  }]

artists = [
    {
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"},
    {
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "website": "",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"},
    {   
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "website": "",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"}
]

for v in venues:
    venue = Venue(name=v['name'], address=v['address'], city=v['city'], state=v['state'], phone=v['phone'], website=v['website'], facebook_link=v['facebook_link'], seeking_talent=v['seeking_talent'], image_link=v['image_link'] )
    db.session.add(venue)

i = 1
for a in artists:
    artist = Artist(name=a['name'], city=a['city'], state=a['state'], phone=a['phone'], website=a['website'], seeking_venue=a['seeking_venue'], image_link=a['image_link'] )
    db.session.add(artist)

db.session.commit()

venues = Venue.query.all()
artists = Artist.query.all()

venues[0].artists.append(artists[0])
venues[2].artists.append(artists[1])
venues[2].artists.append(artists[2])
venues[2].artists.append(artists[0])

db.session.add(venues[0])
db.session.add(venues[2])

db.session.commit()
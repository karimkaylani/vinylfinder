import spotipy
import discogs_client
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import random
import requests
import time

NUMBER_OF_ARTISTS = 30
ALBUMS_PER_ARTIST = 1

# referenced spotipy/examples/artist_albums.py
def get_artist_albums(artist, num):
    master = []
    dups = set()
    a_id = artist['id']

    auth_manager = SpotifyClientCredentials()
    spot = spotipy.Spotify(auth_manager=auth_manager)

    try:
        results = spot.artist_albums(a_id, album_type='album,single')
    except:
        return []
    
    master.extend(results['items'])
    while results['next']:
        results = spot.next(results)
        master.extend(results['items'])
    albums = []
    for album in master:
        name = album['name']
        if 'deluxe' in name.lower():
            continue
        if name.lower() not in dups:
            dups.add(name.lower())
            albums.append(album)
    length = min(len(albums), num)
    return albums[:length]

def get_releases(sp, d, page):
    artists = []
    releases = []
    page_factor = page * NUMBER_OF_ARTISTS

    results = sp.current_user_top_artists(limit=page_factor+NUMBER_OF_ARTISTS)
    for item in results['items']:
        artists.append(item)
    
    artists = artists[page_factor:]
    
    seen = set()
    start_time = time.time()

    for artist in artists:
        if time.time() - start_time > 1:
            r = requests.get('http://google.com')
            start_time = time.time()
            print('sent!')
        print(artist['name'])
        albums = get_artist_albums(artist, ALBUMS_PER_ARTIST)
        for album in albums:
            print(album['name'])
            results = d.search(album['name'], type='release', artist=artist['name'], format='vinyl')
            try:
                release = results.page(0)[0]
                print('found master!')
                name = release.title.lower()
                if name not in seen:
                    seen.add(name)
                    releases.append(release)
            except:
                print('failed!')
                continue
    return releases

import spotipy
import discogs_client
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
import random

NUMBER_OF_ARTISTS = 2
ALBUMS_PER_ARTIST = 2

# referenced spotipy/examples/artist_albums.py
def get_artist_albums(sp, artist, num):
    master = []
    dups = set()
    a_id = artist['id']

    try:
        results = sp.artist_albums(a_id, album_type='album,single')
    except:
        return []
    
    master.extend(results['items'])
    while results['next']:
        results = sp.next(results)
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

def get_releases(sp, d):
    artists = []
    releases = []

    results = sp.current_user_top_artists(limit=NUMBER_OF_ARTISTS)
    for item in results['items']:
        artists.append(item)
    
    seen = set()

    for artist in artists:
        print(artist['name'])
        albums = get_artist_albums(sp, artist, ALBUMS_PER_ARTIST)
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
    random.shuffle(releases)
    return releases

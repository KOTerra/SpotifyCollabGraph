import time
import matplotlib.pyplot as plt
import networkx as nx
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import discogs_client
import requests

# tokens
client_credentials_manager = SpotifyClientCredentials(client_id='9a324ce2de004464916503c99da4c2f2',
                                                      client_secret='6855817946bf4204b187537c4c47dd70')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
discogs = discogs_client.Client('ExampleApplication/0.1', user_token='caNEgSDjmfRnyvXcZKRUfhLgSZcZnvgsYJdzCGLM')

playlist_id = '1ssL2ME8jwjHRVKf7Cnbur'

artist_bands = {}


def discogs_test():
    artist_name = "Magna Carta Cartel"
    results = discogs.search(artist_name, type="artist")

    if results:
        band = results[0]
        print(f"Band: {band.name}, ID: {band.id}")
    else:
        print("No results found.")
        exit()

    artist = discogs.artist(band.id)
    print("Members:", [member.name for member in artist.members])

    release = artist.releases.page(0)[1]
    year = f" ({release.year})" if hasattr(release, 'year') and release.year else ""
    print(f"Release: {release.title} {year}")

    print("Tracks:")
    for track in release.tracklist:
        print(f"- {track.title}")


# Function to check Discogs rate limit and handle rate-limiting errors
def check_discogs_rate_limit():
    # Perform a dummy API call to check the rate limits
    response = requests.get("https://api.discogs.com/", headers={'User-Agent': 'Your-Unique-App/1.0'})

    # Check for rate limiting headers
    rate_limit_remaining = int(response.headers.get('X-Discogs-Ratelimit-Remaining', 1))
    rate_limit_reset = int(response.headers.get('X-Discogs-Ratelimit-Reset', time.time() + 60))

    if rate_limit_remaining == 0:
        reset_time = rate_limit_reset - time.time()
        print(f"Discogs rate limit reached. Sleeping for {reset_time + 5} seconds...")
        time.sleep(reset_time + 5)  # Sleep until rate limit is reset


def get_band_members(band_name_str):
    check_discogs_rate_limit()

    results = discogs.search(band_name_str, type="artist")

    if results:
        band = results[0]
    else:
        return None

    artist = discogs.artist(band.id)
    return artist.members


def make_band_member_connection(artist_name):
    band_memberships = artist_bands.get(artist_name)

    for band in band_memberships:
        add_band_to_artist(artist_name, band)


def add_band_to_artist(artist_name, band_name):
    if artist_name not in artist_bands:
        artist_bands[artist_name] = []
    if band_name not in artist_bands[artist_name]:
        artist_bands[artist_name].append(band_name)


def get_playlist_tracks(playlist_id):
    tracks = []
    results = sp.playlist_items(playlist_id)
    for item in results['items']:
        track = item['track']
        artists = [artist['name'] for artist in track['artists']]
        tracks.append({'name': track['name'], 'artists': artists})
    return tracks


def construct_graph_from_playlist(playlist_id):
    G = nx.Graph()
    tracks = get_playlist_tracks(playlist_id)

    #add all artists as nodes
    for track in tracks:
        artists = track['artists']
        for artist in artists:
            if artist not in G:
                G.add_node(artist)

                #get the bands of the artist from Discogs and add edges between the artist and their bands
                band_memberships = get_band_members(artist)
                if band_memberships:
                    for member in band_memberships:
                        if member.name not in G:
                            G.add_node(member.name)
                        G.add_edge(artist, member.name)
                        print(f"  {member.name} --in--> {artist} ")

    for track in tracks:
        artists = track['artists']
        for i in range(len(artists)):
            for j in range(i + 1, len(artists)):
                G.add_edge(artists[i], artists[j], song=track['name'])
                print(f"{artists[i]} --with--> {artists[j]}")

    return G


def export_graph(G, filename):
    nx.write_graphml(G, filename)


def visualize_graph(G):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=2, iterations=50)
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=5, font_weight='bold')
    plt.title('Artist Collaborations')
    plt.show()


if __name__ == '__main__':
    discogs_test()

    G = construct_graph_from_playlist(playlist_id)

    export_graph(G, 'collaboration_graph_from_playlist.graphml')

    visualize_graph(G)

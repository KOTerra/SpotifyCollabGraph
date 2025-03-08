import time
import os
import matplotlib.pyplot as plt
import networkx as nx
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import discogs_client
import requests

# API tokens
client_credentials_manager = SpotifyClientCredentials(client_id='9a324ce2de004464916503c99da4c2f2',
                                                      client_secret='6855817946bf4204b187537c4c47dd70')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
discogs = discogs_client.Client('ExampleApplication/0.1', user_token='caNEgSDjmfRnyvXcZKRUfhLgSZcZnvgsYJdzCGLM')

playlist_id = '1ssL2ME8jwjHRVKf7Cnbur'

GRAPH_FILE = 'collaboration_graph_from_playlist.graphml'

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


def check_discogs_rate_limit():
    response = requests.get("https://api.discogs.com/", headers={'User-Agent': 'Your-Unique-App/1.0'})

    rate_limit_remaining = int(response.headers.get('X-Discogs-Ratelimit-Remaining', 1))
    rate_limit_reset = int(response.headers.get('X-Discogs-Ratelimit-Reset', time.time() + 60))

    if rate_limit_remaining == 0:
        reset_time = rate_limit_reset - time.time()
        print(f"Discogs rate limit reached. Sleeping for {reset_time + 5} seconds...")
        time.sleep(reset_time + 5)


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


def load_graph_from_file(filename):
    if os.path.exists(filename):
        return nx.read_graphml(filename)
    else:
        return nx.Graph()


def construct_graph_from_playlist(playlist_id, G):
    tracks = get_playlist_tracks(playlist_id)

    for track in tracks:
        artists = track['artists']
        for artist in artists:
            if artist not in G:
                G.add_node(artist)

                band_memberships = get_band_members(artist)
                if band_memberships:
                    for member in band_memberships:
                        if member.name not in G:
                            G.add_node(member.name)
                        G.add_edge(artist, member.name, type="band_member")  # Mark band edges
                        print(f"  {member.name} --in--> {artist} (band member)")

    for track in tracks:
        artists = track['artists']
        for i in range(len(artists)):
            for j in range(i + 1, len(artists)):
                if not G.has_edge(artists[i], artists[j]):
                    G.add_edge(artists[i], artists[j], song=track['name'], type="collab")
                    print(f"{artists[i]} --with--> {artists[j]} (collaboration)")

    return G


def clean_removed_artists(G, playlist_tracks):
    """Removes artists and bands that are no longer in the playlist, while preserving valid connections."""

    playlist_artists = {artist for track in playlist_tracks for artist in track["artists"]}

    graph_artists = set(G.nodes)

    band_members = {}  # band -> set(members)
    member_bands = {}  # member -> set(bands)

    for artist in graph_artists:
        for neighbor, data in G[artist].items():
            if data.get("type") == "band_member":
                band_members.setdefault(artist, set()).add(neighbor)
                member_bands.setdefault(neighbor, set()).add(artist)

    artist_has_playlist_collab = {artist: False for artist in graph_artists}

    for artist in graph_artists:
        for neighbor, data in G[artist].items():
            if data.get("type") == "collab" and neighbor in playlist_artists:
                artist_has_playlist_collab[artist] = True

    artists_with_solo_songs = set()
    for track in playlist_tracks:
        if len(track["artists"]) == 1:
            artists_with_solo_songs.add(track["artists"][0])

    bands_to_keep = set()
    for band, members in band_members.items():
        if (
                band in playlist_artists
                or artist_has_playlist_collab[band]
                or any(member in artists_with_solo_songs for member in members)
                or any(artist_has_playlist_collab[member] for member in members)
        ):
            bands_to_keep.add(band)

    artists_to_keep = set(playlist_artists) | artists_with_solo_songs

    for artist in graph_artists:
        if artist in member_bands and member_bands[artist] & bands_to_keep:
            artists_to_keep.add(artist)

        if artist_has_playlist_collab[artist]:
            artists_to_keep.add(artist)

    for artist in list(graph_artists - artists_to_keep):
        print(f"Removing {artist} (no playlist songs, no playlist-linked collabs, no band-linked collabs)")
        G.remove_node(artist)

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

    G = load_graph_from_file(GRAPH_FILE)

    G = construct_graph_from_playlist(playlist_id, G)

    G = clean_removed_artists(G, get_playlist_tracks(playlist_id))

    export_graph(G, GRAPH_FILE)

    visualize_graph(G)

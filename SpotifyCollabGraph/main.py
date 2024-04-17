import networkx as nx
import spotipy
import matplotlib.pyplot as plt
from spotipy.oauth2 import SpotifyClientCredentials

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id='9a324ce2de004464916503c99da4c2f2',
                                                      client_secret='6855817946bf4204b187537c4c47dd70')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# Function to retrieve tracks from a playlist
def get_playlist_tracks(playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    for item in results['items']:
        track = item['track']
        artists = [artist['name'] for artist in track['artists']]
        tracks.append({'name': track['name'], 'artists': artists})
    return tracks


# Function to construct the collaboration graph from a playlist
def construct_graph_from_playlist(playlist_id):
    G = nx.Graph()
    tracks = get_playlist_tracks(playlist_id)

    # Add all artists as nodes
    for track in tracks:
        artists = track['artists']
        for artist in artists:
            if artist not in G:
                G.add_node(artist)

    # Add edges between artists
    for track in tracks:
        artists = track['artists']
        for i in range(len(artists)):
            for j in range(i + 1, len(artists)):
                G.add_edge(artists[i], artists[j], song=track['name'])
    return G


# Function to export graph in a format suitable for drawing
def export_graph(G, filename):
    nx.write_graphml(G, filename)


# Function to visualize the graph
def visualize_graph(G):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=2, iterations=50)  # Layout algorithm
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='skyblue', font_size=5, font_weight='bold')
    plt.title('Artist Collaborations')
    plt.show()


if __name__ == '__main__':
    playlist_id = '1ssL2ME8jwjHRVKf7Cnbur'

    G = construct_graph_from_playlist(playlist_id)

    export_graph(G, 'collaboration_graph_from_playlist.graphml')

    visualize_graph(G)

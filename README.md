# SpotifyCollabGraph
Goal is to create a knowledge graph to serve a recommendation engine of all musicians that exist on every streaming platform, where connections in the graph database represent a "artist WORKED WITH artist" or "artist MEMBER OF artist" in the case of bands and also having semantic embeddings on nodes for ML integration (link prediction, community detection etc.)

Currently the project can retrieve this information from songs on a spotify playlist and load it in a remote neo4j database. 
411 artist nodes on example playlist (https://open.spotify.com/playlist/1ssL2ME8jwjHRVKf7Cnbur) with 71 songs.
Target is around 20 million artists.

It will build upon streaming platforms API and publically available databases such as musicbrainz and discogs, while also having the capability to periodically update itself with new music releases.

Currently used tech stack:
- python
- neo4j
- spotify/discogs API
- oracle cloud interface
- tailscale
- docker

BASE_URL = "https://www.jiosaavn.com/api.php"

COMMON = "&_format=json&_marker=0&api_version=4&cc=in"

SEARCH              = BASE_URL + "?__call=search.getResults"                   + COMMON + "&q="
SEARCH_SONGS        = BASE_URL + "?__call=search.getResults"                   + COMMON + "&q="
SEARCH_ALBUMS       = BASE_URL + "?__call=search.getAlbumResults"              + COMMON + "&q="
SEARCH_ARTISTS      = BASE_URL + "?__call=search.getArtistResults"             + COMMON + "&q="
SEARCH_PLAYLISTS    = BASE_URL + "?__call=search.getPlaylistResults"           + COMMON + "&q="
SEARCH_ALL          = BASE_URL + "?__call=search.getResults"                   + COMMON + "&q="

SONG                = BASE_URL + "?__call=song.getDetails"                     + COMMON + "&pids="
ALBUM               = BASE_URL + "?__call=content.getAlbumDetails"             + COMMON + "&albumid="
PLAYLIST            = BASE_URL + "?__call=playlist.getDetails"                 + COMMON + "&listid="
LYRICS              = BASE_URL + "?__call=lyrics.getLyrics"                    + COMMON + "&lyrics_id="

# Artist — note: parameter is "artistId" (capital I), not "artistid"
ARTIST_BY_ID        = BASE_URL + "?__call=artist.getArtistPageDetails"         + COMMON + "&artistId="
ARTIST_TOP_SONGS    = BASE_URL + "?__call=artist.getArtistMoreSong"            + COMMON + "&artistId="
ARTIST_TOP_ALBUMS   = BASE_URL + "?__call=artist.getArtistMoreAlbum"          + COMMON + "&artistId="

# Suggestions — returns {song_id: [...songs...]} dict
SUGGESTIONS         = BASE_URL + "?__call=reco.getreco"                        + COMMON + "&pid="

# Launch data — single endpoint that contains trending, charts, new_albums, top_playlists
LAUNCH_DATA         = BASE_URL + "?__call=webapi.getLaunchData"                + COMMON

# Radio — two-step: create station, then get songs
RADIO_CREATE        = BASE_URL + "?__call=webradio.createEntityStation"        + COMMON
RADIO_SONGS         = BASE_URL + "?__call=webradio.getSong"                    + COMMON

# URL token resolver — resolves a jiosaavn.com share URL to structured data
RESOLVE             = BASE_URL + "?__call=webapi.get"                          + COMMON

# Top searches / browse modules
TOP_SEARCHES        = BASE_URL + "?__call=content.getTopSearches"              + COMMON

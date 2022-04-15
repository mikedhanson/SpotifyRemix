import json
import datetime
import requests
import spotipy
import discord
from spotipy.oauth2 import SpotifyOAuth

DeemixEmailAddress = ''
DeemixPassword = ''
DEEMIX_URI = 'http://server:port'
Spotify_CLIENT_ID = ''
Spotify_CLIENT_SECRET = ''
Spotify_REDIRECT_URI = 'http://localhost:3000'
DiscordBotToken = '' 
Discord_Channel = ''
SpotifyURL = "https://open.spotify.com/playlist/"

client = discord.Client()

Creds = {
    'email': DeemixEmailAddress,
    'pass': DeemixPassword, 
}


@client.event
async def DiscordNotify(RawData):

    await client.wait_until_ready()
    channel = client.get_channel(int(Discord_Channel))  # channel id

    Data = {
        "Number Of Tracks": RawData['NUMBER_OF_TRACKS'],
        "Playlist": RawData['SPOTIFY_PLAYLIST'],
    }

    # each item to new line as a string
    format_msg = '\n'.join( [f'{key}: {value}' for key, value in Data.items()])

    embedVar = discord.Embed(title="Demix Spotify Companion", color=0x00ff00)
    embedVar.add_field(name="Details", value=format_msg, inline=False)
    embedVar.description = "DeeSpot started downloading new tracks"
    await channel.send(embed=embedVar)

    print(f'Bot disconecting... {client.user}')
    await client.close()


@client.event
async def on_ready():
    print(f'Bot connected as {client.user}')
    print("bot_name:", client.user.name, "User_id:", client.user.id)
    print("Bot ready")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    open_browser = False,
    client_id = Spotify_CLIENT_ID,
    client_secret = Spotify_CLIENT_SECRET,
    redirect_uri = Spotify_REDIRECT_URI,
    scope = "user-library-read, playlist-modify-private, playlist-read-private, playlist-modify-public"
)
)

# auth to deemix
def deemix(Creds, SpotifyPlaylist):
    SESSION = requests.session()  # Create new session
    url = DEEMIX_URI+'/api/loginEmail'
    payload = json.dumps({
        "email": Creds['email'],
        "password": Creds['pass'],
        "accessToken": ""
    })
    headers = {'Content-Type': 'application/json'}
    response = SESSION.request(
        "POST", url, headers=headers, data=payload).json()
    # Use SESSION  to login with ARL
    url = DEEMIX_URI+'/api/loginArl'
    payload = json.dumps({
        "arl": response['arl'],
        "force": False,
        "child": 0
    })
    headers = {'Content-Type': 'application/json'}
    response = SESSION.request(
        "POST", url, headers=headers, data=payload).json()

    # removeFinishedDownloads
    url = DEEMIX_URI+"/api/removeFinishedDownloads"
    payload = json.dumps({
        "arl": '',
        "force": False,
        "child": 0
    })
    headers = {
        'Authorization': "Bearer " + response['arl'],
        'Content-Type': 'application/json'
    }
    clear = requests.request(
        "POST", url, headers=headers, data=payload).json()
    print(f"Deemix - Clearing downloads...{clear}")

    # ADD spot link to queue
    url = DEEMIX_URI + "/api/addToQueue"
    payload = json.dumps({
        "arl": response['arl'],
        "url": SpotifyPlaylist,
        "bitrate": None
    })
    headers = {
        'Authorization': "Bearer " + response['arl'],
        'Content-Type': 'application/json'
    }
    response = SESSION.request(
        "POST", url, headers=headers, data=payload).json()
    if(response['result'] == False):
        print(
            f"Failed to add {SpotifyPlaylist} to {url} Error: {response['errid']}")
        exit
    print(f"Adding playlist to deemix {response}")

    # logout
    SESSION.request("POST", DEEMIX_URI+'/api/logout').json()

    return response


def deemixSettings():
    url = DEEMIX_URI + "/api/getsettings"
    response = requests.request("GET", url).json()
    return response

# returns a list of objects containing all users liked songs
def UsersLikedSong(results):
    tracksArray = []
    while results:
        for i, track in enumerate(results['items']):
            tracksArray.append(track)
        if results['next']:
            results = sp.next(results)
        else:
            results = None

    return tracksArray

# Create new spotify playlist (temp)
def NewPlaylist():
    PlaylistTmpName = "tmp_"+datetime.datetime.now().strftime("%m/%d/%Y")
    NewPlaylist = sp.user_playlist_create(
        sp.me()['id'], PlaylistTmpName, public=True, collaborative=False, description='temp playlist')

    if(NewPlaylist):
        print(f"Newplaylist ID: {NewPlaylist['id']}")
        return NewPlaylist['id']
    else:
        print("Failed to create new playlist")


def DeleteOldPlaylists(id):
    print(f"Deleting playlist: {id}")
    sp.current_user_unfollow_playlist(id)


def main():

    SpotPlaylistID = NewPlaylist()
    SpotifyPlaylist = "https://open.spotify.com/playlist/" + SpotPlaylistID 
    
    Tracks = sp.current_user_saved_tracks(limit=50, offset=0, market='US')
    AllLikedTracks = UsersLikedSong(Tracks)

    for item in AllLikedTracks: #Tracks['items']: #AllLikedTracks: #tracks['items']:
        track = item['track']
        print(f"Adding {track['id'], track['name']} to {SpotPlaylistID}")
        sp.playlist_add_items(SpotPlaylistID, [track['uri']])

    deemix(Creds, SpotifyPlaylist)

    DeemixSettings = deemixSettings()


    print("Starting...: " +
          '\n SpotifyPlaylist     :: %s' % SpotifyPlaylist +
          '\n DEEMIX_URI          :: %s' % DEEMIX_URI + 
          '\n Number of tracks    :: %s' % {len(AllLikedTracks)}
          )

    DeleteOldPlaylists(SpotPlaylistID)

    Data = {
        "NUMBER_OF_TRACKS": {len(AllLikedTracks)},
        "SPOTIFY_PLAYLIST": SpotifyPlaylist,

        "DOWNLOAD_LOCATION": DeemixSettings['settings']['downloadLocation'],
        "DEEMIX_URI": DEEMIX_URI
    }

 
    client.loop.create_task(DiscordNotify(Data))
    client.run(DiscordBotToken)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(0)

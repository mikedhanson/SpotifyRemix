# SpotifyRemix
Spotify Deemix automation 

-- Use at your own risk -- 

## Requirements 
discord | requests | spotipy

You need to create a developer account for spotify and create an app. 

## How does it work? 

Creates a temp spotify playlist and moves all users liked music to that playlist. 

## Usage

Variables that can be passed to docker img. 
```python
DeemixEmailAddress = ''
DeemixPassword = ''
DEEMIX_URI = 'http://server:port'
Spotify_CLIENT_ID = ''
Spotify_CLIENT_SECRET = ''
Spotify_REDIRECT_URI = 'http://localhost:3000'
DiscordBotToken = '' 
Discord_Channel = ''
SpotifyURL = "https://open.spotify.com/playlist/"
```

## Example 

```bash 

docker run -it --rm -p 3001:3000 -e DeemixEmailAddress="" -e DeemixPassword='' -e DEEMIX_URI="" -e Spotify_CLIENT_ID='' -e Spotify_CLIENT_SECRET='' -e DiscordBotToken='' -e Discord_Channel='' docker_img_name

```
## Build the docker image

```bash 
docker build -t mike/SpotifyRemix .
```

## Run the docker image

```bash 
docker run -it --rm -p 3001:3000 mike/SpotifyRemix
```

## Get docker here 
https://docs.docker.com/get-docker/

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
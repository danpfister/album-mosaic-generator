import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import requests

def get_credentials():
    try:
        data = json.load(open(r'./credentials.json', 'r'))
        return data["username"], data['client-id'], data['client-secret']
    except:
        print(f"reading secret.json failed")
        raise
    
def test_get_image(top_tracks: json):
    unique_album_ids = set()
    for count, item in enumerate(top_tracks['items']):
        if item['album']['id'] in unique_album_ids:
            continue
        unique_album_ids.add(item['album']['id'])
        image_path = item['album']['images'][2]['url']
        image = requests.get(image_path, stream=True)
        file = open(f'./images/test_image{count}.jpg', 'wb')
        file.write(image.content)
        file.close()
    

if __name__ == "__main__":
    USERNAME, CLIENT_ID, CLIENT_SECRET = get_credentials()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri="https://github.com/danpfister",
                                                   scope="user-top-read"))
    
    IMG_COUNT = 10
    top_tracks = sp.current_user_top_tracks(limit=IMG_COUNT)
    test_get_image(top_tracks)
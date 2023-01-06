import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import requests
import cv2 as cv
import numpy as np

def get_credentials():
    try:
        data = json.load(open(r'./credentials.json', 'r'))
        return data["username"], data['client-id'], data['client-secret']
    except:
        print(f"reading credentials.json failed")
        raise
    
def save_image(url, path):
    image = requests.get(url, stream=True)
    file = open(path, 'wb')
    file.write(image.content)
    file.close()
    
def test_get_image(top_tracks: json):
    unique_album_ids = set()
    item = top_tracks['items'][6]
    unique_album_ids.add(item['album']['id'])
    image_path = item['album']['images'][2]['url']
    save_image(image_path, f'./images/test_image{0}.jpg')
    
def get_dominant_colour():
    image = cv.imread('./images/test_image0.jpg')
    image = image.reshape((-1, 3))
    image = np.float32(image)
    
    criteria = (cv.TermCriteria_EPS + cv.TermCriteria_MAX_ITER, 10, 1.0)
    flags = cv.KMEANS_RANDOM_CENTERS
    K = 8
    _, labels, palette = cv.kmeans(image, K, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    
    r, g, b = palette[np.argmax(counts)]
    print(f"the perceived brightness is {0.21*r + 0.72*g + 0.07*b}")
    
if __name__ == "__main__":
    USERNAME, CLIENT_ID, CLIENT_SECRET = get_credentials()
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri="https://github.com/danpfister",
                                                   scope="user-top-read"))
    
    IMG_COUNT = 10
    top_tracks = sp.current_user_top_tracks(limit=IMG_COUNT)
    test_get_image(top_tracks)
    get_dominant_colour()
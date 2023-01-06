import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import requests
import cv2 as cv
import numpy as np
import argparse

class Album:
    def __init__(self, album, path) -> None:
        self.name = album['name']
        self.id = album['id']
        self.path = path
        self.color = self.get_dominant_color()
        self.luminance = self.get_luminance()
        
    def __repr__(self) -> str:
        return f"{self.name} with luminance {self.luminance}"
            
    def get_dominant_color(self):
        image = cv.imread(self.path)
        image = image.reshape((-1, 3))
        image = np.float32(image)
        
        criteria = (cv.TermCriteria_EPS + cv.TermCriteria_MAX_ITER, 10, 1.0)
        flags = cv.KMEANS_RANDOM_CENTERS
        K = 8
        _, labels, palette = cv.kmeans(image, K, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)
        
        return palette[np.argmax(counts)]
        
    def get_luminance(self):
        r, g, b = self.color
        return 0.213*r + 0.715*g + 0.072*b

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
    
def get_album_covers(spotify: spotipy.Spotify, IMG_COUNT: int, TIME_RANGE):
    unique_album_ids = set()
    albums = list()
    offset = 0
    index = 0
    while len(unique_album_ids) < IMG_COUNT:
        top_tracks = spotify.current_user_top_tracks(limit=1, offset=offset, time_range=TIME_RANGE)
        offset += 1
        if len(top_tracks['items']) == 0:
            raise Exception("reached album limit")
        album = top_tracks['items'][0]['album']
        if album['id'] in unique_album_ids:
            print(f"skipped album {album['name']} (duplicate)")
            continue
        unique_album_ids.add(album['id'])
        image_path = album['images'][2]['url'] # take 64x64 album cover (other options are 300x300 and 640x640)
        print(f"saved album {album['name']}")
        save_image(image_path, f'./images/album_image_{index}.jpg')
        albums.append(Album(album, f'./images/album_image_{index}.jpg'))
        index += 1
    return albums
    
def create_image(albums: list, SIZE):
    albums.sort(key=lambda album: album.luminance)
    rows = list()
    for index in range(0, len(albums), SIZE):
        images = [cv.imread(albums[index+offset].path) for offset in range(SIZE)]
        rows.append(np.hstack([*images]))
    image = np.vstack([*rows])
    cv.imwrite('./images/output.png', image)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Album Mosaic Generator")
    parser.add_argument('--size', help="Set the number of albums in x and y axis", default=5, required=False)
    parser.add_argument('--range', help="Set the time range of top tracks to use: 'short', 'medium', 'long'", default="medium", required=False)
    args = parser.parse_args()
    
    MOSAIC_WIDTH = int(args.size)
    if args.range not in ["short", "medium", "long"]:
        raise Exception("invalid argument for range")
    match args.range:
        case "short":
            TIME_RANGE = "short_term"
        case "medium":
            TIME_RANGE = "medium_term"
        case "long":
            TIME_RANGE = "long_term"
    
    USERNAME, CLIENT_ID, CLIENT_SECRET = get_credentials()
    
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri="https://github.com/danpfister",
                                                   scope="user-top-read"))
    
    albums = get_album_covers(spotify, MOSAIC_WIDTH**2, TIME_RANGE)
    create_image(albums, MOSAIC_WIDTH)
    
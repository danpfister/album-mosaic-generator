# Album Mosaic Generator
This script generates a Mosaic using the album covers of the top tracks.

Unfortunately, the Spotify API is only able to return [the top 50 tracks](https://community.spotify.com/t5/Spotify-for-Developers/Cannot-set-offset-to-above-50-for-a-user-s-favorite-tracks/m-p/4975544/highlight/true#M482), which (after removing duplicates) leads to very limited mosaic sizes. At the moment there is no workaround available.

## Sorting based on Luminance
The album covers are sorted based on luminance according to the formula:
```
L = 0.213*R + 0.715*G + 0.072*B
```
Example output:

![alt text](https://github.com/danpfister/album-mosaic-generator/blob/main/images/output.png?raw=true)
from pathlib import Path
import re
import requests


def get_lyrics(artist, title, album, duration):

    lrc_lib = 'https://lrclib.net/api/get'

    try:
        # Try fetching lrc-lib with regular title
        res = requests.get(lrc_lib, params={'artist_name': artist,
                                            'track_name': title,
                                            'album_name': album,
                                            'duration': duration})
        res.raise_for_status()
        # print(res.json()["syncedLyrics"])
        print(f"{title} => Lyrics found")
        return res.json()["syncedLyrics"]
    except requests.exceptions.HTTPError:
        
        try:
            # Try fetching lrc-lib with title without feat
            
            new_title = re.sub(r'\(feat\..*', "", title)
            res = requests.get(lrc_lib, params={'artist_name': artist,
                                                'track_name': new_title,
                                                'album_name': album,
                                                'duration': duration})
            res.raise_for_status()
            # print(res.json()["syncedLyrics"])
            print(f"{title} => Lyrics found")
            return res.json()["syncedLyrics"]
        except requests.exceptions.HTTPError:
            
        
            print(f"{title} => Lyrics NOT found")
            return None
        

# if __name__ == "__main__":
#     get_lyrics("Tony Boy", "Ego", "Umile (Deluxe)", 141)



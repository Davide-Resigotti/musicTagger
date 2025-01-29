from pathlib import Path
import re
import requests


def UnsynchronisedLyrics(artist, title, album, duration):

    lrc_lib = 'https://lrclib.net/api/get'
    


    try:
        # Try fetching lrc-lib with regular title
        if album == "singles":
                album = ""
  
        res = requests.get(lrc_lib, params={'artist_name': artist,
                                            'track_name': title,
                                            'album_name': album,
                                            'duration': duration})
        res.raise_for_status()
        # print(res.json()["syncedLyrics"])
        print(f"{title} => plainLyrics found")
        return res.json()["plainLyrics"] 
    except requests.exceptions.HTTPError:
        
        try:
            # Try fetching lrc-lib with title without feat
            if album == "singles":
                album = ""
            new_title = re.sub(r'\(feat\..*', "", title)
            res = requests.get(lrc_lib, params={'artist_name': artist,
                                                'track_name': new_title,
                                                'album_name': album,
                                                'duration': duration})
            res.raise_for_status()
            # print(res.json()["syncedLyrics"])
            print(f"{new_title} => plainLyrics found")
            return res.json()["plainLyrics"]

        except requests.exceptions.HTTPError:   

            print(f"{title} => plainLyrics NOT found")
            return None
            
def SynchronisedLyrics(artist, title, album, duration):

    lrc_lib = 'https://lrclib.net/api/get'

    try:
        # Try fetching lrc-lib with regular title
        if album == "singles":
                album = ""
        res = requests.get(lrc_lib, params={'artist_name': artist,
                                            'track_name': title,
                                            'album_name': album,
                                            'duration': duration})
        res.raise_for_status()
        # print(res.json()["syncedLyrics"])
        print(f"{title} => syncedLyrics found")
        return res.json()["syncedLyrics"] 
    except requests.exceptions.HTTPError:
        
        try:
            # Try fetching lrc-lib with title without feat
            if album == "singles":
                album = ""
            new_title = re.sub(r'\(feat\..*', "", title)
            res = requests.get(lrc_lib, params={'artist_name': artist,
                                                'track_name': new_title,
                                                'album_name': album,
                                                'duration': duration})
            res.raise_for_status()
            # print(res.json()["syncedLyrics"])
            print(f"{new_title} => syncedLyrics found")
            return res.json()["syncedLyrics"]

        except requests.exceptions.HTTPError:   

            print(f"{title} => syncedLyrics NOT found")
            return None
        

# if __name__ == "__main__":
#     SynchronisedLyrics("Tony Boy", "Wet", "", 138)



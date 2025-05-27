import time
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TPE2, TXXX, TRCK, USLT, TCOM, SYLT, TMOO
import re
import os
import lrcGet
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Watcher:
    def __init__(self, directory_to_watch):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return None
        elif event.src_path.endswith('.mp3'):
            print(f"New file detected: {event.src_path}")
            time.sleep(5)
            manage_tags(event.src_path)

def manage_folder_tags(folder_path):
    print("Processing folder:", folder_path)
    if not os.path.exists(folder_path):
        print("The specified folder does not exist.")
        return
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.mp3'):
                file_path = os.path.join(root, file)
                # print(f"Found MP3 file: {file_path}")
                manage_tags(file_path)

def manage_tags(file_path):
    
    audio = ID3(file_path)
    
    # ------------------- GET TAGS -------------------
    
    mood = audio.get('TMOO', [None])

    
    if mood != "DONE":
    
        title = audio.get('TIT2', [None])
        artist = audio.get('TPE1', [None])
        album = audio.get('TALB', [None])
        albumArtist = audio.get('TPE2', [None])
        
        duration = str(audio.get('TLEN', [None])[0]) if audio.get('TLEN', [None])[0] is not None else None
        if duration:
            duration = duration.rstrip('0')
            if len(duration) < 3:
                duration = duration.ljust(3, '0')
            duration = int(duration)
        else:
            duration = None


        artists = audio.getall('TXXX:ARTISTS')[0] if audio.getall('TXXX:ARTISTS') else None
        track_number = audio.get('TRCK', [None])
        

            
        if title is None or artist is None:
            print("no artist or title")
            return
        
        
        # Get the first artist to compare to artist
        first_artists = artists if artists else None
        
        print("ORINGAL TAGS")
        print(f"Titolo: {title}")
        print(f"Artista: {artist.text}")
        print(f"Album: {album}") if album else None
        print(f"Album Artist: {albumArtist}") if albumArtist else None
        print(f"Durata: {duration}") if duration else None  
        print(f"Artisti: {artists.text}") if artists else None
        print(f"Track Number: {track_number}") if track_number else None
        print()
        
        # ------------------- EDIT TAGS -------------------
        
        # artists that are considered as double artist
        double_artist = ["Glocky & Faneto", "SadTurs & KIID", "Rayan & Intifaya", "Intifaya & Rayan"]
        
        
        
        
        if artists is not None :
            
            if artist[0] in double_artist and artist[0] == albumArtist[0]:
                principal_artist = artist[0]
                artists_list = []
                
            # if miss one of two in the artist
            elif artist[0] == "Rayan" or artist[0] == "Intifaya":
                principal_artist = "Rayan & Intifaya"
                
                artists_list = []
            elif albumArtist[0] == "Rayan" or albumArtist[0] == "Intifaya":
                principal_artist = "Rayan & Intifaya"
                
                artists_list = []
            else:
                principal_artist = artists[0]
                
            
            artists_list = ', '.join(artists).split(', ')
            



        else:
            if isinstance(artist, list):
                principal_artist = artist[0]
            else:
                artist = artist[0]
                if re.search(r"feat\.|&|,", artist):
                    artists_list = re.split(r"\s*feat.\s*|\s*&\s*|\s*,\s*", artist)
                    principal_artist = artists_list[0].strip()
                else:
                    principal_artist = artist
                    artists_list = []
        
        # Remove SadTurs and KIID from the artists 
        if principal_artist == "SadTurs & KIID":
            if "SadTurs" in artists_list:
                artists_list.remove("SadTurs")
                audio['TCOM'] = TCOM(encoding=3, text="SadTurs")
            if "KIID" in artists_list:
                artists_list.remove("KIID")
                audio['TCOM'] = TCOM(encoding=3, text="KIID")
                

                
        
        producers = ["SadTurs", 
                     "KIID", 
                     "Ava", 
                     "CoCo", 
                     "Peppe Amore", 
                     "Ddusi", 
                     "ilovethisbeat", 
                     "Wairaki", 
                     "Pherro", 
                     "Eiemgei", 
                     "Fallen", 
                     "tarantinothe3rd", 
                     "Simo Fre", 
                     "Ksub", 
                     "Brama", 
                     "4997", 
                     "85Prod", 
                     "Uanay", 
                     "Kadesh", 
                     "TroppoAvanti", 
                     "Nablito", 
                     "Ed Mars", 
                     "Niiut", 
                     "idua", 
                     "N'Dreamer", 
                     "NARDI", 
                     "Finesse", 
                     "Nko",
                     "333 Mob"]

        # Create a string with the list of featured artists, excluding double artists
        feat_artists = ' & '.join([item for item in artists_list if item not in producers])
        

            
        # Remove the main artist from the list of featured artists and spaces and &
        if principal_artist in feat_artists:
            feat_artists = re.sub(r'\s*&?\s*' + re.escape(principal_artist) + r'\s*&?\s*', '', feat_artists).strip()
            
        # Works only with Rayan & Intifaya    
        if principal_artist == "Rayan & Intifaya" or albumArtist == "Rayan & Intifaya":
            feat_artists = re.sub(r'\s*&?\s*' + re.escape("Rayan & Intifaya") + r'\s*&?\s*', '', feat_artists).strip()
            feat_artists = re.sub(r'\s*&?\s*' + re.escape("Intifaya & Rayan") + r'\s*&?\s*', '', feat_artists).strip()
            

        
        print()
        print(f"featured : {feat_artists}")
        print()
        
        
        print("EDITED TAGS")
        
        # TITLE
        # Check if feat artists are set, if not set it to the list of featured artists
        
        title = title[0]

        
        title = re.sub(r'\(feat\..*?\)', "", title, flags=re.IGNORECASE).strip()
        
  
        if "feat" not in title and len(artists_list) > 0 and feat_artists != "":
            new_title = f"{title} (feat. {feat_artists})"
            # print("feat not in title")
        elif "(feat." in title and len(artists_list) > 0 and feat_artists != "":
            new_title = re.sub(r'\(feat\..*', f"(feat. {feat_artists})", title)
            # print("(feat in title")
        elif "feat." in title and len(artists_list) > 0 and feat_artists != "":
            new_title = re.sub(r'\feat\..*', f"(feat. {feat_artists})", title)
            # print("feat. in title")
        else:
            new_title = title
        
               
        # Remove the (prod. ...) and (official video) from the title
        new_title = re.sub(r'\(prod\..*?\)|\(official video\)', "", new_title, flags=re.IGNORECASE).strip()
        
        # Remove all (feat. ...) from the new title
        # new_title = re.sub(r'\(feat\..*?\)', "", new_title, flags=re.IGNORECASE).strip()

        # Update the title tag
        #if title != new_title: removed because do not update when remove (feat.)
        audio['TIT2'] = TIT2(encoding=3, text=new_title)
        print(f"Titolo aggiornato: {new_title}")
        
        #ARTIST
        # Check if artist is set, if not set it to the principal artist
        if artist != principal_artist:
            audio['TPE1'] = TPE1(encoding=3, text=principal_artist)
            print(f"Artista aggiornato: {principal_artist}")
            
        #ALBUM
        # Chek if the track is a single, if so set the album name to singles
        if track_number == '1/1' or track_number == '1':
            audio['TALB'] = TALB(encoding=3, text='singles')
            album = 'singles'
            print("Album impostato a singles")

            
        #TRACK NUMBER
        # Check if track number is set, if not set it to 1
        if track_number is None:
            audio['TRCK'] = TRCK(encoding=3, text='1')
            print("Track number impostato a 1")
        
        #ALBUM ARTIST
        # Check if album artist is set, if not set it to the artist name    
        if albumArtist != principal_artist:
            audio['TPE2'] = TPE2(encoding=3, text=principal_artist)
            print(f"Album Artist aggiornato: {principal_artist}")
            
        #ARTISTS
        # if artists is None 
        # add to the array of artists
        if first_artists is None:
            artists_list.insert(0, principal_artist)
            audio['TXXX:ARTISTS'] = TXXX(encoding=3, text=artists_list, desc='ARTISTS')
            print(f"Artisti aggiornati: {audio['TXXX:ARTISTS'].text}")
            
        #DISC NUMBER
        # remove disk number for singles
        if album == 'singles':
            audio.delall('TPOS')
            

        # DOWNLOAD lyrics
        
        # replace lyrics 
        audio.delall('USLT')
        unsynchronisedLyrics = lrcGet.UnsynchronisedLyrics(principal_artist, new_title, album, duration)
        audio['USLT'] = USLT(encoding=3, text=unsynchronisedLyrics)
        




    
        print()
        print("-----------------------------")
        print() 
        
        
        audio['TMOO'] = TMOO(encoding=3, text="DONE")
            
        audio.save() 
        
        # Update the file name with the new title if it isn't already correct
        new_file_name = re.sub(r'.*\.mp3$', f"{new_title}.mp3", os.path.basename(file_path))
        new_file_path = os.path.join(os.path.dirname(file_path), new_file_name)
        if file_path != new_file_path:
            os.rename(file_path, new_file_path)
            file_path = new_file_path
            
        
        
    
    def print_tags(file_path):
        try:
            audio = ID3(file_path)
            for tag in audio.values():
                print(f"{tag.FrameID}: {tag.text}")

        except Exception as e:
            print(f"Errore nel caricamento del file: {e}")
            
            
            
    def print_lyrics(file_path):
        try:
            # Carica i tag ID3 dal file audio
            audio = ID3(file_path)
            
            # Cerca il frame USLT che contiene le lyrics
            uslt = audio.getall('USLT')
            if uslt:
                for lyrics in uslt:
                    print(f"Lyrics ({lyrics.lang}): {lyrics.text}")
            else:
                print("No lyrics found.")

        except Exception as e:
            print(f"Errore nel caricamento del file: {e}")
        

        




if __name__ == "__main__":
    folder_to_watch = "/Users/davideresigotti/Music/Music/Media.localized/Music"
    manage_folder_tags(folder_to_watch)
    # w = Watcher(folder_to_watch)
    # w.run()


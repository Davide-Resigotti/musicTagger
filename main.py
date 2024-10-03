from mutagen.id3 import ID3, TIT2, TPE1, TALB, TPE2, TXXX, TRCK, USLT, TCOM
import re
import os
import lrcGet





def manage_folder_tags(folder_path):
    print("Processing folder:", folder_path)
    if not os.path.exists(folder_path):
        print("The specified folder does not exist.")
        return
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.mp3'):
                file_path = os.path.join(root, file)
                print(f"Found MP3 file: {file_path}")
                manage_tags(file_path)

def manage_tags(file_path):
    
    audio = ID3(file_path)
    
    # ------------------- GET TAGS -------------------
    
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
    
    # Get the first title to compare to album name to check if it's a single
    first_title = title[0] if title else None
    
    # Get the first artist to compare to artist
    first_artists = artists if artists else None
    
    print("ORINGAL TAGS")
    print(f"Titolo: {title}")
    print(f"Artista: {artist.text}")
    print(f"Album: {album}") if album else None
    print(f"Album Artist: {albumArtist}") if albumArtist else None
    print(f"Durata: {duration}") if duration else None  
    print(f"Artisti: {artists.text}") if artists else None
    print()
    
    # ------------------- EDIT TAGS -------------------
    
    # artists that are considered as double artist
    double_artist = ["Glocky & Faneto", "SadTurs & KIID", "Rayan & Intifaya" ]
    
    if artists is not None :
        if artist[0] in double_artist:
            principal_artist = artist[0]
            artists_list = []
            
        elif artist[0] == "Rayan" or artist[0] == "Intifaya":
            principal_artist = "Rayan & Intifaya"
            artists_list = []
        else:
            principal_artist = artists[0]
        
        artists_list = ', '.join(artists).split(', ')
        print(principal_artist)

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
            


        
    # Remove the main artist from the list of featured artists
    if principal_artist in artists_list:
        artists_list.remove(principal_artist)
            
    
    producers = ["SadTurs", "KIID", "Ava", "CoCo", "Peppe Amore"]

    # Create a string with the list of featured artists, excluding double artists
    feat_artists = ', '.join([item for item in artists_list if item not in producers])
    
       
    print()
    print(f"featured : {feat_artists}")
    print()
    
    print("EDITED TAGS")
    
    # TITLE
    # Check if feat artists are set, if not set it to the list of featured artists
    
    title = title[0]
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


    # Update the title tag
    if title != new_title:
        audio['TIT2'] = TIT2(encoding=3, text=new_title)
        print(f"Titolo aggiornato: {new_title}")
    
    #ARTIST
    # Check if artist is set, if not set it to the principal artist
    if artist != principal_artist:
        audio['TPE1'] = TPE1(encoding=3, text=principal_artist)
        print(f"Artista aggiornato: {principal_artist}")
        
    #ALBUM
    # Chek if the track is a single, if so set the album name to singles
    if first_title == album:
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
        

    # download lyrics
    firts_lyrics = audio.getall('USLT')[0].text if audio.getall('USLT') else None
    
    
    lyrics = lrcGet.get_lyrics(artist[0], title, album[0], duration)
    if lyrics is None:
        new_title1 = re.sub(r'\(feat\..*', "", title)
        lyrics = lrcGet.get_lyrics(artist[0], new_title1, album[0], duration)
    
    if lyrics is not None:
        if firts_lyrics != lyrics:
            audio['USLT'] = USLT(encoding=3, text=lyrics)



  
    print()
    print("-----------------------------")
    print() 
        
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
    folder_path = '/Users/davideresigotti/Downloads/a'
  
    manage_folder_tags(folder_path)
    # print_tags('/Users/davideresigotti/Downloads/NO REGULAR MUSIC (Deluxe)/CD2/05 - HORSE DANCE (feat. Yung Snapp, DrefGold, Side Baby).mp3')
    # print_lyrics('/Users/davideresigotti/Downloads/SadTurs & KIID.mp3')


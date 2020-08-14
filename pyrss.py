from os import close
import sys, os
import multiprocessing as mp
from re import sub
import atoma
import requests
import sqlite3
import os
import re
import pygame
import time
import mutagen.oggvorbis
#import pydub
import PySimpleGUI
import shutil
import subprocess

gui_queue = None





def pyrss_db_create():
    db = sqlite3.connect("db-pyrss.db") # Create db for storing name of first currently available feed item file so we know if we should download the feed or not
    # grab cursor from handle
    cur = db.cursor()
    # Create the table the first time if it doesn't exist
    cur.execute("""
                CREATE TABLE IF NOT EXISTS pyrss_db (
                id INTEGER PRIMARY KEY, filename VARCHAR UNIQUE, feedtitle VARCHAR
                )          
    """)
    # See if it's empty
    cur.execute("""
                SELECT COUNT(*) FROM pyrss_db        
    """)
    count = cur.fetchone()[0] # Fetches result, which is next row of query result set
    # If it's empty, put dummy text in so we can update it with the file name later
    if count < 1:
        cur.execute("""
                    INSERT INTO pyrss_db (filename, feedtitle) VALUES ("dummytext", "dummytitle")
        """)
    # If the feeds.txt exists, it might have feeds in it, don't wipe out! Otherwise, create it to be used by users
    if os.path.exists("feeds.txt") == False:
        open("feeds.txt", "w")
    db.commit() # Commit change to db
    db.close() # Close db
    
def pyrss_db_check(filename, feedtitle):
    print(filename)
    print(feedtitle)
    db = sqlite3.connect("db-pyrss.db") # returns a handle
    # grab cursor from handle
    cur = db.cursor() # keep track of where you are in the db as you run commands
    # Run argument against db to see if currently available feed items[0] matches what's already been downloaded and stored in db
    cur.execute(f"""
                SELECT COUNT(*) FROM pyrss_db WHERE filename = "{filename}" AND feedtitle = "{feedtitle}"       
    """)
    count = cur.fetchone()[0] # Fetches result
    #print(f"There are {count} rows")
    # If it's not in the db, set the entry to the first available feed item name to run future queries against to check if we have most recent feed items
    if count < 1:
        cur.execute(f"""
                    INSERT OR IGNORE INTO pyrss_db (filename, feedtitle) values ("{filename}", "{feedtitle}")
        """)
        #print(f"We inserted {filename} into the db")
        db.commit() # Commit to db
    else:
        pass
        # Set status to caught up
        #py_rss_status = f"Status: You're all caught up on feeds!"
        # re-enable the download button
        #window['Download'].update(disabled=False)
        #window["py_rss_status"].update(f"{py_rss_status}")
        #window.refresh() # Refresh the window
    db.close() # Close db
    return count # returns count to see if we should continue downloading feed or not
    
    

    
            
def is_dir_half_full(path):
    if os.path.exists(path) and not os.path.isfile(path):
        # If path exists and it's not a file 
        # Check for ogg files, that's all we want to know
        can_play = False
        for fname in os.listdir(path):
            if fname.endswith("ogg") and os.path.getsize(f"{path}/{fname}") > 10:
                can_play = True
                break
            else:
                can_play = False
        if can_play == True:
            return True
        else:
            return False
        # Check if the directory is empty or not empty
        # for filez in os.listdir(path):
        #     if ".ogg" in filez:
        #         return True
        #     else:
        #         pass 
    else: 
        return False
  
   
        

def play_files(to_play_dir, played_dir, favs_dir, window, py_rss_status, bar_length, values):
    old_file = ""
    for py_file in os.listdir("to_play"):
        if py_file.endswith(".ogg"):
            bar_length = 0
            player_stop = 0
            window["percentage"].update_bar(bar_length)
            window['Fav it!'].update(disabled=False)
            window['Pause'].update(disabled=False)
            window['Play'].update(disabled=True)
            window['Stop'].update(disabled=False)
            py_file_path = f"{to_play_dir}/{py_file}"
            py_file_ogg = mutagen.oggvorbis.OggVorbis(py_file_path)
            py_file_length_mess = py_file_ogg.info.pprint()
            py_file_length_search = re.search("Ogg Vorbis, (.+?) seconds", py_file_length_mess)
            if py_file_length_search:
                global length_found
                length_found = float(py_file_length_search.group(1))
            py_rss_ogg_len = round(length_found + 1)
            #print(py_rss_ogg_len)
            
            
            
            
            pygame.mixer.init()
            global music_file
            music_file = open(f"{to_play_dir}/{py_file}")
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play()
            
            bar_interval = 60/py_rss_ogg_len
            window["py_rss_status"].update(f"{py_rss_status}")
            player_position = 0
            while player_position < py_rss_ogg_len:
                window["percentage"].update_bar(bar_length)
                #print(pygame.mixer.music.get_pos())
                bar_length = bar_length + bar_interval
                player_position += 1
                if old_file != "":
                    os.remove(old_file)
                    old_file = ""
                #print(player_position)
                event, values = window.read(timeout = 1000)
                if event == PySimpleGUI.WIN_CLOSED:
                    music_file.close()
                    break
                if event == "Fav it!":
                    src = os.path.realpath(f"{to_play_dir}\\{py_file}")
                    dst = os.path.realpath(f"{favs_dir}") 
                    # I... didn't know if this would work or not but it does, awesome!
                    shutil.copy(src, dst)
                    window['Fav it!'].update(disabled=True)
                if event == "Rewind":
                    window['Rewind'].update(disabled = True)
                    bar_length = bar_length - (bar_interval * 10)
                    if bar_length < 0:
                        bar_length = 0
                    pygame.mixer.music.stop()
                    player_position = player_position - 10
                    if player_position < 0:
                        player_position = 0
                    pygame.mixer.music.load(f"{to_play_dir}/{py_file}")
                    pygame.mixer.music.play(loops = 0, start = player_position)
                    window['Rewind'].update(disabled = False)
                if event == "Fast Fwd":
                    window['Fast Fwd'].update(disabled = True)
                    bar_length = bar_length + (bar_interval * 10)
                    pygame.mixer.music.stop()
                    player_position = player_position + 10
                    pygame.mixer.music.load(f"{to_play_dir}/{py_file}")
                    pygame.mixer.music.play(loops = 0, start = player_position)
                    window['Fast Fwd'].update(disabled = False)
                if event == "Pause":
                    window['Pause'].update(disabled = True)
                    window['Rewind'].update(disabled = True)
                    window['Fast Fwd'].update(disabled = True)
                    window['Play'].update(disabled = False)
                    pygame.mixer.music.stop()
                    py_rss_status = "Status: Paused"
                    window["py_rss_status"].update(f"{py_rss_status}")
                    while True:
                        event, values = window.read(timeout = 250)
                        if event == PySimpleGUI.WIN_CLOSED:
                            music_file.close()
                            break
                        elif event == "Play":
                            player_stop == 0
                            break
                        elif event == "Stop":
                            bar_length = 0
                            player_position = 0
                            window['Play'].update(disabled = False)
                            window['Fav it!'].update(disabled = True)
                            player_stop = 1
                            window["percentage"].update_bar(bar_length)
                            music_file.close()
                            break
                        else:
                            pass
                    event, values = window.read(timeout = 10)        
                    if player_stop == 1 or event == "Stop":
                        window['Stop'].update(disabled = True)
                        py_rss_status = "Status: Waiting for input"
                        window["py_rss_status"].update(f"{py_rss_status}")
                        music_file.close()
                        return
                    else:
                        player_stop = 0
                    window['Pause'].update(disabled = False)
                    window['Fav it!'].update(disabled = False)
                    window['Play'].update(disabled = True)
                    window['Rewind'].update(disabled = False)
                    window['Fast Fwd'].update(disabled = False)
                    pygame.mixer.music.load(f"{to_play_dir}/{py_file}")
                    pygame.mixer.music.play(loops = 0, start = player_position)
                if event == "Stop":
                    window['Pause'].update(disabled = True)
                    window['Rewind'].update(disabled = True)
                    window['Fast Fwd'].update(disabled = True)
                    window['Play'].update(disabled = False)
                    window['Stop'].update(disabled = True)
                    window['Fav it!'].update(disabled = True)
                    pygame.mixer.music.stop()
                    music_file.close()
                    bar_length = 0
                    player_position = 0
                    window["percentage"].update_bar(bar_length)
                    py_rss_status = "Status: Waiting for input"
                    window["py_rss_status"].update(f"{py_rss_status}")
                    return
                if event == "Fav it!":
                    src = os.path.realpath(f"{to_play_dir}\\{py_file}")
                    dst = os.path.realpath(f"{favs_dir}") 
                    # I... didn't know if this would work or not but it does, awesome!
                    shutil.copy(src, dst)
                    window['Fav it!'].update(disabled=True)
        pygame.mixer.music.stop() 
        music_file.close()
        src = os.path.realpath(f"{to_play_dir}\\{py_file}")
        dst = os.path.realpath(f"{played_dir}\\{py_file}")
        shutil.copy(src, dst)
        old_file = src
            
        
        
class ScreenPython:
    

    def __init__(self):
        global gui_queue
        py_rss_status = "Waiting for input"
        # Set global variables for directories to store feed files
        to_play_dir = "to_play"
        played_dir = "played"
        favs_dir = "favs"
        # Set player progress bar to zero
        bar_length = 0
        # Set download/conversion percentage to zero
        download_percentage = 0
        percentage = 0
        py_rss_status = "Waiting for input"
        global converting_status
        converting_status = False

        PySimpleGUI.theme('DarkTeal12')
        layout = [
        #[PySimpleGUI.Text("You can leave the feed box empty and instead use local feeds.text file, one feed per line.")],
        #[PySimpleGUI.Text("The interface might freeze for a few seconds with large audio files, but it will finish.")],
        [PySimpleGUI.Text("Feed: "), PySimpleGUI.InputText()],
        [PySimpleGUI.Text("Max items to download: "), PySimpleGUI.InputText(default_text = "20", size = (4,1)), PySimpleGUI.Button("Download")],
        [PySimpleGUI.Text('_'  * 60, justification = "center", size = (60,1))],
        [PySimpleGUI.Text("Download using feeds.text instead: "), PySimpleGUI.Button("Download using feeds file")],
        [PySimpleGUI.Text('_'  * 60, justification = "center", size = (60,1))], 
        [PySimpleGUI.Text(f"Status: {py_rss_status}", key = "py_rss_status", size = (60,1))],
        [PySimpleGUI.Text('_'  * 60, justification = "center", size = (60,1))], 
        [PySimpleGUI.Text("Player", justification = "center", size = (60, 1))],
        [PySimpleGUI.Button("Play All Files"), PySimpleGUI.Button("Play"), PySimpleGUI.Button("Pause"), PySimpleGUI.Button("Rewind"), PySimpleGUI.Button("Fast Fwd"), PySimpleGUI.Button("Fav it!"), PySimpleGUI.Button("Stop")],
        [PySimpleGUI.Text('  '), PySimpleGUI.ProgressBar(60, orientation = "h", size = (40,20), key = "percentage")]]
        
        window = PySimpleGUI.Window("Py_RSS Aggregator", layout, finalize=True)
        window['Pause'].update(disabled=True)
        window['Stop'].update(disabled=True)
        window['Fav it!'].update(disabled=True)
        window['Rewind'].update(disabled=True)
        window['Fast Fwd'].update(disabled=True)

        while True:  # Event Loop

            event, values = window.read(timeout = 10)
            
            # If directory not empty
            if is_dir_half_full(to_play_dir):
                if converting_status == False:
                    #print(f"converting status is {converting_status}")
                    window['Play'].update(disabled=False)
                    window['Play All Files'].update(disabled=False)
                else:
                    #print(f"converting status is {converting_status}")
                    window['Play'].update(disabled=True)
                    window['Play All Files'].update(disabled=True)
            else:
                window['Play'].update(disabled=True)
                window['Play All Files'].update(disabled=True)
                py_rss_status = "Status: You need to download some feeds to have something to play"
                window.refresh()
                
            if event == PySimpleGUI.WIN_CLOSED:
                break
            
            if not "ffmpeg.exe" in list(os.listdir(".")) or not "ffplay.exe" in list(os.listdir(".")) or not "ffprobe.exe" in list(os.listdir(".")):
                py_rss_status = "Status: You need ffmpeg.exe, ffplay.exe, and ffprobe.exe in app directory"
                window["py_rss_status"].update(f"{py_rss_status}")
                window.refresh()
            
            elif event == "Download" or event == "Download using feeds file":
                global failed_feed
                failed_feed = 0
                window['Download'].update(disabled=True)
                py_rss_status = "Status: Checking feeds..."
                window["py_rss_status"].update(f"{py_rss_status}")
                if values[1] == "" and event == "Download":
                    py_rss_status = f"Status: Sorry, please enter max download items" # Apologize, retry
                    
                    window['Download'].update(disabled=False) # Enable download button so they can try again
                    window["py_rss_status"].update(f"{py_rss_status}") # Set status
                    window.refresh() # Refresh window
                    continue
                
                pyrss_db_create()
                #feed_getter = multiprocessing.Process(name="get_feed", target = "get_feed", args = (window, values, to_play_dir, percentage))
                # It would be smarter to download all files first, then come back, and use threading for conversion of all ogg files in dir
                download_percentage = 0
                parse_and_download(window, event, values, to_play_dir, download_percentage)
                
                if failed_feed == 1:
                    print("failed feed")
                    py_rss_status = f"Status: Sorry, there was a problem with at least one feed" # Apologize, retry
                    
                    window['Download'].update(disabled=False) # Enable download button so they can try again
                    window["py_rss_status"].update(f"{py_rss_status}") # Set status
                    window.refresh() # Refresh window
                    print("FAILED FEED")
                    continue
                window["py_rss_status"].update(f"{py_rss_status}")
                converting_status = True
                prog_meter(gui_queue, to_play_dir, percentage)
                event, values = window.read(timeout=10)
                window["py_rss_status"].update(f"{py_rss_status}") 
                window.refresh()   
                
                #feed_getter.start()
                if is_dir_half_full(to_play_dir) and converting_status == False:
                    window['Play'].update(disabled=False)
                    window['Play All Files'].update(disabled=False)
                else:
                    py_rss_status = "Status: You need to download some feeds to have something to play"
                    window.refresh()
                
                
                    
            elif event == "Play All Files" or event == "Play":
                window['Download'].update(disabled=True)
                window['Play All Files'].update(disabled=True)
                window['Play'].update(disabled=True)
                window['Rewind'].update(disabled=False)
                window['Fast Fwd'].update(disabled=False)
                window['Stop'].update(disabled=False)
                py_rss_status = "Status: Playing!"   
                play_files(to_play_dir, played_dir, favs_dir, window, py_rss_status, bar_length, values)   
            else:
                pass
            
            if converting_status:
                window['Play All Files'].update(disabled=True)
                window['Play'].update(disabled=True)
                window['Download'].update(disabled=True)
                window['Download using feeds file'].update(disabled=True)
                try:
                    message = gui_queue.get_nowait()    # see if something has been posted to Queue
                except Exception as e:                     # get_nowait() will get exception when Queue is empty
                    message = None                      # nothing in queue so do nothing
                if message:
                    print(f'Got a queue message {message}!!!')
                    py_rss_status = message
                    window["py_rss_status"].update(f"{py_rss_status}")
                    if message == "Status: Ready to play files!":
                        converting_status = False
                
            
        window.close()
        
def parse_and_download(window, event, values, to_play_dir, download_percentage):
    global feeds # Declare global variable
    global failed_feed
    failed_feed = 0
    feeds = {} # Empty list to fill with feeds
    # Create folders if they don't exist to hold the received rss files to play, and folder for played files
    if not os.path.exists("to_play"):
        os.mkdir("to_play")
    if not os.path.exists("played"):
        os.mkdir("played")
    if not os.path.exists("favs"):
        os.mkdir("favs")
    # Get url response of rss url
    # Set URL for feed
    #event, values = window.read(timeout = 10) # DON'T? Need this here to read values list below for rss_url? oK, DON'T lol
    
    if os.path.exists("feeds.txt") == True and not values[0]: # If feeds.txt exists and feed text bar in app is empty
        feeds_txt = open("feeds.txt", "r") # Open feeds.txt for reading
    
        if feeds_txt.mode == "r": # read mode!
            global feeds_txt_content # Declare global variable
            feeds_txt_content = feeds_txt.readlines() # fill content variable with lines in file
        feeds_txt.close() # Close feeds.txt
        for feed in feeds_txt_content: # For each line in file content
            feed_info = feed.strip() #Strip whitespace
            feed_info = feed.split(",")
            max_items = int(feed_info[1].strip())
            feed_link = feed_info[0].strip()
            feeds[feed_link] = max_items # 
        #feeds = list(dict.fromkeys(feeds)) # Remove duplicates, just in case, by making a list from a dict from a list ;)
    else:
        # If the box had text, use that as feed url - "Test feed url: https://apps.jw.org/E_RSSMEDIAMAG?rln=E&rmn=g&rfm=mp3"
        rss_max_items = int(values[1].strip()) # 
        feed_link = values[0].strip()
        feeds[feed_link] = rss_max_items # Append to empty feeds list (empty because there's only one feed)
    n = 0
    total_downloads = 0
    for feed, max_items in feeds.items():
        total_downloads += max_items
    download_percentage_point = 100/total_downloads
    download_percentage = 0
    for feed, max_items in feeds.items(): # Loop over dict of feeds and enumerate them for the user
        try: # If they've input bad feeds, catch it
            rss_url_response = requests.get(feed) # Get the feed with requests.get()
        except (requests.exceptions.InvalidSchema, requests.exceptions.MissingSchema): # This is triggered if the feed isn't valid
            failed_feed = 1
            py_rss_status = f"Status: Sorry, {feed} is not a valid feed, please try again" # Apologize, retry
            
            window['Download'].update(disabled=False) # Enable download button so they can try again
            window["py_rss_status"].update(f"{py_rss_status}") # Set status
            window.refresh() # Refresh window
            return
        except Exception:
            failed_feed = 1
            return
        # Parse the feed content
        try:
            py_rss_feed = atoma.parse_rss_bytes(rss_url_response.content)
        except (atoma.exceptions.FeedParseError):
            failed_feed = 1
            py_rss_status = f"Status: Sorry, {feed} is not a valid feed, please try again" # Apologize, retry
            
            window['Download'].update(disabled=False) # Enable download button so they can try again
            window["py_rss_status"].update(f"{py_rss_status}") # Set status
            window.refresh() # Refresh window
            return
        # Show feed title
        #print(f"The feed title is {py_rss_feed.title}.")
        # Print feed item count
        #print(f"There are {len(py_rss_feed.items)} items")
        py_rss_filename_count = 1
        # For feed entries, download each to "to_play" folder for them to be played
        
        py_rss_status = f"Status: Downloading Feed {n + 1} of {len(feeds)} ({py_rss_feed.title[:15]})... ({round(download_percentage)}% complete)"
        window["py_rss_status"].update(f"{py_rss_status}")
        window.refresh()
        if len(py_rss_feed.items) == 0:
            download_percentage += (download_percentage_point * max_items)
            py_rss_status = f"Status: Downloading Feed {n + 1} of {len(feeds)} ({py_rss_feed.title[:15]})... ({round(download_percentage)}% complete)"
            window["py_rss_status"].update(f"{py_rss_status}")
            #py_rss_status = f"Status: Ready to play feeds!"
            #window["py_rss_status"].update(f"{py_rss_status}")
            #window['Download'].update(disabled=False)
            #window.refresh() # Refresh window
            n += 1
            continue
        #download_percentage_point = 100/len(py_rss_feed.items)*len(feeds) Old didn't work
        for rn, entries in enumerate(py_rss_feed.items):
            download_percentage += download_percentage_point
            
            
            # Use requests.get to get the link per item
            if not entries.link or not ".mp3" in entries.link:
                if entries.guid or not ".mp3" in entries.guid:
                    if not entries.enclosures or not ".mp3" in str(entries.enclosures):
                        print("not here")
                        print(f"uhoh, we lost feed info...{print(entries)}")
                        exit()
                    else:
                        #extractor = urlextract.URLExtract() # for urlextractor
                        #extractor.update() # for urlextractor
                        # urlextractor fails in compiled program
                        urlz = (re.search("(?P<url>https?://[^\s'\"]+)", str(entries.enclosures)).group("url"))
                        #urlz = extractor.find_urls(str(entries.enclosures)) # for urlextractor
                        #print(urlz)
                        #urlz = urlz[0] # for urlextractor
                        urlz = urlz.split("?", 1) # for urlextractor AND for getting rid of parameters so sanitized for db
                        #print(urlz[0]) # for urlextractor
                        
                        
                        rss_file_name = os.path.basename(urlz[0])  # was urlz[0] for urlextractor
                        if pyrss_db_check(rss_file_name, py_rss_feed.title) == 1:
                            
                            break
                        else:
                            rss_file_response = requests.get(urlz[0])   # was urlz[0] for urlextractor
                        # print(rss_file_name)
                        # exit()
                else:
                    
                    rss_file_name = os.path.basename(entries.guid)
                    if pyrss_db_check(rss_file_name, py_rss_feed.title) == 1:
                        
                        break
                    else:
                        rss_file_response = requests.get(entries.guid)
            else:
                
                rss_file_name = os.path.basename(entries.link)
                if pyrss_db_check(rss_file_name, py_rss_feed.title) == 1:
                    
                    break
                else:
                    rss_file_response = requests.get(entries.link)
            # http://www.podcast411.com/new_demo_feed.xml https://podcasts.files.bbci.co.uk/p05k5bq0.rss
            # Get the file name element response
            #rss_file_name_unparsed = rss_file_response.headers["content-disposition"] 
            # Parse the file name out of it
            #rss_file_name_partly_parsed = re.findall("filename=(.+)", rss_file_name_unparsed)[0] 
            # Strip quotation marks, not needed
            
            #print(rss_file_name)
            # If it's the first item in feed, run a query on the db to see if this is an old feed. If so, discontinue downloading and checking
            if py_rss_filename_count > max_items:
                print("Reached the max!")
                download_percentage -= download_percentage_point
                py_rss_status = f"Status: Downloading Feed {n + 1} of {len(feeds)} ({py_rss_feed.title[:15]})... ({round(download_percentage)}% complete)"
                window["py_rss_status"].update(f"{py_rss_status}")
                break
            #if pyrss_db_check(rss_file_name, py_rss_feed.title) == 1: # Don't need here anymore
            # returns from function pyrss_db_check(rss_file_name)
            if n == len(feeds):
                
                py_rss_status = f"Status: You're all caught up on feeds!"
                window['Download'].update(disabled=False)
                window["py_rss_status"].update(f"{py_rss_status}")
                window.refresh() # Refresh window
                return # exit function
            else:
                pass
            py_rss_filename_count += 1 # If we've passed the test, continue downloading
            # download the files to the "to_play" directory
            # Setting the timeout to 30 seconds in case they're bigger files
            with open(f"{to_play_dir}/{rss_file_name}", "wb") as f: # wb, b for binary
                for chunk in rss_file_response.iter_content(chunk_size=5120):
                    if not chunk:
                        break
                    
                    window.refresh()
                    window["py_rss_status"].update(f"{py_rss_status}")
                    window.refresh() # Refresh window
                    f.write(chunk)
                    f.flush()
            if n != len(feeds) and rn - 1 != len(py_rss_feed.items):
                print(f"The length of feeds is {len(feeds)}, n is {n}, length of feed items is {len(py_rss_feed.items)} and rn is {rn}")  
                
            else:
                pass
                #py_rss_status = f"Status: Ready to play feeds!"
            py_rss_status = f"Status: Downloading Feed {n + 1} of {len(feeds)} ({py_rss_feed.title[:15]})...({round(download_percentage)}% complete)"
            window["py_rss_status"].update(f"{py_rss_status}")
            window.refresh() # Refresh window
        n += 1
    window['Download'].update(disabled=False)
def prog_meter(gui_queue, to_play_dir, percentage):
    proc = mp.Process(target=convert_them_all, args=(gui_queue, to_play_dir, percentage))
    proc.start()
    return proc

def convert_them_all(gui_queue, to_play_dir, percentage):
    print(gui_queue)
    global py_rss_status
    global converting_status
    converting_status = True
    num_of_files = 0
    for mp3file in list(os.listdir("to_play")):
        if mp3file.endswith(".mp3"):
            num_of_files += 1
    if num_of_files == 0:
        converting_status = False
        py_rss_status = f"Status: Ready to play files!"
        gui_queue.put(py_rss_status)
        return
    
    percentage_point = 100/num_of_files
    percentage = 0
    while converting_status:
        for py_file in os.listdir("to_play"):
            if py_file.endswith(".mp3"):
                
            # Convert to ogg because pygame has TERRIBLE mp3 support consistently
                py_rss_status = f"Status: Converting to ogg, please stand by... {round(percentage)}% complete"
                gui_queue.put(py_rss_status)
                rss_ogg_name = py_file.replace("mp3", "ogg")
                #the_ogg_conversion = pydub.AudioSegment.from_mp3(f"{to_play_dir}/{py_file}").export(f"{to_play_dir}/{rss_ogg_name}", format = "ogg")
                #import gc
                #del the_ogg_conversion
                #gc.collect()
                # Remove the old file
                subprocess.call(["ffmpeg", "-hide_banner", "-loglevel", "warning", "-n", "-i", f"{to_play_dir}/{py_file}", "-c:a", "libvorbis", "-q:a", "4", f"{to_play_dir}/{rss_ogg_name}"], shell=True)
                os.remove(f"{to_play_dir}/{py_file}")
                percentage += percentage_point
        
        py_rss_status = f"Status: Ready to play files!"
        gui_queue.put(py_rss_status)
        converting_status = False
        return

def main():
    global gui_queue
    gui_queue = mp.Queue()
    screen = ScreenPython()

if __name__ == '__main__':
    main()
    
    
    # TODO put a reset button in to remove all played episodes data
    # TODO error handling for garbage in feeds.txt file, number of feeds not an int, etc
    
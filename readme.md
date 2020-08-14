# PyRss

This is an MP3 audio podcast aggregator that works specifically with xml feed files. For instance, "https://podcasts.files.bbci.co.uk/p05k5bq0.rss", "https://feeds.npr.org/344098539/podcast.xml" or "https://apps.jw.org/E_RSSMEDIAMAG?rln=E&rmn=g&rfm=mp3". Due to the variation in feed xml structure, it may not work for all feeds, so it's a WIP. If you find a feed it doesn't work for, ping me with the url and I'll see if I can add the structure to PyRss. Also, because pydub's AudioSegment functionality isn't great for larger files, I had to resort to using ffmpeg.exe for conversion, so this is a Windows only application for the moment.

## Functionality

It downloads the specified amount of files from each specified feed, one by one, and then converts them to ogg using multiprocessing, because the audio playing module (pygame) doesn't play well with all mp3 files. Once they're converted, you can play the files one by one, and use the 'rewind' and 'fast forward' buttons to seek in 10 second increments. For larger podcasts, I can see how 10 seconds isn't optimal for many use cases, but this is more or less an educational exercise in using Python and basic modules to demonstrate the power of Python even for multimedia use. To save a currently playing file as a 'favorite', click 'Fav it!' and it will be copied to the 'favs' directory. After a file is finished playing, it is moved from the "to_play" directory to the "played" directory, where you can do what you wish with them.

## Getting Started

You'll need ffmpeg, ffplay, and ffprobe's executable files in the same directory with pyrss.py. If you want to list more than one feed to download from, create a file "feeds.txt" in the same directory, and put one feed per line followed by a comma and the max number of items to download from the feed. Alternatively you can just use the user interface to download one feed at a time and enter the max number in the right box.

### Prerequisites

What Python modules you'll need are listed in the requirements.txt file, so you can "pip install requirements.txt" if you don't have them.

### Installing

Just download the zip file and extract it where you want to use it.

## Built With

* [Visual Studio Code](https://code.visualstudio.com/) - Love it!

## Contributing

I don't plan to push this project much further because of the limitations of the basic mondules. For better multimedia control, a more modern interface with better media controls would be better, perhaps using html, css, and js. 

## Authors

* **Micah Lahren** - *Project* - [AlphaPy](https://github.com/AlphaPy)

## License

This project is licensed under the MIT License - see the [license.md](license.md) file for details

## Acknowledgments

* pygame
* PySimpleGUI
* Exercism Mentors

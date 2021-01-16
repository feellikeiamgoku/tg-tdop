YDL_OPTS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.mp3',
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True
}

RATE_LIMIT = 25

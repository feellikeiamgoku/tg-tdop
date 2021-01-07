from youtube_dl import YoutubeDL

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.mp3',
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': False
}

with YoutubeDL(ydl_opts) as ydl:
    # ydl.in
    info_playlist = ydl.extract_info('https://www.youtube.com/playlist?list=PL7T6cfreEgTCW8nIEOjg1XsgQ5zf086u4', download=True)
    yt_id, title = info['id'], info['title']
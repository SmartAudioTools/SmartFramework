from SmartFramework.files import joinPath
from SmartFramework.web import is_connected, wait_connection_fonction
import os
import yt_dlp as youtube_dl

# import youtube_dl

DownloadError = youtube_dl.utils.DownloadError
# # mise à jour de youtube_dl
# fou la merde ......
# import pip._internal
# try:
##    # pip._internal.main(["install", "youtube_dl", "--upgrade"])
#    pip._internal.main(["install", "yt_dlp", "--upgrade"])
# except:
#    pass

# from youtube_dl.utils.DownloadError


def videoDownload(
    links, pathTemplate="%(title)s.%(ext)s", folder=None, wait_connection=False
):

    if wait_connection:
        wait_connection_fonction()

    if isinstance(links, str):
        links = [links]
    if folder is not None:
        pathTemplate = joinPath(folder, pathTemplate)

    ydl_opts = {
        "outtmpl": pathTemplate,
        "writeautomaticsub": True,
        "writesubtitles": True,
        "subtitleslangs": ["fr"],
        "skip_download": False,
        "format": "bestvideo+bestaudio",
        "cookiefile": f"{os.path.dirname(__file__)}/youtube.com_cookies.txt",
    }

    for link in links:
        succed = False
        while not succed:
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([link])
                succed = True
            except DownloadError:
                if wait_connection and not is_connected():
                    wait_connection_fonction()
                else:
                    raise


if __name__ == "__main__":
    pass

    # youtube_dl = get_youtub_dl()
    # youtube_dl.main(["", "URL", "https://www.youtube.com/watch?v=bsvE1HZ1fjU"])

    videoDownload(["https://www.youtube.com/watch?v=2YfwjngH9Y0"])

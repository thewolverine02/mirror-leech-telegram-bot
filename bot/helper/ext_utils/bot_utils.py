from re import match, findall
from threading import Thread, Event
from time import time
from math import ceil
from psutil import virtual_memory, cpu_percent, disk_usage
from requests import head as rhead
from urllib.request import urlopen
from telegram import InlineKeyboardMarkup

from bot.helper.telegram_helper.bot_commands import BotCommands
from bot import download_dict, download_dict_lock, STATUS_LIMIT, botStartTime
from bot.helper.telegram_helper.button_build import ButtonMaker

MAGNET_REGEX = r"magnet:\?xt=urn:btih:[a-zA-Z0-9]*"

URL_REGEX = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+"

COUNT = 0
PAGE_NO = 1


class MirrorStatus:
    STATUS_UPLOADING = "𝐔𝐩𝐥𝐨𝐚𝐝𝐢𝐧𝐠...📤"
    STATUS_DOWNLOADING = "𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠...📥"
    STATUS_CLONING = "𝐂𝐥𝐨𝐧𝐢𝐧𝐠...♻️"
    STATUS_WAITING = "𝐐𝐮𝐞𝐮𝐞𝐝...💤"
    STATUS_FAILED = "𝐅𝐚𝐢𝐥𝐞𝐝🚫.𝐂𝐥𝐞𝐚𝐧𝐢𝐧𝐠 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝..."
    STATUS_PAUSE = "𝐏𝐚𝐮𝐬𝐞𝐝...⛔️"
    STATUS_ARCHIVING = "𝐀𝐫𝐜𝐡𝐢𝐯𝐢𝐧𝐠...🔐"
    STATUS_EXTRACTING = "𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐢𝐧𝐠...📂"
    STATUS_SPLITTING = "𝐒𝐩𝐥𝐢𝐭𝐭𝐢𝐧𝐠...✂️"
    STATUS_CHECKING = "𝐂𝐡𝐞𝐜𝐤𝐢𝐧𝐠𝐔𝐩...📝"
    STATUS_SEEDING = "𝐒𝐞𝐞𝐝𝐢𝐧𝐠...🌧"

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']


class setInterval:
    def __init__(self, interval, action):
        self.interval = interval
        self.action = action
        self.stopEvent = Event()
        thread = Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time() + self.interval
        while not self.stopEvent.wait(nextTime - time()):
            nextTime += self.interval
            self.action()

    def cancel(self):
        self.stopEvent.set()

def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{SIZE_UNITS[index]}'
    except IndexError:
        return 'File too large'

def getDownloadByGid(gid):
    with download_dict_lock:
        for dl in list(download_dict.values()):
            status = dl.status()
            if (
                status
                not in [
                    MirrorStatus.STATUS_ARCHIVING,
                    MirrorStatus.STATUS_EXTRACTING,
                    MirrorStatus.STATUS_SPLITTING,
                ]
                and dl.gid() == gid
            ):
                return dl
    return None

def getAllDownload():
    with download_dict_lock:
        for dlDetails in list(download_dict.values()):
            status = dlDetails.status()
            if (
                status
                not in [
                    MirrorStatus.STATUS_ARCHIVING,
                    MirrorStatus.STATUS_EXTRACTING,
                    MirrorStatus.STATUS_SPLITTING,
                    MirrorStatus.STATUS_CLONING,
                    MirrorStatus.STATUS_UPLOADING,
                    MirrorStatus.STATUS_CHECKING,
                ]
                and dlDetails
            ):
                return dlDetails
    return None

def get_progress_bar_string(status):
    completed = status.processed_bytes() / 8
    total = status.size_raw() / 8
    p = 0 if total == 0 else round(completed * 100 / total)
    p = min(max(p, 0), 100)
    cFull = p // 8
    p_str = '●' * cFull
    p_str += '○' * (12 - cFull)
    p_str = f"[{p_str}]"
    return p_str

def get_readable_message():
    with download_dict_lock:
        msg = ""
        dlspeed_bytes = 0
        uldl_bytes = 0
        START = 0
        if STATUS_LIMIT is not None:
            tasks = len(download_dict)
            global pages
            pages = ceil(tasks/STATUS_LIMIT)
            if PAGE_NO > pages and pages != 0:
                globals()['COUNT'] -= STATUS_LIMIT
                globals()['PAGE_NO'] -= 1
            START = COUNT
        for index, download in enumerate(list(download_dict.values())[START:], start=1):
            msg += f"<b>▬▬▬ @LinkZz_MBBS ▬▬▬</b>\n"
            msg += f"<b>𝗡𝗮𝗺𝗲:</b> <code>{download.name()}</code>"
            msg += f"\n<b>𝗦𝘁𝗮𝘁𝘂𝘀:</b> <i>{download.status()}</i>"
            if download.status() not in [
                MirrorStatus.STATUS_ARCHIVING,
                MirrorStatus.STATUS_EXTRACTING,
                MirrorStatus.STATUS_SPLITTING,
                MirrorStatus.STATUS_SEEDING,
            ]:
                msg += f"\n{get_progress_bar_string(download)} {download.progress()}"
                if download.status() == MirrorStatus.STATUS_CLONING:
                    msg += f"\n<b>𝗖𝗹𝗼𝗻𝗲𝗱:</b> {get_readable_file_size(download.processed_bytes())} of {download.size()}"
                elif download.status() == MirrorStatus.STATUS_UPLOADING:
                    msg += f"\n<b>𝗨𝗽𝗹𝗼𝗮𝗱𝗲𝗱:</b> {get_readable_file_size(download.processed_bytes())} of {download.size()}"
                else:
                    msg += f"\n<b>𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱𝗲𝗱:</b> {get_readable_file_size(download.processed_bytes())} of {download.size()}"
                msg += f"\n<b>𝗦𝗽𝗲𝗲𝗱:</b> {download.speed()} | <b>𝗘𝗧𝗔:</b> {download.eta()}"
                try:
                    msg += f"\n<b>𝗦𝗲𝗲𝗿𝘀:</b> {download.aria_download().num_seeders}" \
                           f" | <b>𝗣𝗲𝗲𝗿𝘀:</b> {download.aria_download().connections}"
                except:
                    pass
                try:
                    msg += f"\n<b>𝗦𝗲𝗲𝗱𝗲𝗿𝘀:</b> {download.torrent_info().num_seeds}" \
                           f" | <b>𝗟𝗲𝗲𝗰𝗵𝗲𝗿𝘀:</b> {download.torrent_info().num_leechs}"
                except:
                    pass
                msg += f"\n<b> 𝗧𝗼 𝗖𝗮𝗻𝗰𝗲𝗹:</b> <code>/{BotCommands.CancelMirror} {download.gid()}</code>"
            elif download.status() == MirrorStatus.STATUS_SEEDING:
                msg += f"\n<b>𝗦𝗶𝘇𝗲: </b>{download.size()}"
                msg += f"\n<b>𝗦𝗽𝗲𝗲𝗱: </b>{get_readable_file_size(download.torrent_info().upspeed)}/s"
                msg += f" | <b>𝗨𝗽𝗹𝗼𝗮𝗱𝗲𝗱: </b>{get_readable_file_size(download.torrent_info().uploaded)}"
                msg += f"\n<b>𝗥𝗮𝘁𝗶𝗼: </b>{round(download.torrent_info().ratio, 3)}"
                msg += f" | <b>𝗧𝗶𝗺𝗲: </b>{get_readable_time(download.torrent_info().seeding_time)}"
                msg += f"\n<b> 𝗧𝗼 𝗖𝗮𝗻𝗰𝗲𝗹:</b> <code>/{BotCommands.CancelMirror} {download.gid()}</code>"
            else:
                msg += f"\n<b>𝗦𝗶𝘇𝗲: </b>{download.size()}"
            msg += "\n\n"
            if STATUS_LIMIT is not None and index == STATUS_LIMIT:
                break
        total, used, free, _ = disk_usage('.')
        free = get_readable_file_size(free)
        currentTime = get_readable_time(time() - botStartTime)
        bmsg = f"<b>𝗖𝗣𝗨:</b> {cpu_percent()}% | <b>𝗙𝗥𝗘𝗘:</b> {free}"
        for download in list(download_dict.values()):
            speedy = download.speed()
            if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                if 'K' in speedy:
                    dlspeed_bytes += float(speedy.split('K')[0]) * 1024
                elif 'M' in speedy:
                    dlspeed_bytes += float(speedy.split('M')[0]) * 1048576
            if download.status() == MirrorStatus.STATUS_UPLOADING:
                if 'KB/s' in speedy:
                    uldl_bytes += float(speedy.split('K')[0]) * 1024
                elif 'MB/s' in speedy:
                    uldl_bytes += float(speedy.split('M')[0]) * 1048576
        dlspeed = get_readable_file_size(dlspeed_bytes)
        ulspeed = get_readable_file_size(uldl_bytes)
        bmsg += f"\n<b>𝗥𝗔𝗠:</b> {virtual_memory().percent}% | <b>𝗨𝗣𝗧𝗜𝗠𝗘:</b> {currentTime}"
        bmsg += f"\n<b>𝗗𝗟🔻:</b> {dlspeed}/s | <b>𝗨𝗟🔺:</b> {ulspeed}/s"
        if STATUS_LIMIT is not None and tasks > STATUS_LIMIT:
            msg += f"<b>📖𝗣𝗮𝗴𝗲:</b> {PAGE_NO}/{pages} | <b>📝𝗧𝗮𝘀𝗸𝘀:</b> {tasks}\n"
            buttons = ButtonMaker()
            buttons.sbutton("⏪𝗣𝗥𝗘𝗩𝗜𝗢𝗨𝗦", "status pre")
            buttons.sbutton("𝗡𝗘𝗫𝗧⏩", "status nex")
            button = InlineKeyboardMarkup(buttons.build_menu(2))
            return msg + bmsg, button
        return msg + bmsg, ""

def turn(data):
    try:
        with download_dict_lock:
            global COUNT, PAGE_NO
            if data[1] == "nex":
                if PAGE_NO == pages:
                    COUNT = 0
                    PAGE_NO = 1
                else:
                    COUNT += STATUS_LIMIT
                    PAGE_NO += 1
            elif data[1] == "pre":
                if PAGE_NO == 1:
                    COUNT = STATUS_LIMIT * (pages - 1)
                    PAGE_NO = pages
                else:
                    COUNT -= STATUS_LIMIT
                    PAGE_NO -= 1
        return True
    except:
        return False

def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d'
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h'
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m'
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

def is_url(url: str):
    url = findall(URL_REGEX, url)
    return bool(url)

def is_gdrive_link(url: str):
    return "drive.google.com" in url

def is_gdtot_link(url: str):
    url = match(r'https?://.*\.gdtot\.\S+', url)
    return bool(url)

def is_mega_link(url: str):
    return "mega.nz" in url or "mega.co.nz" in url

def get_mega_link_type(url: str):
    if "folder" in url:
        return "folder"
    elif "file" in url:
        return "file"
    elif "/#F!" in url:
        return "folder"
    return "file"

def is_magnet(url: str):
    magnet = findall(MAGNET_REGEX, url)
    return bool(magnet)

def new_thread(fn):
    """To use as decorator to make a function call threaded.
    Needs import
    from threading import Thread"""

    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper

def get_content_type(link: str):
    try:
        res = rhead(link, allow_redirects=True, timeout=5)
        content_type = res.headers.get('content-type')
    except:
        content_type = None

    if content_type is None:
        try:
            res = urlopen(link, timeout=5)
            info = res.info()
            content_type = info.get_content_type()
        except:
            content_type = None
    return content_type


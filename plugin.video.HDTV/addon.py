import json
import os
import re
import sys
import time
import traceback
import urllib
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

# End of Imports
#
# Setting up basic Variables for XBMC ####
__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')

addon_id = 'plugin.video.HDTV'
selfAddon = xbmcaddon.Addon(id=addon_id)
profile_path = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
addonPath = xbmcaddon.Addon().getAddonInfo('path')
addonversion = xbmcaddon.Addon().getAddonInfo('version')
sys.path.append(os.path.join(addonPath, 'resources', 'lib'))


# Initializing the settings ###
if not selfAddon.getSetting('dummy') == 'true':
    selfAddon.setSetting('dummy', 'true')


# Define settting function ###
def show_settings():
    selfAddon.openSettings()


# End of Addon Class info and setting ####

##### Define General Functions #####
def convert(s):
    try:
        return s.group(0).encode('latin1').decode('utf8')
    except:
        return s.group(0)


# Define function to monitor real time parameters ###
def get_params():
    param = []
    paramstring = sys.argv[2]
    print
    sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if params[len(params) - 1] == '/':
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param


# Define Addon specific Functions
def add_directory(name, url, mode, iconimage, isItFolder=True):
    u = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=iconimage)
    liz.setInfo(type='Video', infoLabels={'Title': name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isItFolder)

    return ok


def add_types():
    m3_list = readM3u(addonPath + '\list.m3u')
    playlist_group = []

    for i in m3_list:
        if i is None:
            continue
        else:
            playlist_group.append(i['tvg-group'])

    playlist_group = list(dict.fromkeys(playlist_group))
    playlist_group.sort()
    for i in playlist_group:
        add_directory(i, i, 2, '')

    add_directory('Settings', 'Settings', 99, 'OverlayZIP.png', isItFolder=False)
    return


def add_channels(group_name):
    playlist_tracks = readM3u(addonPath + '\list.m3u')
    for i in playlist_tracks:
        if i is None:
            continue
        else:
            ch_group = i['tvg-group']
            ch_name = i['tvg-name']
            ch_url = i['link']
            ch_icon = i['tvg-logo']
            if ch_group == group_name:
                add_directory(ch_name.encode('utf-8'), ch_url, 3, ch_icon, isItFolder=False)
    return

def play_url(media_url):
    playlist = xbmc.PlayList(1)
    playlist.clear()
    listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
    listitem.setInfo("Video", {"Title": name})
    listitem.setProperty('mimetype', 'video/x-msvideo')
    listitem.setProperty('IsPlayable', 'true')
    playlist.add(media_url, listitem)
    xbmcgui.Dialog().notification(__addonname__, "Playing  Video", __icon__, 3000, False)
    xbmc.Player().play(playlist)

def readM3u(m3u_url):
    m3lines = readAllLines(m3u_url)
    m3_list = parseFile(m3lines)
    return m3_list


def readAllLines(m3u_url):
    m3lines = [line.rstrip('\n') for line in open(m3u_url)]
    return m3lines


def parseFile(m3lines):
    m3_list = []
    numLine = len(m3lines)
    for n in range(numLine):
        line = m3lines[n]
        if line[0] == "#":
            m3_list.append(manageLine(m3lines, n))

    return m3_list


def manageLine(m3lines, n):
    lineInfo = m3lines[n]
    lineLink = m3lines[n + 1]
    if lineInfo != "#EXTM3U":
        m = re.search("tvg-name=\"(.*?)\"", lineInfo)
        name = m.group(1)
        m = re.search("tvg-ID=\"(.*?)\"", lineInfo)
        id = m.group(1)
        m = re.search("tvg-logo=\"(.*?)\"", lineInfo)
        logo = m.group(1)
        m = re.search("group-title=\"(.*?)\"", lineInfo)
        group = m.group(1)
        m = re.search("[,](?!.*[,])(.*?)$", lineInfo)
        title = m.group(1)
        # ~ print(name+"||"+id+"||"+logo+"||"+group+"||"+title)

        test = {
            "title": title,
            "tvg-name": name,
            "tvg-ID": id,
            "tvg-logo": logo,
            "tvg-group": group,
            "titleFile": os.path.basename(lineLink),
            "link": lineLink
        }
        return test


# Start of MAIN Code
params = get_params()
url = None
name = None
mode = None

# noinspection PyBroadException
try:
    url = urllib.unquote_plus(params['url'])
except:
    pass
# noinspection PyBroadException
try:
    name = urllib.unquote_plus(params['name'])
except:
    pass
# noinspection PyBroadException
try:
    mode = int(params['mode'])
except:
    pass

print
params
args = urlparse.parse_qs(sys.argv[2][1:])
print
name, url, mode

# noinspection PyBroadException
try:
    if mode is None or url is None or len(url) < 1:
        add_types()
    elif mode == 2:
        add_channels(name)
    elif mode == 3:
        play_url(url)
    elif mode == 99:
        show_settings()

except:
    print
    'Something dint work'
    traceback.print_exc(file=sys.stdout)

if not (mode == 3):
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
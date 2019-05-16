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
profile_path = xbmc.translatePath(selfAddon.getAddonInfo('profile')).decode("utf-8")
addonPath = xbmcaddon.Addon().getAddonInfo('path')
addonversion = xbmcaddon.Addon().getAddonInfo('version')
sys.path.append(os.path.join(addonPath, 'resources', 'lib'))
service_addon = addonPath + '/service.py'
cacheDir = os.path.join(profile_path, "cache")
if not os.path.exists(cacheDir):
    os.makedirs(cacheDir)

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

def EXIT():
        xbmc.executebuiltin("XBMC.Container.Update(path,replace)")
        xbmc.executebuiltin("XBMC.ActivateWindow(Home)")

# Define Addon specific Functions
def add_directory(name, url, mode, iconimage, isItFolder=True):
    u = sys.argv[0] + '?url=' + urllib.quote_plus(url) + '&mode=' + str(mode) + '&name=' + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage='DefaultFolder.png', thumbnailImage=iconimage)
    liz.setInfo(type='Video', infoLabels={'Title': name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isItFolder)

    return ok


def add_types():
    add_directory('Refresh Database', 'Refresh_Database', 2, '')

    try:
        with open(cacheDir + '/groups.txt') as data_file:
            group_list = data_file.readlines()

    except:
        xbmcgui.Dialog().ok('World Wide HD Service', 'Loading Cache..... ',
                           'Please Wait Untill Cache is updated.')
        EXIT()

    for i in group_list:
        if i:
            i = i.strip()
            add_directory(i, i, 2, '')

    add_directory('Settings', 'Settings', 99, 'OverlayZIP.png', isItFolder=False)
    return


def add_channels(group_name):
    if group_name == 'Refresh Database':
        xbmc.executebuiltin('XBMC.RunScript(' + service_addon + ')')
    else:
        with open(cacheDir + '/channels.json') as data_file:
            playlist_tracks = json.loads(data_file.read())

        for i in range(0, len(playlist_tracks)):
            if playlist_tracks[i]:
                if playlist_tracks[i]['tvg-group'].encode("utf-8") == group_name:
                    ch_name = playlist_tracks[i]['tvg-name'].encode("utf-8")
                    ch_url = playlist_tracks[i]['link'].encode("utf-8")
                    ch_icon = playlist_tracks[i]['tvg-logo'].encode("utf-8")
                    add_directory(ch_name, ch_url, 3, ch_icon, isItFolder=False)

    return


def play_url(media_url):
    playlist = xbmc.PlayList(1)
    playlist.clear()
    listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
    listitem.setInfo("Video", {"Title": name})
    listitem.setProperty('mimetype', 'video/x-msvideo')
    listitem.setProperty('IsPlayable', 'true')
    playlist.add(media_url, listitem)
    xbmcgui.Dialog().notification(__addonname__, "Please Wait: Loading Video", __icon__, 3000, False)
    xbmc.Player().play(playlist)


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

with open(profile_path + '/runtime', 'r') as fout:
    script_time = float(fout.readline())
    if time.time() > (script_time + 1800):
        xbmc.executebuiltin('XBMC.RunScript(' + service_addon + ')')

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
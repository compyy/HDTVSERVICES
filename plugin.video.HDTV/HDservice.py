import json
import os
import re
import time
import urllib
import xbmc
import xbmcaddon
import xbmcgui

#
addon_id = 'plugin.video.HDTV'
selfAddon = xbmcaddon.Addon(id=addon_id)
addonPath = selfAddon.getAddonInfo("path")
profile_path = xbmc.translatePath(selfAddon.getAddonInfo('profile')).decode("utf-8")
cacheDir = os.path.join(profile_path, "cache")
if not os.path.exists(cacheDir):
    os.makedirs(cacheDir)

cachem3u = cacheDir + '/m3u8file'

# Initializing the settings ###
if not selfAddon.getSetting('dummy') == 'true':
    selfAddon.setSetting('dummy', 'true')


# Define settting function ###
def show_settings():
    selfAddon.openSettings()


###
def DownloaderClass(url, cachem3u):
    dp = xbmcgui.DialogProgress()
    dp.create("HDTV Cache", "Updating Cache File..!", url)
    try:
        (f, headers) = MyURLopener().retrieve(url, cachem3u, lambda nb, bs, fs, url=url: _pbhook(nb, bs, fs, url, dp))
    except Exception as e:
        if e.errno == 'socket error':
            xbmcgui.Dialog().ok('World Wide HD Service', 'Cannot Update Cache',
                                'Unable to reach Server Try Again after 30 minutes or contact Support')
            exit()

        if e.args[1] == 404:
            xbmcgui.Dialog().ok('World Wide HD Service', 'Cannot Update Cache',
                                'Please check if Username/password is correct or contact Support')
            exit()

        xbmcgui.Dialog().ok('World Wide HD Service', 'Cannot Update Cache',
                            'Please contact Support')
        exit()


###
class MyURLopener(urllib.FancyURLopener):
    http_error_default = urllib.URLopener.http_error_default


def _pbhook(numblocks, blocksize, filesize, url=None, dp=None):
    try:
        percent = min((numblocks * blocksize * 100) / filesize, 100)
        print(percent)
        dp.update(percent)
    except:
        percent = 100
        print(percent)
        dp.update(percent)

    if dp.iscanceled():
        print('DOWNLOAD CANCELLED')
        dp.close()


###

def update_m3u():
    print("[ " + addon_id + " ] Updating Cache")
    username = selfAddon.getSetting('USERNAME')
    password = selfAddon.getSetting('PASSWORD')
    url = 'http://ip.sltv.be:8000/get.php?username=' + username + '&password=' + password + '&type=m3u_plus&output=ts'
    DownloaderClass(url, cachem3u)
    m3_list = readM3u(cachem3u)
    playlist_group = []

    for i in m3_list:
        if i is None:
            continue
        else:
            playlist_group.append(i['tvg-group'])

    playlist_group = list(dict.fromkeys(playlist_group))
    playlist_group.sort()
    with open(cacheDir + '/groups.txt', 'w') as fout:
        for i in playlist_group:
            if i:
                fout.write(i)
                fout.write('\n')

    with open(cacheDir + '/channels.json', 'w') as fout:
        json.dump(m3_list, fout)
        with open(profile_path + '/runtime', 'w') as fout:
            fout.write(str(time.time()))

    return


def readM3u(cachem3u):
    m3lines = readAllLines(cachem3u)
    m3_list = parsem3u(m3lines)
    return m3_list


def readAllLines(cachem3u):
    m3lines = [line.rstrip('\n') for line in open(cachem3u)]
    return m3lines


def parsem3u(m3lines):
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

        m3dict = {
            "title": title,
            "tvg-name": name,
            "tvg-ID": id,
            "tvg-logo": logo,
            "tvg-group": group,
            "titleFile": os.path.basename(lineLink),
            "link": lineLink
        }
        return m3dict


###

#
###
if (selfAddon.getSetting('USERNAME') == '') or (selfAddon.getSetting('PASSWORD') == ''):
    xbmcgui.Dialog().ok('World Wide HD Service', 'Account Details Missing: ',
                        'You Must Enter Valid Username and Password to view the Channels')

    with open(profile_path + '/runtime', 'w') as fout:
        fout.write(str(time.time() - 1800))

    show_settings()

with open(profile_path + '/runtime', 'r') as fout:
    script_time = float(fout.readline())
    if time.time() > (script_time + 1800):
        update_m3u()

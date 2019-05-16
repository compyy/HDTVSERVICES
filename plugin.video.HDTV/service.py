import base64
import datetime
import json
import re
import sys
import time
import os
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcgui

#
addon_id = 'plugin.video.HDTV'
selfAddon = xbmcaddon.Addon(id=addon_id)
addonPath = selfAddon.getAddonInfo("path")
profile_path = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
cacheDir = os.path.join(profile_path, "cache")
if not os.path.exists(cacheDir):
    os.makedirs(cacheDir)

# Initializing the settings ###
if not selfAddon.getSetting('dummy') == 'true':
    selfAddon.setSetting('dummy', 'true')


# Define settting function ###
def show_settings():
    selfAddon.openSettings()


###

def update_m3u():
    username = selfAddon.getSetting('USERNAME')
    password = selfAddon.getSetting('PASSWORD')
    url = 'http://ip.sltv.be:8000/get.php?username='+username+'&password='+password+'&type=m3u&output=ts'
    c = urllib3.PoolManager()

    with c.request('GET', url, preload_content=False) as resp, open(filename, 'wb') as out_file:
        shutil.copyfileobj(resp, out_file)

    resp.release_conn()


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


###

#
###
if (selfAddon.getSetting('USERNAME') == '') & (selfAddon.getSetting('PASSWORD') == ''):
    xbmcgui.Dialog().ok('You Must Enter Valid Username and Password to view the channels')
    show_settings()

else:
    update_m3u()
    with open(profile_path + '/runtime', 'w') as fout:
        fout.write(str(time.time()))
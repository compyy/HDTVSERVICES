# -*- coding: utf-8 -*-

import xbmc

# Setting up basic Variables for XBMC ####
__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')

addon_id = 'plugin.video.HDTV'
selfAddon = xbmcaddon.Addon(id=addon_id)
profile_path = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
addonPath = xbmcaddon.Addon().getAddonInfo("path")
addonversion = xbmcaddon.Addon().getAddonInfo("version")
sys.path.append(os.path.join(addonPath, 'resources', 'lib'))

# Initializing the settings ###
if not selfAddon.getSetting("dummy") == "true":
    selfAddon.setSetting("dummy", "true")

# Define setting function ###
def show_settings():
    selfAddon.openSettings()

username = selfAddon.getSetting('USERNAME')
password = selfAddon.getSetting('PASSWORD')

url = 'http://ip.sltv.be:8000/get.php?username='+username+'&password='+password+'&type=m3u&output=ts'
xbmc.Player().play(url)
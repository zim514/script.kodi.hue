# -*- coding: utf-8 -*-

import logging
import sys
from threading import Event

import xbmc
import xbmcaddon
from xbmcgui import NOTIFICATION_ERROR, NOTIFICATION_WARNING, NOTIFICATION_INFO
import xbmcgui

from KodiGroup import KodiGroup
import globals
import kodiHue
import kodiutils
import qhue
from resources.lib.globals import NUM_GROUPS


# from resources.lib.qhue import Bridge
ADDON = xbmcaddon.Addon()
logger = logging.getLogger(ADDON.getAddonInfo('id'))

connected = False
settingsChanged = False



#===============================================================================
# ev = Event()
# capture = xbmc.RenderCapture()
# fmt = capture.getImageFormat()
# # BGRA or RGBA
# fmtRGBA = fmt == 'RGBA'
#===============================================================================



def menu():
    logger.info("Kodi Hue:  menu started, version: {}".format(ADDON.getAddonInfo('version')))
    monitor = kodiHue.HueMonitor()

    if len(sys.argv) == 2:
        args = sys.argv[1]
    else: 
        args = ""

    logger.info("Kodi Hue: Args: {}".format(args))

    if args == "discover":
        logger.info("Kodi Hue: Started with Discovery")
        bridge = kodiHue.bridgeDiscover(monitor)
        if bridge:
            service() #restart service
    
    elif args == "createHueGroup":
        logger.info("Kodi Hue: Started with createGroup")
        bridge = kodiHue.connectBridge(monitor, silent=True)
        if bridge:
            kodiHue.createHueGroup(bridge)
        else: 
            logger.info("Kodi Hue: Menu() createGroup: No bridge") 

    elif args == ("deleteHueGroup"):
        
        logger.info("Kodi Hue: Started with deleteGroup.")
        
        bridge = kodiHue.connectBridge(monitor, silent=True)  # don't rediscover, proceed silently
        if bridge:
            
            kodiHue.deleteHueGroup(bridge)
        else:
            logger.info("Kodi Hue: No bridge found. deleteGroup cancelled.")

    elif args.startswith("groupSelect"):
        kgroup = args.split("=", 1)[1]
        logger.info("Kodi Hue: Started with groupSelect. args: {}, kgroup: {}".format(args, kgroup))
        
        bridge = kodiHue.connectBridge(monitor, silent=True)  # don't rediscover, proceed silently
        if bridge:
            kodiHue.configureGroup(bridge, kgroup)
        else:
            logger.info("Kodi Hue: No bridge found. Select group cancelled.")
    
    
    else:
        ADDON.openSettings()
         
    
    
    


##################################################
# # RUN
###################
def service():
    logger.info("Kodi Hue:  service started, version: {}".format(ADDON.getAddonInfo('version')))
    monitor = kodiHue.HueMonitor()
    
    initialFlash = kodiutils.get_setting_as_bool("initialFlash")
    globals.forceOnSunset = kodiutils.get_setting_as_bool("forceOnSunset")
    globals.daylightDisable = kodiutils.get_setting_as_bool("daylightDisable")
    
    bridgeIP = ""
    bridgeUser = ""

    if len(sys.argv) == 2:
        args = sys.argv[1]
    else: 
        args = ""
    
    logger.info("Kodi Hue: Args: {}".format(args))


    logger.info("Kodi Hue: Main service started...")
    bridge = kodiHue.connectBridge(monitor,silent=False)
            
    if bridge:
        globals.settingsChanged = False
        globals.daylight = kodiHue.getDaylight(bridge)
        kgroups = kodiHue.setupGroups(bridge,initialFlash)

        timer = 1
        # #Ready to go! Start running until Kodi exit.            
        while globals.connected and not monitor.abortRequested():
            
            if globals.settingsChanged:
                reloadFlash = kodiutils.get_setting_as_bool("reloadFlash")
                forceOnSunset = kodiutils.get_setting_as_bool("forceOnSunset")
                globals.daylightDisable = kodiutils.get_setting_as_bool("daylightDisable")
                kgroups = kodiHue.setupGroups(bridge, reloadFlash)
                globals.settingsChanged = False
            
            timer = timer + 1
            if timer > 59:
                previousDaylight = kodiHue.getDaylight(bridge)
                logger.info('Kodi Hue: Daylight check: current: {}, previous: {}'.format(globals.daylight, previousDaylight))
                if globals.daylight != previousDaylight :
                    logger.info('Kodi Hue: Daylight change! current: {}, previous: {}'.format(globals.daylight, previousDaylight))
                    #oooh daylight changed.
                    globals.daylight = kodiHue.getDaylight(bridge)
                    if not globals.daylight:
                        kodiHue.sunset(bridge,kgroups)
                
                logger.info('Kodi Hue: Service running...')
                timer = 1
                

            
            monitor.waitForAbort(1)
        logger.info('Kodi Hue: Process exiting...')
        return
        
    else:
        logger.info('Kodi Hue: No connected bridge, exiting...')
        return
    
            
         

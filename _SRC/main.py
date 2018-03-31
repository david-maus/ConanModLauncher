#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Conan Mod Launcher.

by David Maus/neslane at www.gef-gaming.de
"""

# ---------------------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------------------

import os
import sys
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon
from ui import resources
from datetime import datetime, time
from time import sleep
import psutil
import subprocess
from configparser import ConfigParser
import pysteamcmd
import pathlib
import webbrowser
import re
import win32serviceutil
from glob import glob
from modules import design, functions, getSteamWorkshopMods


# ---------------------------------------------------------------------------------------
# Global
# ---------------------------------------------------------------------------------------

__author__  = "David MAus"
__version__ = "0.1.0"
__license__ = "MIT"
__title__   = 'Conan Mod Launcher ' +  __version__ + ' - by GEF-GAMING.DE'

# ---------------------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------------------

sys.dont_write_bytecode = True
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# ---------------------------------------------------------------------------------------
# Get & Set Pathes
# ---------------------------------------------------------------------------------------


def getCurrentExecFolder():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.abspath(os.path.dirname(__file__))


def getCurrentRootFolder():
    if getattr(sys, 'frozen', False):
        currentRootFolder = os.path.dirname(sys.executable)
        return os.path.join(currentRootFolder)
    else:
        currentRootFolder = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(currentRootFolder, '../')


def resource_path(relative_path):
    """Get Absolute Path."""
    base_path = getattr(sys, '_MEIPASS',
                        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


uiFilePath          = resource_path("ui/interface.ui")
iconFilePath        = resource_path("ui/main.ico")
currentExecFolder   = getCurrentExecFolder()
currentRootFolder   = getCurrentRootFolder()
settingsPath        = os.path.join(currentRootFolder, 'data', 'settings.ini')


# ---------------------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------------------


class mainWindow(QtWidgets.QDialog):
    """Make Main Window."""

    def __init__(self):
        """Initialize Main Window."""

        super(mainWindow, self).__init__()

        # Load UI File
        uic.loadUi(uiFilePath, self)

        # Set Values
        self.linePath.setText(ConanPath)
        self.lineModPath.setText(modpath)
        self.lineSteamPath.setText(steamPath)
        self.lineParamters.setText(parameters)
        self.lineCollection.setText(collection)


        # Button Mapping
        self.buttonPath.clicked.connect(self.saveFileDialog)
        self.buttonModPath.clicked.connect(self.saveFileDialogMods)
        self.buttonSteamPath.clicked.connect(self.saveFileDialogSteam)
        self.buttonSave.clicked.connect(self.saveConfig)

        self.buttonStartGame.clicked.connect(self.startGame)

        self.buttonInstallMods.clicked.connect(lambda: installMods())

        # eventFilter
        self.headerLogo.installEventFilter(self)



    def saveFileDialog(self):
        my_dir = QFileDialog.getExistingDirectory(self, "Open a folder", ConanPath, QFileDialog.ShowDirsOnly)
        if(my_dir == ''):
            my_dir = ConanPath

        else:
            self.linePath.setText(my_dir)
            self.saveConfig()

    def saveFileDialogMods(self):
        my_dir = QFileDialog.getExistingDirectory(self, "Open a folder", ConanPath, QFileDialog.ShowDirsOnly)
        if(my_dir == ''):
            my_dir = modpath

        else:
            self.lineModPath.setText(my_dir)
            self.saveConfig()

    def saveFileDialogSteam(self):
        my_dir = QFileDialog.getExistingDirectory(self, "Open a folder", ConanPath, QFileDialog.ShowDirsOnly)
        if(my_dir == ''):
            my_dir = steamPath

        else:
            self.lineSteamPath.setText(my_dir)
            self.saveConfig()


    def startGame(self):

        if('http' in collection):
            collectionID = re.compile(r'(\d+)$').search(collection).group(1)
        else:
            collectionID = collection
        ServerAdress = getSteamWorkshopMods.getSteamModsFromCollection(collectionID).getConnectionInfo()

        if(':' in ServerAdress):
            connectParameter = ' +connect ' + ServerAdress
        else:
            connectParameter = ''

        steamExePath = os.path.join(steamPath, 'steam.exe')

        conanParameters = ' -applaunch 440900 -silent ' \
                          + connectParameter \
                          + ' ' \
                          + parameters

        print(steamExePath + conanParameters)
        self.StartGameThread_T = StartGameThread(steamExePath, conanParameters)

        self.StartGameThread_T.start()


    def saveConfig(self):
        my_dir = self.linePath.text()
        modpath = self.lineModPath.text()
        steamPath = self.lineSteamPath.text()
        parameters = self.lineParamters.text()
        collection = self.lineCollection.text()


        writeSettings(my_dir, modpath, steamPath, parameters, collection)
        readSettings()

    def eventFilter(self, target, event):
        """Start Main Function."""
        if target == self.headerLogo and event.type() == QtCore.QEvent.MouseButtonPress:
            self.openURL()

        return False

    def openURL(self):
        """Start Main Function."""
        webbrowser.open_new_tab('http://www.gef-gaming.de/forum')


# ---------------------------------------------------------------------------------------
# Main Functions
# ---------------------------------------------------------------------------------------


def readSettings():
    global ConanPath
    global modpath
    global steamPath
    global parameters
    global collection

    if os.path.isfile(settingsPath):

        config = ConfigParser()
        config.read(settingsPath, encoding='utf8')

        ConanPath = config['SETTINGS']['ConanPath']
        modpath = config['SETTINGS']['modpath']
        steamPath = config['SETTINGS']['steamPath']
        parameters = config['SETTINGS']['parameters']
        collection = config['SETTINGS']['collection']



    else:
        ConanPath = ''
        modpath = ''
        steamPath = ''
        parameters = ''
        collection = ''

        open(settingsPath, "w+").close()
        config = ConfigParser()
        config.read(settingsPath, encoding='utf8')
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'ConanPath', ConanPath)
        config.set('SETTINGS', 'modpath', modpath)
        config.set('SETTINGS', 'steamPath', steamPath)
        config.set('SETTINGS', 'parameters', parameters)
        config.set('SETTINGS', 'collection', collection)

        with open(settingsPath, 'w', encoding='utf8') as configfile:
            config.write(configfile)


def writeSettings(ConanPathNEW, modpathNEW, steamPathNEW, parametersNEW, collectionNEW):

    config = ConfigParser()
    config.read(settingsPath, encoding='utf8')

    config['SETTINGS']['ConanPath'] = ConanPathNEW
    config['SETTINGS']['modpath'] = modpathNEW
    config['SETTINGS']['steamPath'] = steamPathNEW
    config['SETTINGS']['parameters'] = parametersNEW
    config['SETTINGS']['collection'] = collectionNEW

    with open(settingsPath, 'w', encoding='utf8') as configfile:
        config.write(configfile)

    global ConanPath
    global modpath
    global steamPath
    global parameters
    global collection

    ConanPath = ConanPathNEW
    modpath = modpathNEW
    steamPath = steamPathNEW
    parameters = parametersNEW
    collection = collectionNEW

    readSettings()


def installMods():
    steamcmd_path = os.path.join(modpath, '_steamcmd_')
    gamepath = os.path.join(ConanPath)

    pathlib.Path(modpath).mkdir(parents=False, exist_ok=True)
    pathlib.Path(steamcmd_path).mkdir(parents=False, exist_ok=True)

    steamcmd = pysteamcmd.Steamcmd(steamcmd_path)
    steamcmd.install()

    if('http' in collection):
        collectionID = re.compile(r'(\d+)$').search(collection).group(1)
    else:
        collectionID = collection
    steamModlist = getSteamWorkshopMods.getSteamModsFromCollection(collectionID).getCollectionInfo()
    for mod in steamModlist:
        modID = mod[0]
        steamcmd.install_mods(gameid=440900, game_install_dir=modpath, user='anonymous', password=None, validate=True, modID=modID)

    modListFolder = os.path.join(gamepath, 'ConanSandbox', 'Mods')
    modListTXT = os.path.join(modListFolder, 'modlist.txt')
    modRootFolder = os.path.join(modpath, 'steamapps', 'workshop', 'content', '440900')
    if os.path.exists(modListFolder):
        if os.path.isfile(modListTXT):
            pass
        else:
            open(modListTXT, "w+").close()
    else:
        os.mkdir(modListFolder)
        open(modListTXT, "w+").close()

    with open(modListTXT, 'w', encoding='utf8') as modListTXTIO:
        for mod in steamModlist:
            modItemFolder = os.path.join(modRootFolder, mod[0])
            modFileName = os.listdir(modItemFolder)
            modFileName = ''.join(modFileName)
            modFullPath = os.path.join(modItemFolder, modFileName)
            print(modFullPath)
            modListTXTIO.write("*{}\n".format(modFullPath))


class StartGameThread(QThread):

    def __init__(self, steamExePath, conanParameters, parent=None):
        QThread.__init__(self)
        self.steamExePath = steamExePath
        self.conanParameters = conanParameters
        self.runs = True

    def __del__(self):
        self.wait()

    def stop(self):
        self.runs = False

    def run(self):
        if self.runs:
            steamExePath = str(self.steamExePath)
            conanParameters = str(self.conanParameters)
            serverexec = subprocess.Popen(steamExePath + conanParameters)


def startWindow():
    """Start Main Window UI."""

    m = mainWindow()

    # Show Window
    m.show()

    # Return to stay alive
    return m


def main():
    """Main entry point of the app."""
    # Read Settings
    readSettings()

    # Initialize Qt
    app = QtWidgets.QApplication(sys.argv)

    # Set design and colors
    design.QDarkPalette().set_app(app)

    # Initialize and start Window
    window = startWindow()

    # Set Window Title
    window.setWindowTitle(__title__)

    # Set Window Icon
    window.setWindowIcon(QtGui.QIcon(iconFilePath))

    # Close Window on exit
    sys.exit(app.exec_())


if __name__ == "__main__":
    """This is executed when run from the command line."""
    main()

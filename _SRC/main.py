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
from PyQt5.QtWidgets import QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from ui import resources
from datetime import datetime, time
from time import sleep
import psutil
import stat
import subprocess
from configparser import ConfigParser
import pysteamcmd
import pathlib
import webbrowser
import re
from pathlib import Path
import win32serviceutil
from glob import glob
from modules import design, functions, getSteamWorkshopMods


# ---------------------------------------------------------------------------------------
# Global
# ---------------------------------------------------------------------------------------

__author__  = "David MAus"
__version__ = "0.2.2"
__license__ = "MIT"
__title__   = 'Conan Mod Launcher ' +  __version__ + ' - by GEF-GAMING.DE / David Maus'

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
        self.progressBar.setValue(0)
        self.progressBar.setFormat('')


        # Button Mapping
        self.buttonPath.clicked.connect(self.saveFileDialog)
        self.buttonModPath.clicked.connect(self.saveFileDialogMods)
        self.buttonSteamPath.clicked.connect(self.saveFileDialogSteam)
        self.buttonStartGame.clicked.connect(self.startGame)
        self.buttonInstallMods.clicked.connect(self.installMods)
        self.buttonCollectionCheck.clicked.connect(self.checkMods)


        # eventFilter
        self.headerLogo.installEventFilter(self)


    def showErrorDialog(self, title, text):

        msg = QtWidgets.QMessageBox()
        # msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        # msg.setInformativeText("This is additional information")
        msg.setWindowTitle(title)
        # msg.setDetailedText("The details are as follows:")
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)

        result = msg.exec_()
        if result == QtWidgets.QMessageBox.Ok:
            self.on_count_change(0)
            self.on_count_changeStr('')
            self.buttonPath.setEnabled(True)
            self.buttonModPath.setEnabled(True)
            self.buttonSteamPath.setEnabled(True)
            self.buttonStartGame.setEnabled(True)
            self.buttonInstallMods.setEnabled(True)
            self.buttonCollectionCheck.setEnabled(True)

    def checkMods(self):
        self.on_count_change(0)
        self.on_count_changeStr('Checking Collection... please wait')

        self.saveConfig()
        self.buttonPath.setEnabled(False)
        self.buttonModPath.setEnabled(False)
        self.buttonSteamPath.setEnabled(False)
        self.buttonStartGame.setEnabled(False)
        self.buttonInstallMods.setEnabled(False)
        self.buttonCollectionCheck.setEnabled(False)
        self.CheckCollectionThread_T = CheckCollectionThread()
        self.CheckCollectionThread_T.finished.connect(lambda: self.showErrorDialog('ModCollection Info', msgMods))
        self.CheckCollectionThread_T.start()





    def closeEvent(self, event):
        self.saveConfig()



    def installMods(self):
        self.saveConfig()
        conanExeFile  = os.path.join(ConanPath, 'ConanSandbox.exe')
        if(modpath and collection and ConanPath):
            if os.path.exists(modpath) and os.path.exists(ConanPath):
                if Path(conanExeFile).is_file():
                    self.on_count_change(0)
                    self.installModsThread_T = installModsThread()
                    self.installModsThread_T.percent_signal.connect(self.on_count_change)
                    self.installModsThread_T.string_signal.connect(self.on_count_changeStr)
                    self.installModsThread_T.finished.connect(self.thread_finished)
                    self.installModsThread_T.start()

                    self.buttonPath.setEnabled(False)
                    self.buttonModPath.setEnabled(False)
                    self.buttonSteamPath.setEnabled(False)
                    self.buttonStartGame.setEnabled(False)
                    self.buttonInstallMods.setEnabled(False)
                    self.buttonCollectionCheck.setEnabled(False)
                else:
                    self.showErrorDialog('Invalid Directories', 'It seems your conanfolder is invalid (no conansandbox.exe found)')
            else:
                self.showErrorDialog('Path not found', 'Your Modfolder or Conan path was not found')
                # Modfolder exisitert nicht
        else:
            self.showErrorDialog('Emtpy fields', 'You have not entered a modfolder or your collection URL or your ConanFolder')
            # Modfolder Wert nicht ausgefüllt

    def on_count_change(self, value):
        self.progressBar.setValue(value)

    def on_count_changeStr(self, value):
        self.progressBar.setFormat(value)


    def thread_finished(self):
        self.buttonPath.setEnabled(True)
        self.buttonModPath.setEnabled(True)
        self.buttonSteamPath.setEnabled(True)
        self.buttonStartGame.setEnabled(True)
        self.buttonInstallMods.setEnabled(True)
        self.buttonCollectionCheck.setEnabled(True)


    def saveFileDialog(self):
        my_dir = QFileDialog.getExistingDirectory(self, "Choose your Conan Root Folder", ConanPath, QFileDialog.ShowDirsOnly)
        if(my_dir == ''):
            my_dir = ConanPath

        else:
            self.linePath.setText(my_dir)
            self.saveConfig()

    def saveFileDialogMods(self):
        my_dir = QFileDialog.getExistingDirectory(self, "Choose your Modfolder", ConanPath, QFileDialog.ShowDirsOnly)
        if(my_dir == ''):
            my_dir = modpath

        else:
            self.lineModPath.setText(my_dir)
            self.saveConfig()

    def saveFileDialogSteam(self):
        my_dir = QFileDialog.getExistingDirectory(self, "Choose your Steam Root Folder", ConanPath, QFileDialog.ShowDirsOnly)
        if(my_dir == ''):
            my_dir = steamPath

        else:
            self.lineSteamPath.setText(my_dir)
            self.saveConfig()


    def startGame(self):
        self.saveConfig()

        steamExeFile = os.path.join(steamPath, 'Steam.exe')
        conanExeFile  = os.path.join(ConanPath, 'ConanSandbox.exe')

        if(steamPath and ConanPath):
            if os.path.exists(steamPath) and os.path.exists(conanExeFile):
                if Path(steamExeFile).is_file() and Path(conanExeFile).is_file():
                    if('http' in collection):
                        collectionID = re.compile(r'(\d+)$').search(collection).group(1)
                    else:
                        collectionID = collection
                    self.on_count_change(0)
                    self.on_count_changeStr('Checking Collection for Serverinfo...')
                    ServerAdress = getSteamWorkshopMods.getSteamModsFromCollection(collectionID).getConnectionInfo()

                    if(':' in ServerAdress):
                        connectParameter = ' +connect ' + ServerAdress
                        self.on_count_changeStr('Starting Game on ' + ServerAdress)
                    else:
                        connectParameter = ''
                        self.on_count_changeStr('Starting Game...')
                    steamExePath = os.path.join(steamPath, 'steam.exe')

                    conanParameters = ' -applaunch 440900 -silent ' \
                                      + connectParameter \
                                      + ' ' \
                                      + parameters

                    self.StartGameThread_T = StartGameThread(steamExePath, conanParameters)
                    self.StartGameThread_T.finished.connect(lambda: self.on_count_changeStr(''))
                    self.StartGameThread_T.start()
                else:
                    self.showErrorDialog('Invalid Directories', 'It seems your steam or conanfolder is invalid (no steam.exe or conansandbox.exe found)')
                    # Steam und Conan nicht gefunden
            else:
                self.showErrorDialog('Path not found', 'Your steam or conan folder was not found')
                # Pfade exisiterien nicht
        else:
            self.showErrorDialog('Emtpy fields', 'You have not entered your steam folder or your conan folder')
            # Pfadwerte sind nicht ausgefüllt





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


class installModsThread(QThread):
    percent_signal = QtCore.pyqtSignal(int)
    string_signal = QtCore.pyqtSignal(str)
    def __init__(self):
        QThread.__init__(self)
        self.runs = True

    def __del__(self):
        self.wait()

    def stop(self):
        self.runs = False

    def run(self):
        if self.runs:
            self.string_signal.emit('Checking Collection... please wait')
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
            modCount = len(steamModlist)
            percent = 1 / modCount * 100
            for idx, mod in enumerate(steamModlist):
                modID = mod[0]
                self.percent_signal.emit((idx) * percent)
                self.string_signal.emit('Downloading / Updating Mod ' + str(idx + 1) + ' / ' + str(modCount) + ' - %p%')
                steamcmd.install_mods(gameid=440900, game_install_dir=modpath, user='anonymous', password=None, validate=True, modID=modID)
                if(idx + 1 == modCount):
                    self.string_signal.emit('All Mods downloaded' + ' - %p%')
                    self.percent_signal.emit(100)
                else:
                    pass


            modListFolder = os.path.join(gamepath, 'ConanSandbox', 'Mods')
            modListTXT = os.path.join(modListFolder, 'modlist.txt')
            modRootFolder = os.path.join(modpath, 'steamapps', 'workshop', 'content', '440900')
            if os.path.exists(modListFolder):
                if os.path.isfile(modListTXT):
                    pass
                else:
                    self.string_signal.emit('modlist.txt not found, creating it...')
                    try:
                        open(modListTXT, "w").close()
                        self.string_signal.emit('modlist.txt creation successful...')
                    except:
                        self.string_signal.emit('modlist.txt could not be created...')
            else:
                self.string_signal.emit('Modfolder and modlist.txt not found, creating it...')
                try:
                    os.mkdir(modListFolder)
                    open(modListTXT, "w").close()
                    self.string_signal.emit('Modfolder and modlist.txt creation successful...')
                except:
                    self.string_signal.emit('Modfolder and modlist.txt could not be created...')

            self.string_signal.emit('Writing Modpaths to modlist.txt...')
            try:
                os.chmod(modListTXT, stat.S_IWRITE)
                with open(modListTXT, 'w', encoding='utf8') as modListTXTIO:
                    for mod in steamModlist:
                        modItemFolder = os.path.join(modRootFolder, mod[0])
                        modFileName = os.listdir(modItemFolder)
                        modFileName = ''.join(modFileName)
                        modFullPath = os.path.join(modItemFolder, modFileName)
                        modListTXTIO.write("*{}\n".format(modFullPath))
                self.string_signal.emit('Modsetup successful...')
            except:
                self.string_signal.emit('Could not write modpaths to modlist.txt...')


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
            serverexec = subprocess.Popen(steamExePath + conanParameters, close_fds=True)


class CheckCollectionThread(QThread):

    def __init__(self):
        QThread.__init__(self)


    def __del__(self):
        self.wait()


    def run(self):
        if('http' in collection):
            collectionID = re.compile(r'(\d+)$').search(collection).group(1)
        else:
            collectionID = collection

        steamModlist = getSteamWorkshopMods.getSteamModsFromCollection(collectionID).getCollectionInfo()
        CollName = getSteamWorkshopMods.getSteamModsFromCollection(collectionID).getCollName()
        ServerAdress = getSteamWorkshopMods.getSteamModsFromCollection(collectionID).getConnectionInfo()
        if(ServerAdress):
            DirectConnect = 'Yes'
        else:
            DirectConnect = 'No'
        modName = []
        for idx, mod in enumerate(steamModlist):
            mod = str(idx + 1).zfill(2)  + ': ' + mod[1]
            modName.append(mod)
        modName = '\n'.join(modName)
        modCount = str(len(steamModlist))
        global msgMods
        msgMods = ("{} \n"
                   "\n"
                   "Modcount: {} \n"
                   "Direct Connect: {}"
                   "\n"
                   "\n"
                   "------ \n"
                   "\n"
                   "{} "
                   "\n"
                   "\n").format(CollName, modCount, DirectConnect, modName)

        msgMods = msgMods.lstrip()



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

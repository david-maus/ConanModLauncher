#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Project Cars 2 / Dedicated Server Wrapper & Weather Randomizer.

by David Maus/neslane at www.gef-gaming.de

Randomized weather slots server config for Project Cars 2 dedicated server .
Info at www.gef-gaming.de.

WARNING MESSY CODE! :)
"""
import os
import sys; sys.dont_write_bytecode = True
import glob
import subprocess


def main(osPref):

    build('main.spec',
          'ConanModLauncher',
          '../',
          'ui/main.ico',
          'ui',
          upx=0,
          console=0,
          confirm=0,
          osPref=osPref)


def build(sourceFile, programName, binDest, icon, uiPath, upx, console, confirm, osPref):
    if(osPref == 'lnx'):
        pyrcc5Path = os.path.abspath(os.path.join('home', 'david', '.local', 'bin', 'pyrcc5'))
        upxDir = '_thirdparty/upx-3.94-amd64_linux'
    else:
        pyrcc5Path = os.path.abspath(os.path.join(os.__file__, '../..', 'Scripts', 'pyrcc5.exe'))
        upxDir = '_thirdparty/upx394w'

    folderCurrent = os.path.abspath(os.path.dirname(__file__))
    resourcesSource = os.path.abspath(os.path.join(folderCurrent, uiPath))

    distPath = binDest + '/'
    workPath = './_pyinstaller'
    specPath = './'

    if(upx == 0):
        upx = ' --noupx'
    else:
        upx = ''
    if(console == 0):
        console = ' --noconsole'
    else:
        console = ' --console'
    if(confirm == 0):
        confirm = ' --noconfirm'
    else:
        confirm = ''

    for file in glob.glob(resourcesSource + "/*.qrc"):
        p = subprocess.Popen(pyrcc5Path + ' "' + file + '" -o "' + file.replace('.qrc', '.py') + '"', shell=True)
        p.wait()

    p = subprocess.Popen('pyinstaller -F --distpath ' + distPath + ' --workpath ' + workPath + ' --specpath ' + specPath + ' --name "' + programName + '" --icon "' + icon + '" --upx-dir ' + upxDir + upx + confirm + console + ' --clean ' + sourceFile, shell=True)
    p.wait()


if __name__ == "__main__":
    if sys.platform == "linux" or sys.platform == "linux2":
        osPref = "lnx"

    elif sys.platform == "win32":
        osPref = "win"
    main(osPref)

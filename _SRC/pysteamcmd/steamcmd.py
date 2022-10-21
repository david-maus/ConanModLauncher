import os
import platform
import urllib.request
import zipfile
import tarfile
import subprocess


class SteamcmdException(Exception):
    """
    Base exception for the pysteamcmd package
    """
    def __init__(self, message=None, *args, **kwargs):
        self.message = message
        super(SteamcmdException, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return repr(self.message)

    def __str__(self):
        return repr(self.message)


class Steamcmd(object):
    def __init__(self, install_path):
        """
        :param install_path: installation path for steamcmd
        """
        self.install_path = install_path
        if not os.path.isdir(self.install_path):
            raise SteamcmdException('Install path is not a directory or does not exist: '
                                      '{}'.format(self.install_path))

        self.platform = platform.system()
        if self.platform == 'Windows':
            self.steamcmd_url = 'https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip'
            self.steamcmd_zip = os.path.join(install_path, 'steamcmd.zip')
            self.steamcmd_exe = os.path.join(self.install_path, 'steamcmd.exe')

        elif self.platform == 'Linux':
            self.steamcmd_url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"
            self.steamcmd_zip = os.path.join(install_path, 'steamcmd.tar.gz')
            self.steamcmd_exe = os.path.join(self.install_path, 'steamcmd.sh')

        else:
            raise SteamcmdException('The operating system is not supported.'
                                      'Expected Linux or Windows, received: {}'.format(self.platform))

    def _download_steamcmd(self):
        try:
            return urllib.request.urlretrieve(self.steamcmd_url, self.steamcmd_zip)

        except Exception as e:
            raise SteamcmdException('An unknown exception occurred! {}'.format(e))

    def _extract_steamcmd(self):
        if self.platform == 'Windows':
            with zipfile.ZipFile(self.steamcmd_zip, 'r') as f:
                return f.extractall(self.install_path)

        elif self.platform == 'Linux':
            with tarfile.open(self.steamcmd_zip, 'r:gz') as f:
                       def is_within_directory(directory, target):
                           
                           abs_directory = os.path.abspath(directory)
                           abs_target = os.path.abspath(target)
                       
                           prefix = os.path.commonprefix([abs_directory, abs_target])
                           
                           return prefix == abs_directory
                       
                       def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                       
                           for member in tar.getmembers():
                               member_path = os.path.join(path, member.name)
                               if not is_within_directory(path, member_path):
                                   raise Exception("Attempted Path Traversal in Tar File")
                       
                           tar.extractall(path, members, numeric_owner=numeric_owner) 
                           
                       
                       safe_extract(f, self.install_path)

        else:
            # This should never happen, but let's just throw it just in case.
            raise SteamcmdException('The operating system is not supported.'
                                      'Expected Linux or Windows, received: {}'.format(self.platform))

    def install(self, force=False):
        """
        Installs steamcmd if it is not already installed to self.install_path.
        :param force: forces steamcmd install regardless of its presence
        :return:
        """
        if not os.path.isfile(self.steamcmd_exe) or force == True:
            # Steamcmd isn't installed. Go ahead and install it.
            try:
                self._download_steamcmd()
            except SteamcmdException as e:
                return e

            try:
                self._extract_steamcmd()
            except SteamcmdException as e:
                return e
        else:
            pass
        return

    def install_gamefiles(self, gameid, game_install_dir, user=None, password=None, validate=False):
        """
        Installs gamefiles for dedicated server. This can also be used to update the gameserver.
        :param gameid: steam game id for the files downloaded
        :param game_install_dir: installation directory for gameserver files
        :param user: steam username (defaults anonymous)
        :param password: steam password (defaults None)
        :param validate: should steamcmd validate the gameserver files (takes a while)
        :return: subprocess call to steamcmd
        """
        if validate:
            validate = 'validate'
        else:
            validate = None

        steamcmd_params = (
            self.steamcmd_exe,
            '+login {} {}'.format(user, password),
            '+force_install_dir "{}"'.format(game_install_dir),
            '+app_update {}'.format(gameid),
            '{}'.format(validate),
            '+quit',
        )
        try:
            return subprocess.call(steamcmd_params)
        except subprocess.CalledProcessError:
            raise SteamcmdException("Steamcmd was unable to run. Did you install your 32-bit libraries?")

    def install_mods(self, gameid, game_install_dir, user=None, password=None, validate=False, modID=None):
        if validate:
            validate = 'validate'
        else:
            validate = None

        steamcmd_params = (
            self.steamcmd_exe,
            '+login {} {}'.format(user, password),
            '+force_install_dir "{}"'.format(game_install_dir),
            '+workshop_download_item {} {}'.format(gameid, modID),
            '{}'.format(validate),
            '+quit',
        )
        VAL = subprocess.Popen(steamcmd_params, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, creationflags=0x08000000)
        VAL.wait()

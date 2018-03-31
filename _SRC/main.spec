# -*- mode: python -*-

block_cipher = None

added_files = [
         ( './ui', 'ui' ),
         ]

hidden = [

         ]

pathes = [
         ('./_pyinstaller'),
         ('./modules')
         ]

options = [ ('v', None, 'OPTION'), ('W error', None, 'OPTION') ]

a = Analysis(['./main.py'],
             pathex=pathes,
             binaries=[],
             datas=added_files,
             hiddenimports=hidden,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='ConanModLauncher',
          debug=False,
          strip=False,
          upx=False,
          runtime_tmpdir="False",
          console=False , icon='./ui/main.ico')

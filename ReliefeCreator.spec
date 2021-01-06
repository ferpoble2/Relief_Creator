# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src\\main.py'],
             pathex=['C:\\Users\\sergi\\Nextcloud\\Documents\\Universidad\\Introduccion al trabajo de titulo\\Proyecto de Memoria'],
             binaries=[('venv/Lib/site-packages/glfw/*.dll','.')],
             datas=[('src/input/test_inputs/*', 'src/input/test_inputs/'),
                    ('src/input/test_colors/*', 'src/input/test_colors/'),
                    ('src/logs/*','logs/')],
             hiddenimports=['glfw'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='main',
          debug='imports',
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ReliefeCreator')

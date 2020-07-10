# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['C:/Users/Dmytro-pc/PycharmProjects/helPES/gui.py'],
             pathex=['C:\\Users\\Dmytro-pc\\PycharmProjects\\helPES'],
             binaries=[],
             datas=[
                ('./conv', 'conv/'),
                ('./img', 'img/'),
                ('./sign', 'sign/'),
                ('./shot', 'shot/'),
                ('./azure_vm.py', '.'),
                ('./main.py', '.'),
                ('./pesmail.py', '.'),
                ('./logo.png', '.'),
                ('./template-configuration.json', '.'),
                ('./template-team.json', '.'),
                ('./settings.dat', '.')],
             hiddenimports=[],
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
          name='gui',
          debug=False,
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
               name='gui')

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['gui.py'],
             pathex=['C:\\Users\\User\\PycharmProjects\\helPES'],
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
		('./version', '.'),
		('./favicon.ico', '.'),
		('../README.md', '.'),
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
          name='helPES',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
	  version='file_version_info.txt',
	  icon='favicon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='helPES')

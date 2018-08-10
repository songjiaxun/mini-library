# -*- mode: python -*-

block_cipher = None


a = Analysis(['library_system.py'],
             pathex=['C:\\Users\\sjx19\\Desktop\\library\\mini-library\\code'],
             binaries=[ ('DLLs\\x86\\*.dll', '.') ],
             datas=[],
             hiddenimports=[],
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
          name='图书馆管理系统32位',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )

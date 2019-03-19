# -*- mode: python -*-

block_cipher = None

a = Analysis(['library_system.py'],
             pathex=[],
             binaries=[],
             datas=[('VERSION.txt', '.' ), ('图书馆信息.xlsx', '.' ), ('借阅记录.xlsx', '.' ), ('library.db', '.' )],
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
          name='图书馆管理系统',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True,
          icon='logo.ico' )
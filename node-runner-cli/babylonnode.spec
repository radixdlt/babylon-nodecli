# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['babylonnode.py'],
             pathex=['.'],
             binaries=[(".venv/lib/python3.10/site-packages/radix_engine_toolkit/x86_64-unknown-linux-gnu", ".")],
             datas=[('./templates/*.j2', 'templates'),('./testnet-genesis/*', 'testnet-genesis')],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='babylonnode',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

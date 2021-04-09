# -*- coding: UTF-8 -*-

# Python 3.8 is preferred, Win7 SP1 w/o updates requires Python 3.7,
# WinXP requires Python 2.7 + packaging >= 20.9 + pyinstaller 3.2.1

# The following WinPython distributions are known to produce stable binaries:
# https://github.com/winpython/winpython/releases/tag/4.0.20210307
#     Winpython64-3.8.8.0dot.exe
#     Winpython32-3.8.8.0dot.exe
# https://github.com/winpython/winpython/releases/tag/2.3.20200530
#     Winpython64-3.7.7.1dot.exe
# https://github.com/winpython/winpython/releases/tag/1.7.20170401
#     WinPython-32bit-2.7.13.1Zero.exe

from __future__ import print_function

import fileinput
import os
import pefile
import PyInstaller.__main__
import re
import shutil
import struct
import subprocess
import sys
import yaml

version = '1.0.3'
scriptname = 'mozjarr'

regex = re.compile('Recompressor .+?, https')
for line in fileinput.input(scriptname + '.py', inplace=True):
    print(regex.sub('Recompressor %s, https' % version, line), end='')

if sys.version_info[0] == 3:
    if struct.calcsize("P") == 8:
        scriptname += '64'
    else:
        scriptname += '32'

    if sys.version_info[1] < 8:
        scriptname += '_legacy'
else:
    scriptname += 'XP'

metadata = dict(
    Version = version,
    CompanyName = 'JustOff',
    FileDescription = 'MozJAR Recompressor',
    InternalName = 'MozJAR Recompressor',
    LegalCopyright = u'© 2021 JustOff. All rights reserved.',
    OriginalFilename = scriptname + '.exe',
    ProductName = 'MozJAR Recompressor'
)

with open('metadata.yml', 'w') as mdfile:
    yaml.dump(metadata, mdfile)

# This requires pyinstaller_versionfile >= 1.0.2
subprocess.call([
    'create-version-file', 'metadata.yml',
    '--outfile', 'versionfile.txt'
])

PyInstaller.__main__.run([
    '--clean', '--noconfirm', '--onefile', '--console',
    '--version-file', 'versionfile.txt',
    '--name', scriptname,
    'mozjarr.py'
])

exefile = os.path.join('dist', scriptname + '.exe')
pe = pefile.PE(exefile)

if not pe.verify_checksum():
    pe.OPTIONAL_HEADER.CheckSum = pe.generate_checksum()
    pe.close()
    pe.write(exefile)
    print('PE checksum has been updated')

os.remove(scriptname + '.spec')
os.remove('metadata.yml')
os.remove('versionfile.txt')
shutil.rmtree('build')
try:
    shutil.rmtree('__pycache__')
except OSError:
    pass

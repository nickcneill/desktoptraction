import sys
import os
from menu import Menu
from pathlib import Path


def main():
      pass

def install_script():
      sDir = Path(sys.executable).parent.joinpath('Scripts')
      dDir = Path('C:\\Scripts\\Desktop Traction')
      scripts = ['fileutil.py']
      data = ['icon.ico', 'script.reg', 'del.reg', 'setup.py']
      for script in scripts:
            print(Path('./', script))
            print(Path('./', dat).exists())

def install_exec():
      pass
install_script()
# main()

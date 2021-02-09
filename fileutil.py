from pathlib import Path as WindowsPath, Path
import datetime
import time
import os
import pickle
from menu import Menu
import winreg
import argparse
import tkinter
from tkinter.simpledialog import askstring
from tkinter.messagebox import askyesno
import sys
import subprocess


def main():
    global interactive
    tkinter.Tk().withdraw()
    # Parse commandline arguments prior to menu entrypoint
    if len(sys.argv) > 1:
        interactive = False
        arge = lambda e: f'Argument invalid: {e}\nUse no arguments to run interactive mode'
        parser = argparse.ArgumentParser(description="File and Folder Utility for Windows", prog='File App v 1.0f')
        parser.add_argument('target', metavar='t', type=str, help='Target file/folder', default='./')
        parser.add_argument('-d', '--date', help='Prepends date to selected target', action='store_true')
        parser.add_argument('-w', '--word', help='Prepend text to selected target',action='store_true')
        parser.add_argument('-b', '--both', help='Prepend text and date to selected target', action='store_true')
        parser.add_argument('-e', '--eMod', help='Export Modified Date data for folders and sub-folders. Inc. Files etc.', action='store_true')
        parser.add_argument('-i', '--iMod', help='Import Modified Date data for folders and sub-folders.\nInc. Files etc.', action='store_true')
        # parser.add_argument('-r', '--install_registry', help='Installs registry keys for context menu add-in')
        parsedArgs = vars(parser.parse_args())
        functions = {
            "date"  : prepend_date,
            "word"  : prepend_text,
            "both"  : prepend_both,
            "eMod": export_mdate,
            "iMod": import_mdate
        }
        for arg in parsedArgs:
            if parsedArgs[arg] and arg in [f for f in functions.keys()][0:3]:
                functions[arg](target_dir=parsedArgs['target'])
            elif parsedArgs[arg] and arg in [f for f in functions.keys()][3:5]:
                functions[arg]()
            else:
                arge(f'{arge} not recognized please check arguments.')
        # non dict argument handler
        # if parsedArgs.date:
        #     functions[parsedArgs.date](target_dir=parsedArgs.target)
        # if parsedArgs.word:
        #     functions[parsedArgs.word](target_dir=parsedArgs.target)
        # if parsedArgs.both:
        #     functions[parsedArgs.both](target_dir=parsedArgs.target)
        # if parsedArgs.iMod:
        #     functions[parsedArgs.iMod](target_dir=parsedArgs.target)
        # if parsedArgs.eMod:
        #     functions[parsedArgs.eMod](target_dir=parsedArgs.target)
    else:
        # menu entry point
        interactive = True
        menu = Menu(title="Modified Date Utility for Windows(for Matthew) v 0.1")
        prependmenu = Menu(title='Prepends all files in directory and subdirectory with the following:')
        menu.set_options(options=[
            ("Import Modified Dates", set_mdate),
            ("Export Modified Dates", export_mdate),
            ("Prepend Tools", prependmenu.open),
            ("Install Registry Keys", install_registry),
            ("Exit", menu.close)
        ])
        prependmenu.set_options(options=[
            ("Prepend Date", prepend_date),
            ("Prepend Word", prepend_text),
            ("Prepend Both", prepend_both),
            ("Main Menu", prependmenu.close)
        ])
        menu.open()

def get_mdate(curdir='.'):
    return [[i, datetime.datetime.fromtimestamp(i.stat().st_mtime)] for i in Path(curdir).glob("**/*")]

def export_mdate():
    if interactive:
        os.system('cls')
        print("Leave blank for default File: (./mDateExport.mdate) and  Directory")
        export_dir=Path(input('Export File-Location: ') or './')
        filename=input('Export Filename: ') or 'mDateExport.mdate'
        selected_directory=input('Export Directory') or './'
        with open(f'{export_dir}/{filename}', 'wb') as outfile:
            pickle.dump(get_mdate(Path(selected_directory)), outfile)
    else:
        try:
            with open(f'./mDateExport.mdate', 'wb') as outfile:
                pickle.dump(get_mdate(Path('./')), outfile)
        except FileNotFoundError:
            print(f'Please check that ./mDateExport.mdate  exists and is in the current directory.')

def import_mdate():
    if interactive:
        if input('Override default export file? (y/n)') == 'y':
            input_dir = Path(input('Path to .mdate file: '))
        else:
            input_dir = "./mDateExport.mdate"
        with open(f"{input_dir}", "rb") as infile: 
            return pickle.load(infile)
    else:
        input_dir = "./mDateExport.mdate"
        try:
            with open(f"{input_dir}", "rb") as infile: 
                return pickle.load(infile)
        except FileNotFoundError:
            print(f'Please check that {input_dir} exists and is in the current directory.')

def set_mdate():
    mDateExport = import_mdate()
    for i in mDateExport:
        mDate = time.mktime(i[1].timetuple()) 
        try:
            os.utime(i[0], (mDate, mDate))
        except:
            print('an error has occurred')

def prepend_date(useModDate=False, inc_dir=False, strf="%d%m%y", target_dir='.'):
    if interactive:
        # useModeDate = askyesno(title='Prepend Date', message='Use modified date?')
        if input('Use Modified Date').lower() == 'y':
            useModDate = True
        if input('Include Folders?').lower() == 'y':
            inc_dir = True
        if input('change date/time format?'.lower()) == 'y':
            strf = input('Enter date time format (https://strftime.org/): ')
        target_dir = input('Target directory (Leave blank for current): ')
    if Path(target_dir).is_file():
        now = datetime.datetime.now().strftime(strf)
        return Path(target_dir).rename(f'{Path(target_dir).parent}/{now}-{Path(target_dir).name}')
    if useModDate:
        for item, date in get_mdate(target_dir):
            if inc_dir:
                item.rename(f'{item.parent}/{date.strftime(strf)}-{item.name}')
            else:
                if item.is_file():
                    item.rename(f'{item.parent}/{date.strftime(strf)}-{item.name}')
    else:
        appDate = datetime.datetime.now().strftime(strf)
        for item in Path(target_dir).glob("**/*.*"):
            if inc_dir:
                item.rename(f"{item.parent}/{appDate}-{item.name}")
            else:
                if item.is_file():
                    item.rename(f"{item.parent}/{appDate}-{item.name}")

def prepend_text(text=None, inc_dir=False, target_dir='.'):
    if interactive:
        text = input('Text to prepend: ')
        target_dir = input('Target directory (Leave blank for current): ')
        if input('Include Folders?').lower() == 'y':
            inc_dir = True
    if not text:
        tkinter.Tk().withdraw()
        text = askstring('Append Text', 'Enter text to prepend to file:')
    if Path(target_dir).is_file():
        return Path(target_dir).rename(f'{Path(target_dir).parent}/{text}-{Path(target_dir).name}')
    for item in Path(target_dir).glob("**/*.*"):
        if inc_dir:
            item.rename(f"{item.parent}/{text}-{item.name}")
        else:
            if item.is_file():
                item.rename(f"{item.parent}/{text}-{item.name}")

def prepend_both(text=None, inc_dir=False, target_dir='.', useModDate=False, strf="%d%m%y", date_first=False):
    # 'text' parameter maybe unneeded.
    if interactive:
        if input('Prepend Date first? ie. 010180-YOURTEXT? ').lower() == 'y':
            date_first = True
    if Path(target_dir).is_file():        
        if date_first:
            prepend_date(useModDate, inc_dir, strf, target_dir=prepend_text(text, inc_dir, target_dir))
        else:
            prepend_text(text, inc_dir, target_dir=prepend_date(useModDate, inc_dir, strf, target_dir))
    else:
        if date_first:
            prepend_text(text, inc_dir, target_dir)
            prepend_date(useModDate, inc_dir, strf, target_dir)
        else:
            prepend_date(useModDate, inc_dir, strf, target_dir)
            prepend_text(text, inc_dir, target_dir)
        

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return Path(base_path, relative_path)

def install_registry():
    if input("To install in script mode enter 'y' for executable enter 'n'") == y:
        reg = resource_path('./script/.reg')
        subprocess.Popen(f'regedit.exe -s {reg}')
        print('Keys installed ensure python and python/scripts are in PATH')
    else:
        reg = resource_path('./exec/.reg')
        subprocess.Popen(f'regedit.exe -s {reg}')
        print("Keys installed ensure fileutil is located in C:\\Program Files\\Desktop Traction\\")


main()
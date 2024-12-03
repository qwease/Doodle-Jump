# -*- coding: utf-8 -*-

try:
    import PyInstaller.__main__
    import pygame
    import glob
    import fnmatch
    import sys
    import os
    import shutil
    import operator
except ImportError as message:
    raise SystemExit("Unable to load module. %s" % message)

class BuildExe:
    def __init__(self):
        #Name of starting .py
        self.script = "main.py"

        #Name of program
        self.project_name = "Pencil"

        #Version of program
        self.project_version = "0.0"

        #Icon file (None will use pygame default icon)
        self.icon_file = None

        #Extra files/dirs copied to game
        self.extra_datas = []

        #Extra/excludes python modules
        self.extra_modules = []
        self.exclude_modules = []
        
        #DLL Excludes
        self.exclude_dll = ['']

        #Extra scripts
        self.extra_scripts = []

        #Dist directory
        self.dist_dir = 'dist'

    def opj(self, *args):
        path = os.path.join(*args)
        return os.path.normpath(path)

    def find_data_files(self, srcdir, *wildcards, **kw):
        def walk_helper(arg, dirname, files):
            if '.svn' in dirname:
                return
            names = []
            lst, wildcards = arg
            for wc in wildcards:
                wc_name = self.opj(dirname, wc)
                for f in files:
                    filename = self.opj(dirname, f)

                    if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                        names.append(filename)
            if names:
                lst.append((dirname, names))

        file_list = []
        recursive = kw.get('recursive', True)
        if recursive:
            os.path.walk(srcdir, walk_helper, (file_list, wildcards))
        else:
            walk_helper((file_list, wildcards),
                       srcdir,
                       [os.path.basename(f) for f in glob.glob(self.opj(srcdir, '*'))])
        return file_list

    def run(self):
        if os.path.isdir(self.dist_dir):  # Erase previous destination dir
            shutil.rmtree(self.dist_dir)
        
        # Use the default pygame icon, if none given
        if self.icon_file == None:
            path = os.path.split(pygame.__file__)[0]
            self.icon_file = os.path.join(path, 'pygame.ico')

        # List all data files to add
        extra_datas = []
        for data in self.extra_datas:
            if os.path.isdir(data):
                extra_datas.extend(self.find_data_files(data, '*'))
            else:
                extra_datas.append(data)

        # Create the PyInstaller command arguments
        args = [
            self.script,
            '--name=' + self.project_name,
            '--onefile',
            '--windowed',
            '--icon=' + self.icon_file,
            '--distpath=' + self.dist_dir,
            '--workpath=build',
            '--clean',
        ]

        # Add data files
        for data in extra_datas:
            args.append('--add-data=' + data + os.pathsep + '.')

        # Add extra modules
        for module in self.extra_modules:
            args.append('--hidden-import=' + module)

        # Add excluded modules
        for module in self.exclude_modules:
            args.append('--exclude-module=' + module)

        # Run PyInstaller
        PyInstaller.__main__.run(args)
        
        # Copy img directory to dist directory
        img_src = 'img'
        if os.path.exists(img_src):
            img_dst = os.path.join(self.dist_dir, 'img')
            if os.path.exists(img_dst):
                shutil.rmtree(img_dst)
            shutil.copytree(img_src, img_dst)
            print(f"Copied {img_src} directory to {img_dst}")

        if os.path.isdir('build'):  # Clean up build dir
            shutil.rmtree('build')

if __name__ == '__main__':
    BuildExe().run()  # Run generation
    input("Press any key to continue")  # Pause to let user see that things ends
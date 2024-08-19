#!/usr/bin/env python

import flickrapi
import os
import math
import argparse

api_key="3e7dd44924b55357971d63965c3b4f86"
from SECRETS import api_secret

flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
flickr.authenticate_via_browser(perms='write')

lastline=False
numfiles=0

# calculate an MD5 hash for a file:
# hashlib.md5(open('./IMAGES/11/11/DSCF3801.JPG', 'rb').read()).hexdigest()

def lines_that_start_with(string, fp):
    return [line for line in fp if line.startswith(string)]

def callback(p):
    """
    This callback is for generating the progress bar on the command line
    """
    global lastline

    progress = p['progress']
    name = p['name']
    n = p['n']
    numfiles = p['numfiles']

    total = 100
    percent = 100 * (progress / float(total))
    bar = '#' * int(percent) + '-' * int(100 - percent)
    count=f"{n}/{numfiles}"
    if (math.ceil(percent) == 100) and lastline==False:
        print(f"\r{count} : {name} |{bar}| {math.ceil(percent)}%\n", end="\r")
    elif lastline==False:
        print(f"\r{count} : {name} |{bar}| {math.ceil(percent)}%", end="\r")

    if math.ceil(percent) == 100:
        lastline=True
	
def list_images(path):
    """
    Function that receives as a parameter a directory path
    :return list_: File List and Its Absolute Paths
    """

    files = []

    # r = root, d = directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))

    lst = [file for file in files]
    return lst

class FileWithCallback(object):
    def __init__(self, filename, callback):
        self.file = open(filename, 'rb')
        self.callback = callback
        self.len = os.path.getsize(filename)
        self.fileno = self.file.fileno
        self.tell = self.file.tell
        self.p = {}

    def read(self, size):
        global numfiles
        global n
        if self.callback:
            self.p['progress'] = self.tell() * 100.0 / self.len
            self.p['name'] = filename
            self.p['numfiles'] = numfiles
            self.p['n'] = n
            self.callback(self.p)

        return self.file.read(size)

class list_action(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        return super().__init__(option_strings, dest, nargs=0, default=argparse.SUPPRESS, **kwargs)
    
    def __call__(self, parser, namespace, values, option_string, **kwargs):
        photosets = flickr.photosets.getList()['photosets']
        for photoset in reversed(photosets['photoset']):
            print(f"{photoset['id']:20} : {photoset['title']['_content']}")
        exit(0)

        parser.exit()

if __name__ == '__main__':

    home_directory = os.path.expanduser('~')
    configbase=home_directory+"/.config/syncr"
    configfile=configbase+"/syncedfiles"
    try:
        os.mkdir(configbase)
    except:
        pass

    parser = argparse.ArgumentParser(
        prog='syncr',
        description='Upload images to Flickr',
        epilog='')

    parser.add_argument("folder", help="upload this folder of images (incl. all subfolders)")
    parser.add_argument('-l', '--list', action=list_action, help='list existing albums and exit')
    parser.add_argument('-n', '--album', help='add images to a new album called ALBUM')
    parser.add_argument('-d', '--usedirname', action="store_true", help='use the folder name as the album name (creates a new album)')
    parser.add_argument('-e', '--existingalbum', help='upload to existing album (specify album/photoset ID)')
    parser.add_argument('-p', '--privacy', help='set image privacy to PRIVACY. Default is public', default="private")
    parser.add_argument('--dryrun', action="store_true", default=False, help='Dry run - don\'t make any changes on Flickr')

    args = parser.parse_args()

    if args.privacy=="public":
        is_public=True
    else:
        is_public=False
        
    imagelist = list_images(args.folder)
    numfiles=len(imagelist)
    photoids=[]

    if not args.dryrun:
        # upload the images
        n = 1
        for image in imagelist:
            filename = image
            found = False

            # if the absolute filename exists in the history, don't re-upload
            with open(configfile, 'r') as fp:
                for line in lines_that_start_with(os.path.abspath(filename), fp):
                    found=True

            if not found:

                fileobj = FileWithCallback(filename, callback)
                rsp = flickr.upload(filename, fileobj, is_public=is_public, format='etree')

                with open(configfile, 'a') as f:
                    f.writelines(os.path.abspath(filename)+'\n')

                for c in rsp:
                    photoid = rsp[0].text
                    photoids.append(photoid)
                lastline=False
            else:
                print(f"Skipping {filename}, already in history ({configfile})")

            n += 1

        # create album, if requested, and add all images
        albumid=None
        if args.album or args.usedirname:
        
			# use specified album name
            if args.album:
                albumname = args.album
			# ...or use the directory name as album name
            if args.usedirname:
                albumname = args.folder

            # create the album
            rsp = flickr.photosets.create(title=albumname, primary_photo_id=photoids[0])
            albumid = rsp['photoset']['id']

        if args.existingalbum:
            albumid = args.existingalbum            

        # add uploaded images to this album
        if albumid:
            for photoid in photoids[1:]:
                flickr.photosets.addPhoto(photoset_id=albumid, photo_id=photoid)


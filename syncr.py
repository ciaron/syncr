#!/usr/bin/env python

import flickrapi
import os
import math
import argparse
from PIL import Image
import urllib.request

api_key="3e7dd44924b55357971d63965c3b4f86"
from SECRETS import api_secret

flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
flickr.authenticate_via_browser(perms='write')

lastline=False
numfiles=0

# warn about uploads bigger than this threshold
threshold=200 #MB

def lines_that_start_with(string, fp):
    return [line for line in fp if line.startswith(string)]

# list_action is used in argparse so that --list doesn't require positional arg "folder"
class list_action(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        return super().__init__(option_strings, dest, nargs=0, default=argparse.SUPPRESS, **kwargs)
    
    def __call__(self, parser, namespace, values, option_string, **kwargs):
        photosets = flickr.photosets.getList()['photosets']
        for photoset in reversed(photosets['photoset']):
            print(f"{photoset['id']:20} : {photoset['title']['_content']}")
        exit(0)

        parser.exit()

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

def url_is_alive(url):
    """
    Checks that a given URL is reachable.
    :param url: A URL
    :rtype: bool
    """
    request = urllib.request.Request(url)
    request.get_method = lambda: 'HEAD'

    try:
        urllib.request.urlopen(request)
        return True
    except urllib.request.HTTPError:
        return False

def is_image(filename):
    try:
        im=Image.open(filename)
        im.verify()
        im.close()
        return True
    except:
        return False

def list_images(path):
    """
    Function that receives as a parameter a directory path
    :return list_: File List and Its Absolute Paths
    """

    files = []

    # r = root, d = directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if is_image(os.path.join(r,file)):
                files.append(os.path.join(r, file))

    lst = [file for file in files]
    return lst

def get_upload_size(imagelist):
    upload_size=0
    for f in imagelist:
        upload_size += os.path.getsize(f)
    return upload_size

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
    parser.add_argument('-n', '--albumname', help='add images to a new album called ALBUMNAME')
    parser.add_argument('-d', '--usedirname', action="store_true", help='use the folder name as the album name (creates a new album)')
    parser.add_argument('-e', '--existingalbum', help='upload to existing album (specify album/photoset ID)')
    #parser.add_argument('-p', '--privacy', help='set image privacy to PRIVACY. Default is private', default="private")
    parser.add_argument('-p', '--privacy', help='set image privacy on upload. Default is private', choices=['public', 'private'], default='private')
    parser.add_argument('-y', help='don\'t prompt, assume affirmative', action="store_true")
    parser.add_argument('--download', dest='albumid', help='Download all images (original size) from ALBUMID to FOLDER')
    parser.add_argument('--dryrun', action="store_true", default=False, help='Dry run - don\'t make any changes on Flickr')

    args = parser.parse_args()

    if args.privacy=="public":
        is_public=True
    else:
        is_public=False
        
    imagelist = list_images(args.folder)
    numfiles=len(imagelist)
    photoids=[]

    # CONFIRM UPLOAD SIZE
    upload_size = get_upload_size(imagelist)/1024/1024

    if (not args.y) and upload_size > threshold:
        answer = input(f"upload size will be {upload_size:.2f} MB in {len(imagelist)} files. Do you want to continue? [y/n] ")
        if not answer or answer[0].lower() != 'y':
            print('Exiting')
            exit(1)

    # if there's no history file, make an empty one
    if not os.path.isfile(configfile):
        open(configfile, 'a').close()

    # DOWNLOADING
    if args.albumid:
        # get list of photos in album
        ps = flickr.photosets.getPhotos(photoset_id=args.albumid, extras="url_l,url_o")
        num_to_download = len(ps['photoset']['photo'])
        n = 1
        if not os.path.isdir(args.folder):
            os.makedirs(args.folder, exist_ok=True)
        for photo in ps['photoset']['photo']:
            print(f"downloading {n} of {num_to_download}")
            if url_is_alive(photo['url_o']):
                urllib.request.urlretrieve(photo['url_o'], os.path.join(args.folder, os.path.basename(photo['url_o'])))
                n += 1
            else:
                print(f"{photo['url_o']} not found, skipping")

        print(f"finished downloading, exiting")
        exit(0)

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

        if args.albumname or args.usedirname:
        
			# use specified album name
            if args.albumname:
                albumname = args.albumname
			# ...or use the directory name as album name
            if args.usedirname:
                albumname = args.folder

            # create the album
            if len(photoids) > 0:
                rsp = flickr.photosets.create(title=albumname, primary_photo_id=photoids[0])
                albumid = rsp['photoset']['id']

        if args.existingalbum:
            albumid = args.existingalbum            

        # add uploaded images to an album, if this is specified
        if albumid:
            for photoid in photoids[1:]:
                flickr.photosets.addPhoto(photoset_id=albumid, photo_id=photoid)


#!/usr/bin/env python

import flickrapi
import os
import math
import argparse

api_key="3e7dd44924b55357971d63965c3b4f86"
from SECRETS import api_secret

flickr = flickrapi.FlickrAPI(api_key, api_secret)
flickr.authenticate_via_browser(perms='write')

lastline=False

def callback(p):
    """
    This callback is for generating the progress bar on the command line
    """
    global lastline

    progress = p['progress']
    name = p['name']

    total = 100
    percent = 100 * (progress / float(total))
    bar = '#' * int(percent) + '-' * int(100 - percent)
    #print(f"\r|{bar}| {percent:.2f}%", end="\r")

    if (math.ceil(percent) == 100) and lastline==False:
        print(f"\r{name} |{bar}| {math.ceil(percent)}%\n", end="\r")
    elif lastline==False:
        print(f"\r{name} |{bar}| {math.ceil(percent)}%", end="\r")

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
        # the following attributes and methods are required
        self.len = os.path.getsize(filename)
        self.fileno = self.file.fileno
        self.tell = self.file.tell
        self.p = {}

    def read(self, size):
        if self.callback:
            #self.callback(self.tell() * 100.0 / self.len)
            self.p['progress'] = self.tell() * 100.0 / self.len
            self.p['name'] = filename
            self.callback(self.p)

        return self.file.read(size)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='syncr',
        description='Upload images to Flickr',
        epilog='')

    #group = parser.add_mutually_exclusive_group()
    parser.add_argument("folder", help="upload this folder of images (incl. all subfolders)")
    parser.add_argument('-l', '--list', action="store_true", help='list existing albums and exit')
    parser.add_argument('-n', '--album', help='add images to a new album called ALBUM')
    parser.add_argument('-d', '--usedirname', action="store_true", help='use the folder name as the album name (creates a new album)')
    parser.add_argument('-e', '--existingalbum', help='upload to existing album (specify album/photoset ID)')
    parser.add_argument('-p', '--privacy', help='set image privacy to PRIVACY. Default is public', default="private")

    args = parser.parse_args()

    if args.list:
        photosets = flickr.photosets.getList()[0]
        for photoset in reversed(photosets):
            print(f"{photoset.attrib['id']:20} : {photoset[0].text}")
        exit(0)

    if args.privacy=="public":
        is_public=True
    else:
        is_public=False
        
    imagelist = list_images(args.folder)
    #imagelist = list_images('./IMAGES/11/11')
    #print(imagelist)
    #print(args)

    # no callback for progress bar:
    #rsp = flickr.upload(filename, title="A TEST")

    # Upload all images in folder
    dryrun = False
    photoids=[]

    if not dryrun:
        # upload the images
        for image in imagelist:
            filename = image
            fileobj = FileWithCallback(filename, callback)
            rsp = flickr.upload(filename, fileobj, is_public=is_public)
            #rsp = flickr.upload(filename, fileobj, title="untitled", is_public=is_public)
            for c in rsp:
                photoid = rsp[0].text
                photoids.append(photoid)
                #print(photoid)
                #print(c.tag, c.attrib)
            lastline=False

        # create album, if requested, and add all images
        albumid=None
        if args.album or args.usedirname:
        
            #print(args.album)
            if args.album:
                albumname = args.album
            if args.usedirname:
                albumname = args.folder

            # create the album
            rsp = flickr.photosets.create(title=albumname, primary_photo_id=photoids[0])
            albumid = rsp[0].attrib['id']
            #print(f"album id is {albumid}")

        if args.existingalbum:
            albumid = args.existingalbum            

            # add uploaded images to this album
        if albumid:
            for photoid in photoids[1:]:
                flickr.photosets.addPhoto(photoset_id=albumid, photo_id=photoid)


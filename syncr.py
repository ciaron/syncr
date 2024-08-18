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

#def callback(progress):
def callback(p):
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

    parser.add_argument("folder", help="upload this folder of images (incl. all subfolders)")
    parser.add_argument('--album', help='add images to a new album called ALBUM')
    parser.add_argument('-d', '--usedirname', action="store_true", help='use the directory name as the album name (new album)')
    parser.add_argument('--privacy', help='set image privacy to PRIVACY. Default is public')

    args = parser.parse_args()

    if args.album:
        print(args.album)
        # create the album
        rsp = flickr.photosets.create(title=args.album, primary_photo_id="53919645835")
        # print the new photoset/album ID:
        albumid = rsp[0].attrib['id']
        print(f"album id is {albumid}")

    imagelist = list_images('./IMAGES/11/11')
    print(imagelist)

    ## upload a test image
    #filename = "./IMAGES/09/DSCF3769.JPG"
    #fileobj = FileWithCallback(filename, callback)
    #rsp = flickr.upload(filename, fileobj, title="untitled")
    #lastline=False

    #filename = "./IMAGES/10/DSCF3800.JPG"
    #fileobj = FileWithCallback(filename, callback)
    #rsp = flickr.upload(filename, fileobj, title="untitled")
    #lastline=False
    
    # no callback for progress bar:
    #rsp = flickr.upload(filename, title="A TEST")

    # Upload all images in folder
    for image in imagelist:
        filename = image
        fileobj = FileWithCallback(filename, callback)
        rsp = flickr.upload(filename, fileobj, title="untitled")
        for c in rsp:
            print(c.tag, c.attrib)
            photoid = rsp[0].text
            print(photoid)
        lastline=False

import flickrapi
import os

api_key="3e7dd44924b55357971d63965c3b4f86"
from SECRETS import api_secret

flickr = flickrapi.FlickrAPI(api_key, api_secret)
flickr.authenticate_via_browser(perms='write')

filename = "./IMAGES/09/DSCF3769.JPG"

def callback(progress):
    print(progress)

class FileWithCallback(object):
    def __init__(self, filename, callback):
        self.file = open(filename, 'rb')
        self.callback = callback
        # the following attributes and methods are required
        self.len = os.path.getsize(filename)
        self.fileno = self.file.fileno
        self.tell = self.file.tell

    def read(self, size):
        if self.callback:
            self.callback(self.tell() * 100 // self.len)
        return self.file.read(size)

fileobj = FileWithCallback(filename, callback)
rsp = flickr.upload(filename, fileobj, title="A TEST")


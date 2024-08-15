import flickrapi
import os

api_key="3e7dd44924b55357971d63965c3b4f86"
from SECRETS import api_secret

flickr = flickrapi.FlickrAPI(api_key, api_secret)
flickr.authenticate_via_browser(perms='write')

def callback(progress):
    total = 100
    percent = int(100 * (progress / float(total)))
    bar = '#' * percent + '-' * (100 - percent)
    #print(progress) # only reaches 99
    #print(percent, progress)
    print(f"\r|{bar}| {percent:.2f}%", end="\r")

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

    def read(self, size):
        if self.callback:
            self.callback(self.tell() * 100 // self.len)
        return self.file.read(size)

if __name__ == '__main__':

    imagelist = list_images('./IMAGES')
    print(imagelist)

    # upload a test image
    filename = "./IMAGES/09/DSCF3769.JPG"
    fileobj = FileWithCallback(filename, callback)
    rsp = flickr.upload(filename, fileobj, title="A TEST")


# syncr

## create a Python env

`python3 -m venv envs/flickr`

`pip install flickrapi`

`source env/flickr/bin/activate`

## Features

[] rate-limiting

[] warning when number of images in upload exceeds a threshold

[] exclude files which are not images (i.e. only JPG, PNG, GIF)

[] default uploads are `private`, can set to `public` and/or `friends/family`

[] optionally, upload to an album

    [] new album
    
    [] existing


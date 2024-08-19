# syncr

## Getting started

### create a Python env

```shell
python3 -m venv envs/flickr
pip install flickrapi
source env/flickr/bin/activate
```
### Usage
```
syncr --folder=<folder, relative or absolute> --rate=<images per minute> --quiet --nowarn --album="My New Album" | --use-directory-name | --select-album
```
## Features

- [ ] progress bar, squelch with `--quiet`
- [ ] rate-limiting `--rate`
- [ ] don't repeat uploads, or `--replace` or `--allow-duplicate-uploads`
- [ ] warning when number of images (or total upload size in MB) of upload exceeds a threshold `--nowarn` to disable
- [ ] exclude files which are not images (i.e. only JPG, PNG, GIF)
- [x] default uploads are `private`, can set to `public` and/or `friends/family` : `--privacy=public|friends|private`
- [x] upload to existing album (list albums with `-l`)
- [x] upload to new album `--album=`, or `--use-directory-name|-d`

## Future plans
- [ ] 2-way sync (Flickr photoset <-> folder on disk)
- [ ] set title and description from EXIF (disable with `--no-exif-title`, `--no-exif-desc`)
- [ ] local web app
- [ ] GUI application (Electron? React?)
- [ ] resize before upload (max dimensions)

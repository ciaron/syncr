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
usage: syncr [-h] [-l] [-n ALBUMNAME] [-d] [-e EXISTINGALBUM] [-p PRIVACY] [--download ALBUMID] [--dryrun] folder

Upload images to Flickr

positional arguments:
  folder                upload this folder of images (incl. all subfolders)

options:
  -h, --help            show this help message and exit
  -l, --list            list existing albums and exit
  -n ALBUMNAME, --albumname ALBUMNAME
                        add images to a new album called ALBUMNAME
  -d, --usedirname      use the folder name as the album name (creates a new album)
  -e EXISTINGALBUM, --existingalbum EXISTINGALBUM
                        upload to existing album (specify album/photoset ID)
  -p PRIVACY, --privacy PRIVACY
                        set image privacy to PRIVACY. Default is private
  --download ALBUMID    Download all images (original size) from ALBUMID to FOLDER
  --dryrun              Dry run - don't make any changes on Flickr

```
## Features

- [x] progress bar
- [ ] rate-limiting `--rate` (there are no limits for Flickr Pro members)
- [x] don't repeat uploads. absolute paths for uploads are stored and compared
- [ ] warning when number of images (or total upload size in MB) of upload exceeds a threshold `--nowarn` to disable
- [x] exclude files which are not images (i.e. only JPG, PNG, GIF)
- [x] default uploads are `private`, can set to `--privacy=public`
- [x] upload to existing album (list albums with `-l`)
- [x] upload to new album `--album=`, or `--use-directory-name|-d`
- [x] download an album from Flickr to a local directory (`--download ALBUMID LOCAL_FOLDER`)

## Future plans
- [ ] 2-way sync (Flickr photoset <-> folder on disk)
  - [x] 1-way sync works already: 1) `syncr --existingalbum <ID> FOLDERNAME`; then 2) add files to FOLDERNAME then run 1) again
- [ ] set title and description from EXIF (disable with `--no-exif-title`, `--no-exif-desc`)
- [ ] local web app
- [ ] GUI application (Electron? React?)
- [ ] set `is_friend`, `is_family` as well as `is_public`.

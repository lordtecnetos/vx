# vx (*video extraction*)

**vx** is a command line tool that extracts specific parts from multiple [Matroska](https://www.matroska.org/) files. 

The `mkvextract` and `mkvmerge` commands from [MKVToolNix](https://mkvtoolnix.download/) are used to perform the
task.

### Requirements

* [Python](https://www.python.org/) programming language (*version 3.4 or newer*)
* [MKVToolNix](https://mkvtoolnix.download/) tools (*version 9.2 or newer*)

### Install

TODO

### Usage

After installed, type `vx` or `vx -h` or `vx --help` to see the options and commands.

Basic usage: `vx [-h] {tracks,attachments} ...`

**vx** only supports two extraction modes offered by `mkvextract` command, [see](https://mkvtoolnix.download/doc/mkvextract.html) your docs:

* #### Tracks extraction mode
  
  `vx tracks [-h] [--dir [directory]] [--type {subtitles}] video [video ...]`
  
  * `video [video ...]` (*required*) - video or videos to extraction
  
  * `--dir [directory]` (*optional*) - directory that will contain the extracted items (*default: `--type` value, if `[directory]` is empty*)
  
  * `--type {subtitles}` (*optional*) - type of track to extraction (*default: `subtitles`*). There are others types of tracks, how `audio` and `video`, but, in this version, only `subtitles` type is supported ;)
  
  * `-h` or `--help` (*optional*) - show the help message
 
  ##### Examples:
  ```
  # minimum command, extracts all subtitles from one video to current directory with name of video file
  $ vx tracks video.mkv

  # extracts all subtitles from video1 and video2 to current directory
  $ vx tracks video1.mkv video2.mkv 

  # extracts all subtitles from the files with 'mkv' extension in current directory to subtitles directory
  $ vx tracks *.mkv --dir 

  # extracts all subtitles from video to ~/Downloads directory
  $ vx tracks video.mkv --dir ~/Downloads
  ```

* #### Attachments extraction mode

  `vx attachments [-h] [--dir [directory]] video [video ...]`

  * `video [video ...]` (*required*) - video or videos to extraction
  
  * `--dir [directory]` (*optional*) - directory that will contain the extracted items (*default: `attachments`, if `[directory]` is empty*)
  
  * `-h` or `--help` (*optional*) - show the help message
  
  ##### Examples:
  ```
  # This mode extracts all attachments inside a new directory with name of each video file

  # minimum command, extracts all attachments from one video
  $ vx attachments video.mkv

  # extracts all attachments from video1 and video2
  $ vx attachments video1.mkv video2.mkv 

  # extracts all attachments from the files with 'mkv' extension in current directory to attachments directory
  $ vx attachments *.mkv --dir 

  # extracts all attachments from video to ~/Downloads directory
  $ vx attachments video.mkv --dir ~/Downloads
  ```

### Author and Contact

Alessandro Beleboni Belini (lordtecnetos@gmail.com)


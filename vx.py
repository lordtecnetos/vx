#!/usr/bin/python3

import os
import re
import sys
import json
import argparse
import subprocess

from enum import Enum, unique
from distutils.version import LooseVersion

MKV_EXTRACT = 'mkvextract'
MKV_MERGE = 'mkvmerge'

__prog__ = 'vx'


@unique
class FileType(Enum):
    S_KATE = ('S_KATE', 'ogg')
    S_VOBSUB = ('S_VOBSUB', 'sub')
    S_TEXT_ASS = ('S_TEXT/ASS', 'ass')
    S_TEXT_SSA = ('S_TEXT/SSA', 'ass')
    S_TEXT_USF = ('S_TEXT/USF', 'usf')
    S_HDMV_PGS = ('S_HDMV/PGS', 'sup')
    S_TEXT_UTF8 = ('S_TEXT/UTF8', 'srt')

    def __init__(self, codec_id, extension):
        self.codec_id = codec_id
        self.extension = extension

    @classmethod
    def get(cls, codec_id):
        for member in cls.__members__.values():
            if member.codec_id == codec_id:
                return member

        raise VxException("unsupported 'codec_id' : {!r}".format(codec_id))


class ExtractionMode(object):

    def __init__(self, identification_json, type_='', basedir=''):
        self.__sourcefilename, self.__identification_json = None, None
        self.sourcefilename = identification_json.get('file_name')
        self.identification_json = identification_json
        self.basedir = basedir
        self.type = type_

    @property
    def identification_json(self):
        return self.__identification_json

    @identification_json.setter
    def identification_json(self, identification_json):
        if not identification_json.get('container').get('recognized'):
            raise VxException('unsupported file')

        self.__identification_json = identification_json

    @property
    def sourcefilename(self):  # video.mkv
        return self.__sourcefilename

    @sourcefilename.setter
    def sourcefilename(self, filename):
        self.__sourcefilename = os.path.basename(filename)

    @property
    def sourcename(self):  # video
        return os.path.splitext(self.sourcefilename)[0]

    @property
    def basedir_sourcename(self):  # basedir/video
        return os.path.join(self.basedir, self.sourcename)

    def spec(self, id_, path):
        return '{}:{}'.format(id_, path)

    def specs(self):
        pass


class Tracks(ExtractionMode):

    """ Tracks extraction mode """

    __mode__ = 'tracks'

    def __init__(self, identification_json, type_='subtitles', basedir=''):
        super(Tracks, self).__init__(identification_json, type_, basedir)

    def specs(self):
        tracks, subtitles = self.identification_json.get(self.__mode__), []
        subs = [track for track in tracks if track.get('type') == self.type]
        basedir = self.basedir_sourcename

        for sub in subs:
            ftype = FileType.get(sub.get('properties').get('codec_id'))
            extraname = '_' + str(sub.get('id')) if len(subs) > 1 else ''
            path = '{}{}.{.extension}'.format(basedir, extraname, ftype)
            subtitles.append(self.spec(sub.get('id'), path))

        return subtitles


class Attachments(ExtractionMode):

    """ Attachments extraction mode """

    __mode__ = 'attachments'

    def __init__(self, identification_json, basedir=''):
        super(Attachments, self).__init__(identification_json, basedir=basedir)

    def specs(self):
        basedir, attachments = self.basedir_sourcename, []
        for attachment in self.identification_json.get(self.__mode__):
            path = os.path.join(basedir, attachment.get('file_name'))
            attachments.append(self.spec(attachment.get('id'), path))

        return attachments


class VxException(Exception):

    def __init__(self, message):
        self.message = message

    def print_message(self):
        print(str(self))

    def __str__(self):
        return self.message


class tools(object):

    MIN_VERSION = 'v9.2.0'

    def check(self, tool):
        try:
            v = subprocess.check_output([tool, '-V'], universal_newlines=True)
            if not self.is_version_allowed(v):
                msg = '{!r} must have the version {} or newer'
                raise VxException(msg.format(tool, self.MIN_VERSION))
        except FileNotFoundError:
            raise VxException('{0!r} not found.\nInstall {0!r} in {1} '
                              'version or newer'.format(tool, self.MIN_VERSION))

    def is_version_allowed(self, version):
        search = re.search(r'v[\d.]+', version)
        version_searched = LooseVersion(search and search.group() or ' ')
        return version_searched >= LooseVersion(self.MIN_VERSION)

    @classmethod
    def verify(cls, *tools_to_check):
        tools = cls()

        def wrap(function):
            def inner(*args, **kwargs):
                for tool in tools_to_check:
                    tools.check(tool)
                return function(*args, **kwargs)
            return inner
        return wrap


@tools.verify(MKV_MERGE)
def get_extraction_specs(mode, video, **kwargs):
    commands = [MKV_MERGE, '-i', '-F', 'json', video]
    data = subprocess.check_output(commands, universal_newlines=True)

    extraction_specs = mode(json.loads(data), **kwargs).specs()

    if not extraction_specs:
        raise VxException('No {.__mode__}'.format(mode))

    return extraction_specs


@tools.verify(MKV_EXTRACT, MKV_MERGE)
def extract(namespace):
    kwargs = namespace.vars(exclude=('mode', 'videos'))

    for index, video in enumerate(namespace.videos, 1):
        try:
            print('Processing: {!r}'.format(os.path.basename(video)))
            extraction_specs = get_extraction_specs(namespace.mode, video,
                                                    **kwargs)
            commands = [MKV_EXTRACT, namespace.mode.__mode__, video]
            commands.extend(extraction_specs)
            subprocess.call(commands)
        except VxException as e:
            e.print_message()

        if index != len(namespace.videos):
            print()


class ArgsBuilder(object):

    def __init__(self):
        self.parser = argparse.ArgumentParser(description="This program "
                                              "extracts specific parts from multiple Matroska file. "
                                              "The {!r} and {!r} commands from 'MKVToolNix' are used "
                                              "to perform the task".format(
                                                  MKV_EXTRACT, MKV_MERGE),
                                              prog=__prog__)

        self.subparsers = self.parser.add_subparsers(help='extraction modes')

        tracks_parser = self.add_parser_extraction_mode(Tracks, 't')

        self.add_argument_basedir(tracks_parser, "default: '--type' value",
                                  action=DefaultDirectoryAction)

        tracks_parser.add_argument('--type', dest='type_', default='subtitles',
                                   help="type of track to extraction "
                                   "(default: '%(default)s')",
                                   choices=['subtitles'])

        attachments_parser = self.add_parser_extraction_mode(Attachments, 'a')

        self.add_argument_basedir(attachments_parser, "default: 'attachments'",
                                  const='attachments')

    def add_parser_extraction_mode(self, mode, alias):
        help_message = 'extract {.__mode__} from Matroska files'.format(mode)
        parser = self.subparsers.add_parser(mode.__mode__, help=help_message,
                                            description=mode.__doc__,
                                            aliases=[alias])
        self.add_argument_videos(parser)
        parser.set_defaults(mode=mode)
        return parser

    def add_argument_videos(self, parser):
        parser.add_argument('videos', type=FileTypeArgument('r'), nargs='+',
                            help='video or videos to extraction',
                            metavar='video')

    def add_argument_basedir(self, parser, default_help_desc, **kwargs):
        parser.add_argument('--dir', help='directory that will contain the '
                            'extracted items ({} if [%(metavar)s] '
                            'is empty)'.format(default_help_desc),
                            dest='basedir', default='', nargs='?',
                            metavar='directory', **kwargs)

    def parse_args(self):
        instance = Namespace()
        self.parser.parse_args(namespace=instance)
        return instance


class Namespace(argparse.Namespace):

    def vars(self, exclude=None):
        vars_ = vars(self)

        if exclude is None:
            return vars_.copy()

        return {k: v for k, v in vars_.items() if k not in exclude}


class DefaultDirectoryAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values or namespace.type_)


class FileTypeArgument(argparse.FileType):

    def __call__(self, string):
        with super(FileTypeArgument, self).__call__(string) as f:
            return f.name


def main():
    try:
        builder = ArgsBuilder()

        if len(sys.argv) > 1:
            extract(builder.parse_args())
        else:
            builder.parser.print_help()
    except KeyboardInterrupt:
        print('\nAbort')
    except VxException as e:
        e.print_message()


if __name__ == '__main__':
    main()

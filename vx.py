#!/usr/bin/python3

import argparse

from extractor import extract_subtitles
from model import VxException

parser = argparse.ArgumentParser(prog='vx')
parser.add_argument('videos', metavar='video', nargs='+', type=argparse.FileType('r'), help='video or videos to extract subtitles')
parser.add_argument('--dir', dest='in_dir', metavar='dirname', default='', nargs='?', const='Subtitles',
					help="""directory where subtitles are extracted. If the command is entered but not informed any value to it,
						will create a default directory 'Subtitles'""")

if __name__ == '__main__':
	args = parser.parse_args()

	try:
		for v in args.videos:
			with v as video:
				extract_subtitles(video.name, args.in_dir)
	except KeyboardInterrupt:
		print('\nAbort')
	except VxException as error:
		parser.print_usage()
		print('vx: error: ' + error.value)


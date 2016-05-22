#!/usr/bin/python3

import os
import argparse

from extractor import extract


parser = argparse.ArgumentParser(prog='vx')
parser.add_argument('videos', metavar='video', nargs='+', type=argparse.FileType('r'), help='video or videos to extract subtitles')
parser.add_argument('--dir', dest='in_dir', metavar='dirname', default='', nargs='?', const='Subtitles', 
	help='directory where subtitles are extracted. If the command is entered but not informed any value to it, will create a default directory \'Subtitles\'')


if __name__ == '__main__':
	args = parser.parse_args()
	
	try:	
		extract(args.videos, args.in_dir)
	except KeyboardInterrupt:
		print('\nAbort')
	except Exception as error:
		parser.print_usage()
		# TODO personalizar os possíveis erros
		print('vx: error: ' + error.args[0])


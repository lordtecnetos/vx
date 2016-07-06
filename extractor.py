import re
import os
import json
import subprocess
from distutils.version import LooseVersion

from model import Subtitle, VxException

tools = ('mkvmerge', 'mkvextract')


def check_tool(tool):
	try:
		search = re.search(r'v[\d.]+', subprocess.check_output([tool, '-V'], universal_newlines=True))
		version = search and search.group()
		if version and LooseVersion(version) < LooseVersion('v9.2.0'):
			raise VxException('{!r} must have the version v9.2.0 or newer.'.format(tool))
	except FileNotFoundError:
		raise VxException('{0!r} Not found. Please install {0!r} in v9.2.0 version or newer.'.format(tool))


def verify_tools(function):
	def inner(*args, **kwargs):
		for tool in tools:
			check_tool(tool)

		return function(*args, **kwargs)

	return inner


@verify_tools
def find_in(video, model):
	info = json.loads(subprocess.check_output([tools[0], '-i', '-F', 'json', video], universal_newlines=True))

	if not info.get('container').get('recognized'):
		raise VxException('{!r} unsupported file'.format(video))

	return [model(track, video) for track in info.get('tracks') if track.get('type') == model.__type__]


@verify_tools
def extract_subtitles(video, extrapath=''):
	subtitles = find_in(video, Subtitle)

	for sub in subtitles:
		sub.concat_track_id = len(subtitles) > 1
		out_filename = os.path.join(extrapath, sub.filename)
		subprocess.call([tools[1], 'tracks', video, '{}:{}'.format(sub.track_id, out_filename)])

	if not subtitles:
		print('{!r} does not have tracks with subtitles'.format(video))

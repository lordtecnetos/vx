import os
import json
import subprocess

from model import Subtitle, VxException
from validation import verify_tools


@verify_tools
def find_in(video, model):
	info = json.loads(subprocess.check_output(['mkvmerge', '-i', '-F', 'json', video], universal_newlines=True))

	if not info.get('container').get('recognized'):
		raise VxException('{!r} unsupported file'.format(video))

	return [model(track, video) for track in info.get('tracks') if track.get('type') == model.__type__]


@verify_tools
def extract_subtitles(video, extrapath=''):
	subtitles = find_in(video, Subtitle)
	for sub in subtitles:
		sub.concat_track_id = len(subtitles) > 1
		out_filename = os.path.join(extrapath, sub.filename)
		subprocess.call(['mkvextract', 'tracks', video, '{}:{}'.format(sub.track_id, out_filename)])
		break
	else:
		print('{!r} does not have tracks with subtitles'.format(video))

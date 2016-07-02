import os
import json
import subprocess

from model import Subtitle, VxException
from validation import verify

@verify
def find_in(video, model):
	info = json.loads(subprocess.check_output(['mkvmerge', '-i', '-F', 'json', video], universal_newlines=True))

	if not info.get('container').get('recognized'):
		raise VxException('Unsupported file')

	return [model(track, video) for track in info.get('tracks') if track.get('type') == model.__type__]


@verify
def extract_subtitles(video, extrapath=''):
	subtitles = find_in(video, Subtitle)

	for sub in subtitles:
		sub.concat_track_id = len(subtitles) > 1
		out_filename = os.path.join(extrapath, sub.filename)
		subprocess.call(['mkvextract', 'tracks', video, '{0}:{1}'.format(sub.track_id, out_filename)])

	return subtitles


def extract(videos, extrapath=''):
	for video in videos:
		with video as v:
			if not extract_subtitles(v.name, extrapath):
				print('{!r} does not have tracks with subtitles'.format(v.name))

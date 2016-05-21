import os
import sys
import json
import subprocess

from model import Subtitle


def get_subtitles(video, extrapath):
	result = json.loads(subprocess.check_output(['mkvmerge', '-i', '-F', 'json', video], universal_newlines=True))

	if not result.get('container').get('recognized'):
		raise Exception('Unsupported file')
	
	subs = [Subtitle(track, video, extrapath) for track in result.get('tracks') if track.get('type') == 'subtitles']

	for sub in subs:
		sub.concat_track_id = len(subs) > 1
		subprocess.call(['mkvextract', 'tracks', sub.video, str(sub)])
	
	return bool(subs)
	

def extract(videos, extrapath):
	for video in videos:
		with video as v:
			if not get_subtitles(v.name, extrapath):
				print('{!r} does not have tracks with subtitles'.format(v.name))


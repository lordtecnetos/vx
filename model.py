import os

from enum import Enum, unique


@unique
class SubtitleFileType(Enum):
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
		for name, member in cls.__members__.items():
			if member.codec_id == codec_id:
				return member
		
		raise VxException("The 'vx' not support the 'codec_id' : {!r}".format(codec_id))
	

class Subtitle(object):
	
	__type__ = 'subtitles'
	
	def __init__(self, track, video):
		self.video = video
		self.concat_track_id = False
		self.track_id = track.get('id')
		self.filetype = SubtitleFileType.get(track.get('properties').get('codec_id'))
	
	@property
	def filename(self):
		basename, extension = os.path.splitext(os.path.basename(self.video))
		track_id = '{}__'.format(self.track_id) if self.concat_track_id else ''
		return '{track_id}{0}.{type}'.format(basename, type=self.filetype.extension, track_id=track_id)


class VxException(Exception):
	
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)


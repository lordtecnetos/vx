import re
import subprocess
from distutils.version import LooseVersion

from model import VxException

tools = ('mkvmergej', 'mkvextract')


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

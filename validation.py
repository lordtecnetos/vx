import re
import subprocess
from distutils.version import LooseVersion

from model import VxException

tools = ('mkvmerge', 'mkvextract')


def check_tool(tool):
	try:
		version = subprocess.check_output([tool, '-V'], universal_newlines=True)
		match = re.search(r'v[\d.]+', version).group()
		if match and LooseVersion(match) < LooseVersion('v9.2.0'):
			raise VxException('{!r} possui versão menor que v9.2.0'.format(tool))
	except FileNotFoundError as e:
		raise VxException(e.args[1])


def verify_tools(function):
	def inner(*args, **kwargs):
		for tool in tools:
			check_tool(tool)

		return function(*args, **kwargs)

	return inner

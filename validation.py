import re
import subprocess
from distutils.version import LooseVersion

from model import VxException

tools = ('mkvmerge', 'mkvextract')


def check_version(version):
	match = re.search(r'v[\d.]+', version).group()
	if match and LooseVersion(match) < LooseVersion('v9.2.0'):
		raise VxException('Versao menor que v9.2.0')


def verify_tools(function):
	def inner(*args, **kwargs):
		try:
			for tool in tools:
				check_version(subprocess.check_output([tool, '-V'], universal_newlines=True))

			return function(*args, **kwargs)
		except FileNotFoundError as e:
			raise VxException(e.args[1])

	return inner

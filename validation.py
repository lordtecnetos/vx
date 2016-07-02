import re
import subprocess

from model import VxException
from distutils.version import LooseVersion

tools = ('mkvmerge', 'mkvextract')


def check_version(version):
	match = re.search(r'v[\d.]+', version).group()
	if match and LooseVersion(match) < LooseVersion('v9.2.0'):
		raise VxException('Versao menor que v9.2.0')


def verify(function):
	def inner(*args, **kwargs):
		try:
			for tool in tools:
				check_version(subprocess.check_output([tool, '-V'], universal_newlines=True))
			function(*args, **kwargs)
		except FileNotFoundError as e:
			raise VxException(e.args[1])

	return inner

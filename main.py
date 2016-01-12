#!/usr/bin/env python3
import getopt
import sys 
import os.path
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import platform
import tempfile
import ctypes

""""""""""""""""""""
" Global variables "
""""""""""""""""""""
DEBUG = False
OS_PACK = {
	'Darwin_64bit': r'/(Unity-)[\d\w.]+\.pkg',
	'Windows_64bit': r'/(UnitySetup64-)[\d\w.]+\.exe',
	'Windows_32bit': r'/(UnitySetup32-)[\d\w.]+\.exe',
}


def error(msg):
	print("[ERROR] {0}".format(msg), file=sys.stderr)


def debug(msg):
	if DEBUG:
		print("[DEBUG] {0}".format(msg), file=sys.stderr)


def install_from_uri(uri, system, tmp_dir):
	file_name = os.path.join(tmp_dir, os.path.basename(uri))
	try:
		download_file(uri, file_name)
	except Exception as e:
		error("Cannot download file from url: " + uri)
		return False
	new_dir = os.path.basename(uri)[:os.path.basename(uri).rfind(".")]
	if system in ("Darwin_64bit"):
		#ex_code = os.system("mv {0} /tmp/1.exe".format(file_name))
		ex_code = os.system("installer -package {0} -target /".format(file_name))
		if ex_code != 0:
			error("Can't install " + file_name)
			return False
		else:
			if os.path.isdir("/Applications/Unity"):
				if os.path.isdir("Applications/{0}'".format(new_dir)):
					os.system("unlink /Applications/{0}".format(new_dir))
				os.rename("/Applications/Unity", "/Applications/{0}".format(new_dir))
				debug("Folder renamed to 'Applications/{0}'".format(new_dir))
	elif system in ("Windows_64bit", "Windows_32bit"):
		#error("Currently not supported")
		debug("installing from " + file_name + " to " + new_dir)
		try: 
			debug("{0} /S /D='C:\Program files\{1}'".format(file_name, new_dir))
			ex_code = os.system("{0} /S /D='C:\Program files\{1}'".format(file_name, new_dir))
			#check ex_code in Windows
			if ex_code != 0:
				error("Can't install " + file_name)
				return False
		except Exception as e:
			error("Cannot install {0} from {1}".format(file_name, new_dir))
			return False
	return True


def download_file(uri, file_name):
	debug("Downloading '{0}' into {1}".format(uri, file_name))
	r = requests.get(uri, stream=True)
	with open (file_name, "wb") as fd:
		for chunk in r.iter_content(100):
			fd.write(chunk)
	debug("File {0} sussefully downloaded!".format(file_name))


def file_processing(file, system, tmp_dir):
	to_download = list()
	with open (file, "r") as f:
		for url in f:
			url = url.rstrip('\r\n')
			if not url:
				continue
			if not re.match('^https?://', url):
				error("Invalid link: '{0}'".format(url))
				continue
			html = None
			try:
				html = get_url_content(url)
			except Exception as e:
				error("Can't get content for {0}. Reason {1}.".format(url, e))
				continue
			#do some stuff and get all links
			links_list = list()
			soup = BeautifulSoup(html, "html.parser")
			for link in soup.find_all("a"):
				link = urljoin(url, link.get("href"))
				debug("Link found: {0}".format(link))
				links_list.append(link)
			regex = OS_PACK[system]
			to_install = [i for i in links_list if re.search(regex, i)]
			debug("Files to download and istall " + " ".join(to_install))
			for uri in to_install:
				install_from_uri(uri, system, tmp_dir)


def get_url_content(url, repeat=3):
	counter = 0
	debug("Processing url: {0}".format(url))
	r = requests.get(url)
	while (r.status_code != requests.codes.ok and counter < repeat):
		r = requests.get(url)
		counter += 1
		debug(
			"Repeat request: " + url + " at step " +
			counter + " with reason " + r.status_code
		)
		#if (r.status_code != requests.codes.ok):
	r.raise_for_status()
	return r.text



def usage():
	print("Usage: {0} --file=~./data.txt".format(sys.argv[0]))


def main():
	try:
		is_admin = os.geteuid() == 0
	except AttributeError:
		is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

	if not is_admin:
		error("Need to have a superpower!")
		sys.exit(1)

	system = platform.system() + '_' + platform.architecture()[0]

	if not system in OS_PACK.keys():
		error("Platform {0} is not in the list '{1}'".format(system,
			"', ' ".join(OS_PACK.keys())))
		sys.exit(2)

	try:
		opts, args = getopt.getopt(
			sys.argv[1:], "hf:d", ["help", "file=", "debug"]
		)
	except getopt.GetoptError as err:
		error(err)
		usage()
		sys.exit(3)

	file = None
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit(0)
		elif o in ("-d", "--debug"):
			global DEBUG
			DEBUG = True
		elif o in ("-f", "--file"):		
			if a and os.path.isfile(a) and os.access(a, os.R_OK):
				file = a
			else:
				error(
					"Error: -f|--file reqires path to readable file. ", 
					file=sys.stderr
				)
				usage()
				sys.exit(4)

	#Chech for path, if is not given - use default path
	if not file:
		dirname = os.path.abspath(os.path.dirname(sys.argv[0]))
		file = os.path.join(dirname, 'data.txt')
		if not (os.path.isfile(file) and os.access(file, os.R_OK)):
			usage()
			sys.exit(5)
		debug("Using default file path: " + file)

	with tempfile.TemporaryDirectory() as tmp_dir:
		file_processing(file, system, tmp_dir)


if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass
	except Exception as e:
		error("Unexpected error: " + e)
		sys.exit(6)

#!/usr/bin/env python3
import getopt
import sys 
import os.path
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

""""""""""""""""""""
" Global variables "
""""""""""""""""""""
verbose = False


def error(msg):
	print("[ERROR] {0}".format(msg), file=sys.stderr)


def debug(msg):
	if verbose:
		print("[DEBUG] {0}".format(msg), file=sys.stderr)


def file_processing(file):
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
		opts, args = getopt.getopt(
			sys.argv[1:], "hf:v", ["help", "file=", "verbose"]
			)
	except getopt.GetoptError as err:
		print(err)
		usage()
		sys.exit(1)
	file = None
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit(0)
		elif o in ("-v", "--verbose"):
			global verbose
			verbose = True
		elif o in ("-f", "--file"):		
			if a and os.path.isfile(a) and os.access(a, os.R_OK):
				file = a
			else:
				print(
					"Error: -f|--file reqires path to readable file. ", 
					file=sys.stderr
				)
				usage()
				sys.exit(2)

	if not file:
		dirname = os.path.abspath(os.path.dirname(sys.argv[0]))
		file = os.path.join(dirname, 'data.txt')
		if not (os.path.isfile(file) and os.access(file, os.R_OK)):
			usage()
			sys.exit(3)
	file_processing(file)


if __name__ == "__main__":
    main()


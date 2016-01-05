#!/usr/bin/env python3
import getopt
import sys 
import os.path


def file_processing(file):
	with open (file, "r") as f:
		for line in f:
			print(line, end='\n')


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
	verbose = False
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit(0)
		elif o in ("-v", "--verbose"):
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
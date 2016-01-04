#!/usr/bin/env python3
import random 

def start_game(min_num, max_num, try_to, random_num):
	print("Passed args: %s %s %s %s" % (min_num, max_num, try_to, random_num))

min_num = 0
max_num = 100
try_to = 3 
random_num = random.randrange(min_num, max_num)

print("Try to guess the number I think about. It's from {0} to {1}".format(min_num, max_num))
print("You have {0} tries".format(try_to))

text = input("Enter the number: ")
print(text)

start_game(min_num, max_num, try_to, random_num)

with open ("main.py", "r") as file:
	for line in file:
		print(line, end='')

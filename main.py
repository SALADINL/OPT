#!/usr/bin/env python3

import argparse
import os
import sys

parser = argparse.ArgumentParser(description='This program provide tools to crypt and uncrypt message from files.',
                                 epilog='Enjoy the program!')

group = parser.add_mutually_exclusive_group()
group.add_argument("-g", "--generate", help="enable generate mode (default)", action="store_true")
group.add_argument("-s", "--send", help="enable send mode", action="store_true")
group.add_argument("-r", "--receive", help="enable receive mode", action="store_true")

parser.add_argument("directory", help="directory is needed", type=str)

opts, rem_args = parser.parse_known_args()

if opts.send:
    group_two = parser.add_mutually_exclusive_group()
    group_two.add_argument("-f", "--filename", help="message to be inserted from the file", action="store", type=str)
    group_two.add_argument("-t", "--text", help="message to be inserted from the the command line", action="store",
                           type=str)

if opts.receive:
    parser.add_argument("filename", help="message to be inserted from the file", type=str)

args = parser.parse_args()


def main():
    pass


if __name__ == '__main__':
    main()

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


def get_interfaces_names():
    """
    :return: list of network interface name
    """
    return os.listdir('/sys/class/net/')


def check_network(ifname):
    """
    Function check if an interfaces is UP

    :param ifname: name of the interface
    :return: True if the interfaces is UP
    """

    file = os.open("/sys/class/net/" + ifname + "/operstate", os.O_RDONLY)
    output = os.read(file, 50)
    return True if "up" in str(output) else False


def generate(path):
    """
    Void function which call all the needed function to generate repository and pads
    :param path: Location and name of the repository you want to create
    :return: void
    """

    try:
        os.mkdir(path)
        print(path, " created with success.")
    except FileExistsError:
        print(path, " already exist.")
    new_path = path + '/' + add_dir(path)
    generate_files(new_path)


def add_dir(path):
    """
    :param path: location where create new dir
    :return: name of the create repository
    """
    if nb_directory(path) >= 10000:
        print("Number directory is exceeded")
        sys.exit(1)
    name_dir = str(nb_directory(path)).zfill(4)
    try:
        os.mkdir(path + '/' + name_dir)
    except FileExistsError:
        print(path, " already exist.")

    return name_dir


def nb_directory(path):
    """
    :return: the number of dir in this location
    """
    return len(os.listdir(path))


def generate_files(path):
    """
    This functions will create three types of pad a hundred time
    :param path: location where you want to create pads
    :return: void
    """
    extension = ['p', 's', 'c']
    with open("/dev/random", "rb") as rand:
        for i in range(0, 100):
            for e in extension:
                name_file = str(i) + e
                file = open(path + '/' + name_file.zfill(3), "wb")
                if e == 'c':
                    bytes_dev = rand.read(2000)
                else:
                    bytes_dev = rand.read(48)
                file.write(bytes_dev)
                file.close()
    rand.close()


def main():
    for ele in get_interfaces_names():
        if check_network(ele):
            print("Network detected")
            sys.exit(1)

    dir = args.directory

    if args.send:
        pass
    elif args.receive:
        pass
    else:
        generate(dir)


if __name__ == '__main__':
    main()

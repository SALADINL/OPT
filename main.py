#!/usr/bin/env python3

import argparse
import glob
import os
import sys
import subprocess

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


def read_txt(filename):
    """
    This function read a txt file and store it in a string.

    :param filename: Path of the txt file.
    :return: Return a string within the message
    """

    response = ""
    file = open(filename, 'r')
    response = file.read()
    file.close()

    return response


def check_message(message):
    """
    Check the message don't exceed 2000 char
    """
    return False if len(message) > 20000 else True


def shred_file(path, num_pad):
    """
    Shred the pad used to encrypt

    :param path: location of the pad
    :param num_pad: number of the pad
    :return: void
    """
    subprocess.run(['shred', '-u', path + '/' + num_pad])


def encrypt(message, path):
    """
    This function will call all function need to encrypt message

    :param message: string contains message
    :param path: location of pads needed
    :return: void
    """
    if path[len(path) - 1] == '/':
        path = path[:len(path) - 1]

    if glob.glob(path + '/*c') is None:
        print("Can't find file XXc")
        sys.exit(1)

    f_pad = sorted(glob.glob(path + '/*c'))[0]
    num_pad = f_pad[len(f_pad) - 3:len(f_pad) - 1]
    filename = create_transmission(path, num_pad)

    f_out = open(filename, 'wb')

    f_pref = open(path + '/' + num_pad + 'p', 'rb')
    pref = f_pref.read()
    f_pref.close()

    file = open(f_pad, "rb")
    buffer = file.read()
    int_array = str2int(message)
    res = []
    idx = 0
    for b in buffer:
        if len(int_array) == idx:
            pass
            # res.append((int(b) - ord(' ')) % 255)
        else:
            v = (int(b) - int_array[idx]) % 255
            res.append(v)
            idx += 1

    f_suff = open(path + '/' + num_pad + 's', 'rb')
    suff = f_suff.read()
    f_suff.close()

    res = pref + bytes(res) + suff
    f_out.write(res)
    f_out.close()
    shred_file(path, num_pad + 'c')


def create_transmission(path, num_pad):
    """
    Create a new file with the filename contains location and num pad

    :param path: location of pads
    :param num_pad: number of the pad used
    :return: name of the new file
    """
    path = path.replace('/', "-") + '-' + num_pad + 't'
    open(path, "w+")

    return path


def str2int(message):
    """
    Convert string to an array list of ascii in integer

    :param message: (str) A string which contains the message
    :return: Returns array list of ascii in integer
    """

    int_array = []

    for ele in message:
        int_array.append(ord(ele))

    return int_array


def decrypt(path, filename):
    """
    This function will call all function needed to decrypt a message

    :param path: location of pads
    :param filename: location of transmission file
    :return: void
    """
    filename_output = filename[:len(filename)] + 'm'
    if path[len(path) - 1] == '/':
        path = path[:len(path) - 1]

    f_input = open(filename, 'rb')
    buffer = f_input.read()
    f_input.close()

    pref = buffer[:48]
    content = buffer[48:-48]

    num_pad = scanner(path, pref)
    f_key = open(path + '/' + num_pad + 'c', 'rb')
    keys = f_key.read()
    f_key.close()

    res = []
    for i in range(len(content)):
        v = (int(keys[i]) - int(content[i])) % 255
        res.append(int(v))

    f_out = open(filename_output, "w")
    f_out.write(int2str(res))
    f_out.close()

    shred_file(path, filename)
    shred_file(path, num_pad + 'p')


def scanner(path, pref):
    """
    This function will test every pref-pad to find the correct key

    :param path: location of pads
    :param pref: list of filename
    :return: number of the pad which contain right key
    """
    f_list = glob.glob(path + '/*p')
    num_pad = ""

    for f_name in f_list:
        f = open(f_name, 'rb')
        tmp = f.read()
        if pref == tmp:
            num_pad = f_name[len(f_name) - 3:len(f_name) - 1]

        f.close()
    return num_pad


def int2str(bin_array):
    """
    Convert an array list of ascii in binary to  string

    :param bin_array: (str) An array list of ascii in binary
    :return: Returns string which contains the message
    """

    message = ""

    for ele in bin_array:
        message += chr(ele)

    return message


def main():
    for ele in get_interfaces_names():
        if check_network(ele):
            print("Network detected")
            sys.exit(1)

    dir = args.directory

    if args.send or args.receive:
        if not os.path.exists(dir):
            print('Repository does not exist !')
            sys.exit(1)

    if args.send:
        if args.filename:
            if not os.path.exists(args.filename):
                print('Input file does not exist')
                sys.exit(1)
            message = read_txt(args.filename)
        elif args.text:
            message = args.text
        else:
            message = input("Enter your message : ")

        if not check_message(message):
            print('Too long message !')
            sys.exit(1)

        encrypt(message, dir)
    elif args.receive:
        if not os.path.exists(args.filename):
            print('Input file does not exist')
            sys.exit(1)

        decrypt(dir, args.filename)
    else:
        generate(dir)


if __name__ == '__main__':
    main()

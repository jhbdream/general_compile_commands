#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
#
# usage:
#

"""A tool for generating compile_commands.json ."""

import argparse
import json
import logging
import os
import glob
import re
import subprocess
import sys

_DEFAULT_OUTPUT = 'compile_commands.json'

# 搜索 c 文件
# ignore 可以忽略包含字符串的文件
def get_c_source_files(ignore=""):
    cwd = os.getcwd()
    files = []

    print("current work directory: " + cwd)
    print("find c files...")

    for f in glob.glob(cwd + "/**/*.c", recursive = True):
        if ignore == '' or ignore not in f:
            files.append(f)

    return files

# 搜索包含 .h 的目录
def get_include_file_path(ignore=""):
    cwd = os.getcwd()
    path = []

    print("current work directory: " + cwd)
    print("find headers path...")

    for f in glob.glob(cwd + "/**/*.h", recursive = True):
        if ignore == '' or ignore not in f:
            dir = os.path.dirname(f)
            if dir not in path:
                path.append(dir)

    return path

def gen_cflags(include="", defines="", extra=""):
    cflags = []

    cflags.append("-std=gnu11")

    for path in include:
        cflags.append("-I" + path)

    for d in defines:
        cflags.append("-D" + d)

    return cflags

def gen_compile_command(filename, toolchain="gcc", cflags=[]):
    command = []
    # gcc -Iinclude -DKERNEL -O0 -c -o file.o file.c

    command.append(toolchain)

    if type(cflags) == str:
        cflags = [cflags]

    command.extend(cflags)

    command.append("-c")
    command.append("-o")

    obj_file = os.path.splitext(filename)[0]+'.o'
    command.append(obj_file)

    command.append(filename)

    return command
    

def main():
    output = _DEFAULT_OUTPUT

    root_dir = os.getcwd()
    toolchain = "gcc"

    compile_commands = []

    soruce_files = []
    include_dirs = []
    defines = []
    cflags = []

    soruce_files = get_c_source_files()
    include_dirs = get_include_file_path()
    cflags = gen_cflags(include = include_dirs, defines = defines, extra = "")
       
    for file in soruce_files:
        directory = root_dir
        file = file
        command = " ".join(gen_compile_command(file, cflags = cflags))

        entry = {
            'directory': directory,
            'file': file,
            'command': command,
        }

        compile_commands.append(entry)

    with open(output, 'wt') as f:
        json.dump(compile_commands, f, indent=4, sort_keys=False)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0
#
#
# usage:
#

"""A tool for generating general compile_commands.json ."""

import argparse
import json
import logging
import os
import re
import subprocess
import sys

_DEFAULT_OUTPUT = 'compile_commands.json'

def parse_arguments():
    """Sets up and parses command-line arguments.

    Returns:
        directory: The work directory where the objects were built.
        output: Where to write the compile-commands JSON file.
        paths: The list of files/directories to handle to find .cmd files.
    """
    usage = 'Creates a compile_commands.json database from kernel .cmd files'
    parser = argparse.ArgumentParser(description=usage)

    directory_help = ('specify the output directory used for the kernel build '
                      '(defaults to the working directory)')
    parser.add_argument('-d', '--directory', type=str, default='.',
                     help=directory_help)

    output_help = ('path to the output command database (defaults to ' +
                   _DEFAULT_OUTPUT + ')')
    parser.add_argument('-o', '--output', type=str, default=_DEFAULT_OUTPUT,
                        help=output_help)

    args = parser.parse_args()
    return (os.path.abspath(args.directory),
            args.output)

def process_line(root_directory, command_prefix, file_path):
    """Extracts information from a .cmd line and creates an entry from it.

    Args:
        root_directory: The directory that was searched for .cmd files. Usually
            used directly in the "directory" entry in compile_commands.json.
        command_prefix: The extracted command line, up to the last element.
        file_path: The .c file from the end of the extracted command.
            Usually relative to root_directory, but sometimes absolute.

    Returns:
        An entry to append to compile_commands.

    Raises:
        ValueError: Could not find the extracted file based on file_path and
            root_directory or file_directory.
    """
# The .cmd files are intended to be included directly by Make, so they
    # escape the pound sign '#', either as '\#' or '$(pound)' (depending on the
    # kernel version). The compile_commands.json file is not interepreted
    # by Make, so this code replaces the escaped version with '#'.
    prefix = command_prefix.replace('\#', '#').replace('$(pound)', '#')

    # Use os.path.abspath() to normalize the path resolving '.' and '..' .
    abs_path = os.path.abspath(os.path.join(root_directory, file_path))
    if not os.path.exists(abs_path):
        raise ValueError('File %s not found' % abs_path)
    return {
        'directory': root_directory,
        'file': abs_path,
        'command': prefix + file_path,
    }

def main():
    directory, output = parse_arguments()
    _LINE_PATTERN = r"'(?:[^']|'{2})+'"
    line_matcher = re.compile(_LINE_PATTERN)

    _FILE_NAME_PATTERN = r"'([^']+\.c)'"
    file_name_matcher = re.compile(_FILE_NAME_PATTERN)

    compile_commands = []

    cmdfile = "build.log"
    with open(cmdfile, 'rt') as f:
        for line in f:
            cmd = line_matcher.findall(line)
            file = file_name_matcher.findall(line)

            cmd = " ".join(cmd)
            file = " ".join(file)

            if "gcc" not in cmd:
                continue

            if not file or not cmd:
                continue

            entry = {
                'directory': directory,
                'file': file,
                'command': cmd,
            }

            compile_commands.append(entry)

    with open(output, 'wt') as f:
        json.dump(compile_commands, f, indent=2, sort_keys=True)

if __name__ == '__main__':
    main()

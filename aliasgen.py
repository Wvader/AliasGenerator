import argparse
import os
import pathlib
import random
from os import walk

TEXT_EDITOR = "less"
MEDIA_EDITOR = "open"

parser = argparse.ArgumentParser(
    prog='aliasgen.py',
    description='Generate path and file aliases recursively from a specific path'
)

parser.add_argument('--path', help='Path to target', type=pathlib.Path, required=True)
parser.add_argument('--destination', help='Generate file with aliases', type=pathlib.Path)
parser.add_argument('--console', help='Print aliases statements to the console', action="store_true")
parser.add_argument('--levels', help='Levels to walk', type=int, required=False)
parser.add_argument('--text-editor', help='Set text editor', type=int, required=False)
parser.add_argument('--media-editor', help='Set media editor', type=int, required=False)

commandArgs = parser.parse_args()

unix_path = str(commandArgs.path)
levels = commandArgs.levels

PATH_SEPARATOR = commandArgs.path.anchor

dataFiles = []
alias_bash_statements = []

inital_path_sep_count = unix_path.count(PATH_SEPARATOR)


def random_str(length=8):
    consonants = "bcdfghjklmnpqrstvwxyz"
    vowels = "aeiou"
    return "".join(random.choice((consonants, vowels)[i % 2]) for i in range(length))


def write_aliases_file(path, lines, path_sep):
    if is_file(path):
        write_lines_to_file(path, lines)
    else:
        path = str(path) + path_sep + random_str() + '.aliases'
        write_lines_to_file(path, lines)
    print('File written in: ' + path)


def write_lines_to_file(path, lines):
    with open(path, "a") as f:
        f.writelines(lines)


def is_file(path):
    os.path.isfile(path)  # Does bob.txt exist?  Is it a file, or a directory?


def is_dir(path):
    os.path.isdir(path)


for (dirpath, dirnames, filenames) in walk(unix_path):
    dataFile = {"dirpath": dirpath, "dirnames": dirnames, "filenames": filenames}
    dataFiles.append(dataFile)


def get_upper_path():
    split_path = unix_path.split(PATH_SEPARATOR)
    return split_path[len(split_path) - 1]


def has_hidden_contents(aliaspath):
    if "." in aliaspath:
        return True
    return False


def sanitize_alias_directory(alias_path):
    alias_path = alias_path.replace(PATH_SEPARATOR, '_')
    alias_path = alias_path.replace(' ', '')
    alias_path = alias_path.replace('-', '_')
    return alias_path


def sanitize_file_alias_command(alias_path):
    alias_path = alias_path.replace('-', '_')
    alias_path = alias_path.replace('.txt', '')
    alias_path = alias_path.replace('.md', '')
    alias_path = alias_path.replace('.markdown', '')
    return alias_path


def file_is_text(full_path):
    if ".txt" in full_path:
        return True
    if ".md" in full_path:
        return True
    if ".markdown" in full_path:
        return True
    if ".json" in full_path:
        return True
    return False


def extract_path_alias(dir_path):
    alias_path = dir_path.split(root_path)[1].lower()
    alias_path = sanitize_alias_directory(alias_path)

    if not has_hidden_contents(alias_path):
        alias_bash_statement = "alias '" + alias_path + "'='cd " + dir_path + "'"
        alias_bash_statements.append(alias_bash_statement)


def extract_files_aliases(dir_path, filenames):
    alias_path = dir_path.split(root_path)[1].lower()
    alias_path = sanitize_alias_directory(alias_path)

    if not has_hidden_contents(dir_path):
        for file in filenames:
            file_alias_command = alias_path + "_" + file
            file_alias_command = sanitize_file_alias_command(file_alias_command)
            file_path = dir_path + PATH_SEPARATOR + file

            if file_is_text(file_path):
                alias_bash_statement = "alias '" + file_alias_command + "'='" + TEXT_EDITOR + " " + file_path + "'"
            else:
                alias_bash_statement = "alias '" + file_alias_command + "'='" + MEDIA_EDITOR + " " + file_path + "'"

            alias_bash_statements.append(alias_bash_statement)


def print_bash_statements():
    for alias in alias_bash_statements:
        print(alias)


def get_max_path_separators():
    result = inital_path_sep_count
    if levels is not None:
        result += levels
        return result
    return result + 99


def nothing_to_do():
    return commandArgs.destination is None and commandArgs.console is False


if nothing_to_do():
    parser.print_help()
    print("\n\nError: Use --destination or --console to use.")
    exit(0)

upper_path = get_upper_path()
root_path = unix_path.split(upper_path)[0]

for i in dataFiles:
    path = i['dirpath']
    filenames = i['filenames']
    sep_count = path.count(PATH_SEPARATOR)
    max_count = get_max_path_separators()
    if sep_count >= max_count:
        continue
    extract_path_alias(path)
    extract_files_aliases(path, filenames)

if commandArgs.destination is not None:
    dest = commandArgs.destination
    write_aliases_file(dest, alias_bash_statements, PATH_SEPARATOR)

if commandArgs.console is True:
    print_bash_statements()


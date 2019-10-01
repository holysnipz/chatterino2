#!/usr/bin/env python3
from pathlib import Path

from _generate_resources import *

ignored_files = ['qt.conf', 'resources.qrc', 'resources_autogenerated.qrc', 'windows.rc',
        'generate_resources.py', '_generate_resources.py']

# to ignore all files in a/b, add a/b to ignored_directories.
# this will ignore a/b/c/d.txt and a/b/xd.txt
ignored_directories = ['__pycache__', 'linuxinstall']

def isNotIgnored(file):
    # check if file exists in an ignored direcory
    for ignored_directory in ignored_directories:
        if file.parent.as_posix().startswith(ignored_directory):
            return False

    return file.as_posix() not in ignored_files

all_files = sorted(list(filter(isNotIgnored, \
    filter(Path.is_file, Path('.').glob('**/*')))))
image_files = sorted(list(filter(isNotIgnored, \
    filter(Path.is_file, Path('.').glob('**/*.png')))))

with open('./resources_autogenerated.qrc', 'w') as out:
    out.write(resources_header)
    for file in all_files:
        out.write(f"    <file>{file.as_posix()}</file>\n")
    out.write(resources_footer)

with open('../src/autogenerated/ResourcesAutogen.cpp', 'w') as out:
    out.write(source_header)
    for file in sorted(image_files):
        var_name = file.with_suffix("").as_posix().replace("/",".")
        out.write(f'    this->{var_name}')
        out.write(f' = QPixmap(":/{file.as_posix()}");\n')
    out.write(source_footer)

def writeHeader(out, name, element, indent):
    if isinstance(element, dict):
        if name != "":
            out.write(f"{indent}struct {{\n")
        for (key, value) in element.items():
            writeHeader(out, key, value, indent + '    ')
        if name != "":
            out.write(f"{indent}}} {name};\n");
    else:
        out.write(f"{indent}QPixmap {element};\n")

with open('../src/autogenerated/ResourcesAutogen.hpp', 'w') as out:
    out.write(header_header)

    elements = {}
    for file in sorted(image_files):
        elements_ref = elements
        directories = file.as_posix().split('/')[:-1]
        filename = file.stem
        for directory in directories:
            if directory not in elements_ref:
                elements_ref[directory] = {}
            elements_ref = elements_ref[directory]
        elements_ref[filename] = filename

    writeHeader(out, "", elements, '')

    out.write(header_footer)


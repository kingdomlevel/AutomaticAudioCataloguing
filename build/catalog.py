from contextlib import closing
import os
import time
import wave
import json
# simple parser for extracting basic catalog info from file data


def check_catalogued(core):
    # method to check if the filename adheres to SMC naming convention (boolean return)
    # NOT FOOLPROOF but should do the job
    check = False
    if len(core) == 17:
        if core[15].lower() == 'm' or core[15].lower() == 'c' or core[16] == '0':
            check = True
    return check


def get_resource_owner(file_with_ext):
    owner = file_with_ext[:3]
    return owner


def get_original_format(file_with_ext):
    # equivelant to a use/switch statement
    def audio_format(char):
        char = char.lower()
        return {
            'c': "Cassette",
            'd': "DAT",
            'f': "Online",
            't': "Reel",
            'v': "Vinyl",
        }.get(char, None)
    # check appropriate char in filename
    c = file_with_ext[3]
    return audio_format(c)


def get_shelf_mark(file_with_ext):
    shelf_mark = file_with_ext[4:12]
    shelf_mark = shelf_mark.strip('Xx')
    return shelf_mark


def get_side(file_with_ext):
    side = int(file_with_ext[13:15])
    return side


def get_master_or_copy(file_with_ext):
    c = file_with_ext[15]
    c = c.lower()
    if c == 'm':
        transfer = "Master (%c)" % file_with_ext[16]
    elif c == 'c':
        transfer = "Copy (%c)" % file_with_ext[16]
    else:
        transfer = None
    return transfer


def get_length(file_with_path):
    with closing(wave.open(file_with_path, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        length = frames / float(rate)
        # length = time.strftime('%H:%M:%S', time.gmtime(length))
        return length


def generate_catalog_doc(file_with_path):
    # create a JSON document containing catalog information from file
    path, file_with_ext = os.path.split(file_with_path)
    core, extension = os.path.splitext(file_with_ext)
    duration = get_length(file_with_path)
    # if the item has already been catalogued with SMC naming convention, we can parse that data
    if check_catalogued(core):
        owner = get_resource_owner(file_with_ext)
        audio_format = get_original_format(file_with_ext)
        mark = get_shelf_mark(file_with_ext)
        side = get_side(file_with_ext)
        transfer = get_master_or_copy(file_with_ext)
    data = json.dumps({
        "Filename": file_with_ext,
        "Duration": duration,
        "ResourceOwner": owner,
        "OriginalFormat": audio_format,
        "ShelfMark": mark,
        "Side": side,
        "Transfer": transfer
    })
    return data

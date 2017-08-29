from contextlib import closing
import os
import time
import wave
import json
# simple parser for extracting basic catalog info from file data


def __check_catalogued(core):
    # method to check if the filename adheres to SMC naming convention (boolean return)
    # NOT FOOLPROOF but should do the job
    check = False
    if len(core) == 17:
        if core[15].lower() == 'm' or core[15].lower() == 'c' or core[16] == '0':
            check = True
    return check


def __get_resource_owner(file_with_ext):
    owner = file_with_ext[:3]
    return owner


def __get_original_format(file_with_ext):
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


def __get_shelf_mark(file_with_ext):
    shelf_mark = file_with_ext[4:12]
    shelf_mark = shelf_mark.strip('Xx')
    return shelf_mark


def __get_side(file_with_ext):
    side = int(file_with_ext[13:15])
    return side


def __get_master_or_copy(file_with_ext):
    c = file_with_ext[15]
    c = c.lower()
    if c == 'm':
        transfer = "Master (%c)" % file_with_ext[16]
    elif c == 'c':
        transfer = "Copy (%c)" % file_with_ext[16]
    else:
        transfer = None
    return transfer


def __get_length(file_with_path):
    # returns length of audio file in seconds; stores as type float
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
    # if the item has already been catalogued with SMC naming convention, we can parse that data
    if __check_catalogued(core):
        owner = __get_resource_owner(file_with_ext)
        audio_format = __get_original_format(file_with_ext)
        mark = __get_shelf_mark(file_with_ext)
        side = __get_side(file_with_ext)
        transfer = __get_master_or_copy(file_with_ext)
    else:
        # we don't know this data and want it to be null in the database
        owner, audio_format, mark, side, transfer = (None,)*5

    data = json.dumps({
        "SMC_ID": core,
        "ResourceOwner": owner,
        "OriginalFormat": audio_format,
        "ShelfMark": mark,
        "Side": side,
        "Transfer": transfer
    })
    return data

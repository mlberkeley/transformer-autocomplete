import pprint
from utils import LOGGER
import torch

def transformer_completer(request_data):
    pass


def ComputeCandidates(request_data):
    print("computing candidates")
    pprint.pprint(request_data)
    file_data = request_data['file_data']
    if type(file_data) == dict:
        LOGGER.info("Keys of file data: {}".format(file_data.keys()))
        filepath = request_data['filepath']#list(file_data.keys())[0]
        LOGGER.info("File of file data: {}".format(filepath))
        file_data = file_data[filepath]['contents']
        file_data = file_data.split('\n')
        line = file_data[request_data['line_num']-1]
        line_up_to = line[:request_data['column_num']]
        completion = line_up_to[::-1]
        return [{'insertion_text': completion,
                'menu_text': completion,
                'extra_menu_info': None,
                'kind': None}]
    else:
        print(type(file_data))
        line = file_data[request_data['line_num']-1]
        line_up_to = line[:request_data['column_num']]
        completion = line_up_to[::-1]
        line_up_to = line[:request_data['column_num']]
        completion = line_up_to[::-1]
        return [{'insertion_text': completion,
                'menu_text': completion,
                'extra_menu_info': None,
                'kind': None}]
        return [{'insertion_text': completion,
                'menu_text': completion,
                'extra_menu_info': None,
                'kind': None}]



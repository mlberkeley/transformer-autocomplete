from utils import ToUnicode
from base_request import BaseRequest, DisplayServerException
from test_request import TestRequest

#import vimsupport
from vimsupport import NO_COMPLETIONS

class CompletionRequest(BaseRequest):

    def __init__(self, request_data):
        super(CompletionRequest, self).__init__()
        self.request_data = request_data
        self._response_future = None

    def Start(self):
        self._response_future = self.PostDataToHandlerAsync(self.request_data,
                                                            'completions')
    
    def Done(self):
        return bool(self._response_future) and self._response_future.done()

    def _RawResponse(self):
        if not self._response_future:
            return NO_COMPLETIONS
        response = self.HandleFuture(self._response_future,
                                     truncate_message=True)
        errors = response.pop('errors', [])

        response['line'] = self.request_data['line_num']
        response['column'] = self.request_data['column_num']
        return response

    def Response(self):
        response = self._RawResponse()
        response['completions'] = _ConvertCompletionDatasToVimDatas(
            response['completions'])
        return response

    def OnCompleteDone(self):
        if not self.Done():
            return
        else:
            pass #TODO

def _ConvertCompletionDatasToVimDatas(response_data):
    return [_ConvertCompletionDataToVimData(i, x) for i, x in enumerate(response_data)]

def _ConvertCompletionDataToVimData( completion_identifier, completion_data ):
  # See :h complete-items for a description of the dictionary fields.
    return {
        'word'     : completion_data[ 'insertion_text' ],
        'abbr'     : completion_data.get( 'menu_text', '' ),
        'menu'     : completion_data.get( 'extra_menu_info', '' ),
        'kind'     : ToUnicode( completion_data.get( 'kind', '' ) )[ :1 ].lower(),
        'equal'    : 1,
        'dup'      : 1,
        'empty'    : 1,
        # We store the completion item index as a string in the completion
        # user_data. This allows us to identify the _exact_ item that was completed
        # in the CompleteDone handler, by inspecting this item from v:completed_item
        #
        # We convert to string because completion user data items must be strings.
        #
        # Note: Not all versions of Vim support this (added in 8.0.1483), but adding
        # the item to the dictionary is harmless in earlier Vims.
        'user_data': str( completion_identifier )
    }

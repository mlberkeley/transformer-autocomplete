import pprint
import time
from utils import LOGGER

BAD_SET = "\n"
class Completer(object):
    def __init__(self):
        pass
    
    @staticmethod
    def process_request_data(request_data):
        file_data = request_data['file_data']
        if type(file_data) == dict:
            LOGGER.info("Keys of file data: {}".format(file_data.keys()))
            filepath = request_data['filepath']#list(file_data.keys())[0]
            LOGGER.info("File of file data: {}".format(filepath))
            file_data = file_data[filepath]['contents']
        lines = file_data.split('\n')
        return {'lines': lines,
                'line_num': request_data['line_num']-1,
                'column_num': request_data['column_num']}

    def filter_candidates(candidates):
        ret = []
        for candidate in candidates:
            if candidate not in ret:
                ret.append(candidate)
        return ret
            
    def get_context(self, info):
        if self.use_line:
            line = info['lines'][info['line_num']]
            return line[:info['column_num']] # do we sub 1 here
        else:
            num_chars = info['column_num']
            initial_line = info['line_num']
            context_lines = [info['lines'][initial_line]]
            if initial_line > 0:
                for line_num in range(initial_line-1, -1, -1):
                    print(num_chars)
                    line = info['lines'][line_num]
                    if line == "":
                        break
                    num_chars += len(line) + 1
                    if num_chars > self.seq_len:
                        break
                for i in range(line_num, initial_line):
                    context_lines.append(info['lines'][i]) 

            context = "".join(context_lines)
            if len(context) > self.seq_len:
                context = context[-self.seq_len:]
            LOGGER.info("Context: {}".format(context))
            return context


class TransformerCompleter(Completer):
    def __init__(self, seq_len=100, pred_len=8, top_k=3, use_line=False, num_completions=3):
        super().__init__()
        self.seq_len = seq_len
        self.pred_len = pred_len
        self.top_k = top_k
        self.use_line = use_line
        self.num_completions = num_completions
        self.setup_model()
        self.data = []
        print("Setup transformer model")

    def setup_model(self):
        import transformer_hf as transformer_hf
        self.inference = transformer_hf.inference

    def compute_single(self, context):
        start_time = time.time()
        completion = self.inference(phrase=context,
                                    length=self.pred_len,
                                    top_k=self.top_k)
        inf_time = time.time() - start_time
        self.data.append({'seq_len': len(context), 'time': inf_time, 'pred_len': self.pred_len})
        pprint.pprint(self.data)
        print("{} | {} || took {} seconds seq len {}".format(context, completion, time.time()-start_time, len(context)))
        LOGGER.info("{} | {}  || took {} seconds".format(context, completion, time.time()-start_time))
        assert isinstance(completion, str), 'Completion is not string'
        completion = "".join([c for c in completion if c not in BAD_SET])
        return completion

        
    def compute_candidates(self, request_data):
        assert hasattr(self, 'inference'), "Model not set up in completer"
        info = Completer.process_request_data(request_data)
        context = self.get_context(info)
        completions = [self.compute_single(context) for i in range(self.num_completions)]
        completions = Completer.filter_candidates(completions)
        return [{'insertion_text': completion,
                  'menu_text': completion,
                  'extra_menu_info': None,
                  'kind': None} for completion in completions]

class MirrorCompleter(Completer):

    def __init__(self, seq_len=50, use_line=False):
        super().__init__()
        self.seq_len = seq_len
        self.use_line = use_line

    def compute_single(self, context):
        completion = context[::-1]
        return completion
        
    def compute_candidates(self, request_data):
        info = Completer.process_request_data(request_data)
        context = self.get_context(info)
        completion = self.compute_single(context)
        return [{'insertion_text': completion,
                  'menu_text': completion,
                  'extra_menu_info': None,
                  'kind': None}]

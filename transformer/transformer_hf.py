import torch
from transformers import *
import torch.nn.functional as F
#from run_generation import top_k_top_p_filtering
#from run_generation import sample_sequence

#print(inference(model=model,enc=tokenizer,phrase='Once upon a', length=5))
'''
Method
def inference(phrase, top_k, top_p, length):
    phrase - input string
    top_k - integer of top k values from output logit
    top_p - double of top p (probability) values from output logit
    length = # of next words
'''

# Load pre-trained model tokenizer (vocabulary)
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

# Encode a text inputs
#text = "Happy Birthday to"
#indexed_tokens = tokenizer.encode(text)

# Convert indexed tokens in a PyTorch tensor
#tokens_tensor = torch.tensor([indexed_tokens])

# Load pre-trained model (weights)
model = GPT2LMHeadModel.from_pretrained('gpt2')

# Set the model in evaluation mode to deactivate the DropOut modules
model.eval()

# If you have a GPU, put everything on cuda
#CUDA - Compute Unified Device Architecture
#.to() - Sets dtype or device to a tensor
#tokens_tensor = tokens_tensor.to('cpu')
model.to('cpu')

# Predict all tokens
#with torch.no_grad():
    #outputs = model(tokens_tensor)
    #filter_outputs = top_k_top_p_filtering(logits=outputs, top_k=10, top_p=0.5)
    #predictions = outputs[0]

# Get the predicted next sub-word
#predicted_index = torch.argmax(predictions[0, -1, :]).item()
#predicted_text = tokenizer.decode(indexed_tokens + [predicted_index])

# Print the predicted word
#print(predicted_text)

def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):
    """ Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
    https://gist.github.com/thomwolf/1a5a29f6962089e871b94cbd09daf317
        Args:
            logits: logits distribution shape (..., vocabulary size)
            top_k >0: keep only top k tokens with highest probability (top-k filtering).
            top_p >0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
    """
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = torch.tensor(cumulative_probs >= top_p, dtype=torch.uint8)
        #print(sorted_indices_to_remove.shape)
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0
        
        #Zeros_like - creates tensor with zeros same length as input
        indices_to_remove = torch.zeros_like(logits, dtype=torch.uint8).scatter_(dim=-1, index=sorted_indices, src=sorted_indices_to_remove)
        #indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits

def inference(model = model, enc = tokenizer, phrase= '', top_k = 1, top_p = 0.9, length = 1):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    nsamples = 1
    length = length
    temperature = 1.2
    top_k = top_k
    top_p = top_p
    batch_size = 1
    stop_token = [enc.encoder[x] for x in ('<|endoftext|>', '.', '?', '!')]
    assert nsamples % batch_size == 0

    if length == -1:
        length = model.config.n_ctx // 2
    elif length > model.config.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % model.config.n_ctx)

    context_tokens = enc.encode(phrase) if phrase else [enc.encoder['<|endoftext|>']]
    generated = 0
    out = sample_sequence(
        model=model, length=length,
        context=context_tokens,
        start_token=None,
        batch_size=batch_size,
        temperature=temperature, top_k=top_k, device=device,
        top_p=top_p,
        stop_token=[]#stop_token
    )
    out = out[:, len(context_tokens):].tolist()
    return enc.decode(out[0])

def sample_sequence(model, length, start_token=None, batch_size=None, context=None, temperature=1, top_k=0,
                    device='cuda', top_p=0, stop_token=[]):
    if start_token is None:
        assert context is not None, 'Specify exactly one of start_token and context!'
        context = torch.tensor(context, device=device, dtype=torch.long).unsqueeze(0).repeat(batch_size, 1)
    else:
        assert context is None, 'Specify exactly one of start_token and context!'
        context = torch.full((batch_size, 1), start_token, device=device, dtype=torch.long)
    prev = context
    output = context
    past = None

    count = 0
    with torch.no_grad():
        while count < length:
            logits, past = model(prev, past=past)
            logits = logits[:, -1, :] / temperature
            logits = top_k_top_p_filtering(logits, top_p=top_p, top_k=top_k)
            probs = F.softmax(logits, dim=-1)
            prev = torch.multinomial(probs, num_samples=1)
            output = torch.cat((output, prev), dim=1)
            count += 1
            if prev in stop_token:
                break
    return output


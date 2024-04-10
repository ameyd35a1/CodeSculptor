from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig, BitsAndBytesConfig
from transformers import pipeline
import transformers
import torch
import logging 
from computeInterface import ComputeData

model = None
tokenizer = None
device = 'cuda' if torch.cuda.is_available() else 'cpu'
#print("Device:", device)
# if device == 'cuda':
#     print(torch.cuda.get_device_name(0))

# Create and configure logger
logging.basicConfig(filename="newfile_completion_model.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
# Creating an object
logger = logging.getLogger()
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

def LoadConfig():
    ##Configure the 4bit qunatized model
    bnb_config = BitsAndBytesConfig(
                                load_in_4bit=True,
                                bnb_4bit_use_double_quant=True,
                                bnb_4bit_quant_type="nf4",
                                bnb_4bit_compute_dtype=torch.bfloat16,
                               )
    return bnb_config

def LoadModel():
    global model
    global tokenizer

    bnb_config = LoadConfig()
    model_id = "codellama/CodeLlama-7b-Instruct-hf"
    logger.debug("Loading Tokenizer...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    logger.debug("Tokenizer loaded")

    logger.debug("Loading Model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,
        quantization_config=bnb_config,
    )
    logger.debug("Model loaded")

def ComputeModelInformation(data: ComputeData):
    global device
    PROMPT = f"<s>[INST] <<SYS>>\n{data.system}\n<</SYS>>\n\n{data.message}[/INST]"
    logger.debug(PROMPT)

    logger.debug("Tokenizing input content")
    inputs = tokenizer(PROMPT, return_tensors="pt").to(device)
    input_ids = inputs["input_ids"]

    logger.debug("Processing model...")
    generated_ids = model.generate(
        input_ids= input_ids,
        attention_mask= inputs['attention_mask'],
        pad_token_id=tokenizer.eos_token_id,
        max_new_tokens= 1024
    )
    
    logger.debug("Processing Output...")
    new_tokens = generated_ids[0][input_ids.shape[-1]:]
    outputResponse = tokenizer.decode(new_tokens, skip_special_tokens=True)
    logger.debug(outputResponse)

    return outputResponse
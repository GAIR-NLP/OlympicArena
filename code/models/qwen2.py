from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "../"))
from models.base_model import BaseModel



class Qwen2(BaseModel):
    def __init__(self, model_path=None):
        self.model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    torch_dtype="auto",
                    device_map="auto",
                    trust_remote_code=True
                )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        
    def generate_single(self, example):
        prompt = self.generate_prompt(example)
        messages = [
                    {"role": "system", "content": "You are a highly skilled student proficient in solving scientific problems."},
                    {"role": "user", "content": prompt}
                ]
        text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        model_inputs = self.tokenizer([text], return_tensors="pt").to("cuda")
        if example["subject"] != "CS":
            generated_ids = self.model.generate(
                                model_inputs.input_ids,
                                max_new_tokens=2048,
                                do_sample=False
                            )
        else:
            generated_ids = self.model.generate(
                                model_inputs.input_ids,
                                max_new_tokens=2048,
                                do_sample=True,
                                temperature=0.2
                            )
            
        
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return response


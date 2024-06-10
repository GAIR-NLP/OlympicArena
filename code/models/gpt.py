from openai import OpenAI
import os
import re
import concurrent.futures
import time
from tqdm import tqdm
from models.base_model import BaseModel
from utils import *


class GPT_4o(BaseModel):
    def __init__(self, api_key=None, base_url=None, mode=None):
        super().__init__(mode)
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)

    def lmm_generate(self, example):
        # Interleaved Text and Images
        user_content = []
        prompt = self.generate_prompt(example)
        if example["language"] == "ZH":
            segments = re.split(r'(\[图\d+\])', prompt)
        else:
            segments = re.split(r'(\[figure\d+\])', prompt)
        for seg in segments:
            if not seg.strip():
                continue
            if not seg.startswith('['):
                user_content.append({"type": "text", "text": seg})
            else:
                if example["language"] == "ZH":
                    figure_key = seg[2:-1]
                else:
                    figure_key = seg[7:-1]
                    
                if self.mode == "multi-modal":
                    user_content.append({"type": "image_url", "image_url": {"url": example["figure_urls"][int(figure_key)-1]}})
                else: # text-only
                    user_content.append({"type": "text", "text": seg})


        message = [
            {"role": "system", "content": "You are a highly skilled student proficient in solving scientific problems."},
            {"role": "user", "content": user_content}
        ]
        attempt_count = 0
        max_attempts = 5
        while attempt_count < max_attempts:
            try:
                response = self.client.chat.completions.create(
                    model = "gpt-4o",
                    messages= message,
                    max_tokens=2048,
                    temperature=0.0 if example["subject"] != "CS" else 0.2,
                    seed=123
                )
                return response.choices[0].message.content
            except Exception as e:
                attempt_count += 1
                print(f"Error occurred when calling openai api! {e}")
                time.sleep(15)
        return None
                

    def generate_single(self, example):
        return self.lmm_generate(example)

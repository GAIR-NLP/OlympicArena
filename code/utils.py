import json
import chardet
import os
import re
from datasets import load_dataset, concatenate_datasets


def get_encoding_type(file_path):
    with open(file_path, 'rb') as f:
        sample = f.read(1024)
        cur_encoding = chardet.detect(sample)['encoding']
        return cur_encoding

def read_json(file_path):
    with open(file_path, 'r', encoding=get_encoding_type(file_path), errors="ignore") as f:
        data = json.load(f)
        return data
    
def write_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8', errors="ignore") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
        
def load_data(hf_data_path, split):
    """
    It is ok to test only a subset (e.g., only English subset),
    You can filter the desired data by modifying this function.
    """
    
    subjects = ["Math", "Physics", "Chemistry", "Biology", "Geography", "Astronomy", "CS"]
    datasets = []
    for subject in subjects:
        dataset = load_dataset(hf_data_path, subject, split=split)
        datasets.append(dataset)
    return concatenate_datasets(datasets)


def contains_chinese(d):
    def is_chinese_char(ch):
        return '\u4e00' <= ch <= '\u9fff'

    def check(value):
        if isinstance(value, str):
            return any(is_chinese_char(ch) for ch in value)
        elif isinstance(value, dict):
            return any(check(v) for v in value.values())
        elif isinstance(value, list):
            return any(check(item) for item in value)
        return False

    return check(d)


def extract_code(text):
    pattern = r"```(?:python)?(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return None
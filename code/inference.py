import os
import argparse
from tqdm import tqdm
from utils import *
from models import *
from judge import Judger


def inference(args, datasets):
    non_cs_inference_tasks = []
    cs_inference_tasks = []
    for example in datasets:
        output_path = os.path.join(args.model_output_dir, example["subject"], example["id"]+".json")
        if os.path.exists(output_path):
            continue
        if example["subject"] != "CS":
            non_cs_inference_tasks.append(example)
        else:
            cs_inference_tasks.append(example)
    
    # You can also customize your own model by inheriting the base_model.
    if args.model == "gpt-4o":
        model = GPT_4o(api_key=args.api_key, base_url=args.base_url, mode="multi-modal")
    
    errors = []
    
    def save_callback(index, model_output, cs_flag):
        if cs_flag:
            example = cs_inference_tasks[index]
        else:
            example = non_cs_inference_tasks[index]
        problem_id = example["id"]

        
        save_path = os.path.join(args.model_output_dir, example["subject"], example["id"]+".json")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        save_dict = {}
        save_dict["id"] = example["id"]
        save_dict["answer_type"] = example["answer_type"]
        save_dict["type_sequence"] = example["type_sequence"]
        save_dict["model_output"] = model_output
        
        if model_output is None:  # Handle errors
            print("Model inference error: ", problem_id)
            errors.append(problem_id)
            save_dict["model_answer"] = None
            if args.save_error:
                write_json(save_dict, save_path)
            return
        
        
        extractor = Judger()
        if example["subject"] != "CS":
            save_dict["model_answer"] = extractor.extract_boxed_answer(model_output)
        else:
            code_snippets = [code for text in model_output if (code := extract_code(text))]
            save_dict["model_answer"] = code_snippets

        write_json(save_dict, save_path)
    
    
    print("Inference for non-CS subjects")
    model.generate_batch(non_cs_inference_tasks, save_callback, max_workers=args.batch)
    
    print("Inference for CS subject")
    model.generate_batch_N(cs_inference_tasks, 5, save_callback, max_workers=args.batch)
        
    if len(errors) > 0:
        print("Error Inference:")
        print(errors)
        
def generate_output_json(args):
    output_json_path = os.path.join(args.model_output_dir, args.model+"_"+args.split+".json")
    output_dict = {}
    
    for subject in os.listdir(args.model_output_dir):
        subject_dir = os.path.join(args.model_output_dir, subject)
        if os.path.isdir(subject_dir):
            for problem_id in os.listdir(subject_dir):
                if problem_id.endswith(".json"):
                    file_path = os.path.join(subject_dir, problem_id)
                    d = read_json(file_path)
                    output_dict[d["id"]] = {"model_answer": d.get("model_answer", None)}

                
    write_json(output_dict, output_json_path)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--hf_data_path', type = str, default="GAIR/OlympicArena")
    parser.add_argument('--model_output_dir', type=str, default="./model_output/")
    parser.add_argument("--split", type=str, default="val")
    parser.add_argument("--model", type=str, default="gpt-4o")
    parser.add_argument("--batch", type=int, default=15, help="batch size for inference")
    parser.add_argument("--api_key", type=str, default=None)
    parser.add_argument("--base_url", type=str, default=None)
    parser.add_argument('--save_error', action='store_true', help='save error inference as None, default is False')
    
    args = parser.parse_args()
    
    args.model_output_dir = os.path.join(args.model_output_dir, args.model)
    os.makedirs(args.model_output_dir, exist_ok=True)
    
    # load data
    datasets = load_data(args.hf_data_path, args.split)
    
    inference(args, datasets)
    
    generate_output_json(args)
    
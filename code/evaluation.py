import os
import argparse
from tqdm import tqdm
from utils import *
from code_utils import *
from models import *
from judge import Judger
    
def evaluate(args, datasets, output_json, K=1):
    
    judger = Judger()
    
    for example in tqdm(datasets, desc="Evaluating"):
        result_path = os.path.join(args.result_dir, example["subject"], example["id"]+".json")
        if os.path.exists(result_path):
            continue
        
        if example["subject"] != "CS":
            problem_id = example["id"]
            type_sequence = example["type_sequence"]
            answer = example["answer"]
            if len(answer) == 1:
                answer = answer[0]
            if problem_id in output_json and output_json[problem_id]["model_answer"] is not None:
                flag = judger.auto_judge(output_json[problem_id]["model_answer"], answer, type_sequence)
            else:
                flag = False
                
            result = flag
            
        else:
            problem_id = example["id"]
            
            if problem_id not in output_json or output_json[problem_id]["model_answer"] is None:
                result = 0
            else:
                test_cases = example["test_cases"]
                code_snippets = output_json[problem_id]["model_answer"]
                code_snippets = [snippet for snippet in code_snippets if snippet is not None]
                if code_snippets:
                    code_results = code_executor(code_snippets, test_cases)
                    num_correct = sum(code_result == "Passed" for code_result in code_results) 
                    num_samples = len(code_snippets)
                    pass_at_k = estimate_pass_at_k([num_samples], [num_correct], K)[0]
                    
                    result = pass_at_k
                else:
                    result = 0
                
            
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        write_json({"id": problem_id, 
                    "answer_type": example["answer_type"], 
                    "answer": example.get("answer", None), 
                    "model_answer": output_json[problem_id]["model_answer"] if problem_id in output_json else None, 
                    "result": result, 
                    "subject": example["subject"], 
                    "language": example["language"], 
                    "modality": example["modality"]}, 
                   result_path)
            
    
def generate_result_json(args):
    output_json_path = os.path.join(args.result_dir, args.model+"_"+args.split+".json")
    result_json = {}
    
    for subject in os.listdir(args.result_dir):
        subject_dir = os.path.join(args.result_dir, subject)
        if os.path.isdir(subject_dir):
            for problem_id in os.listdir(subject_dir):
                if problem_id.endswith(".json"):
                    d = read_json(os.path.join(subject_dir, problem_id))
                    result_json[d["id"]] = {"result": d["result"], "subject": d["subject"], "language": d["language"], "modality": d["modality"]}
                    
    write_json(result_json, output_json_path)
           

def calculate_statistics(result_json):
    total_count = 0
    total_correct = 0
    
    subject_totals = {"Math": 0, "Physics": 0, "Chemistry": 0, "Biology": 0, "Geography": 0, "Astronomy": 0, "CS": 0}
    subject_corrects = {"Math": 0, "Physics": 0, "Chemistry": 0, "Biology": 0, "Geography": 0, "Astronomy": 0, "CS": 0}
    
    language_totals = {"EN": 0, "ZH": 0}
    language_corrects = {"EN": 0, "ZH": 0}
    
    modality_totals = {"text-only": 0, "multi-modal": 0}
    modality_corrects = {"text-only": 0, "multi-modal": 0}
    
    for key, value in result_json.items():
        total_count += 1
        subject_totals[value["subject"]] += 1
        language_totals[value["language"]] += 1
        modality_totals[value["modality"]] += 1
        
        result = value["result"]
        
        if result:
            total_correct += 1
            if type(result) == bool:
                subject_corrects[value["subject"]] += 1
                language_corrects[value["language"]] += 1
                modality_corrects[value["modality"]] += 1
            else:
                subject_corrects[value["subject"]] += result
                language_corrects[value["language"]] += 1
                modality_corrects[value["modality"]] += 1
                
    total_rate = total_correct / total_count
    subject_rate = {key: subject_corrects[key] / subject_totals[key] for key in subject_totals}
    language_rate = {key: language_corrects[key] / language_totals[key] for key in language_totals}
    modality_rate = {key: modality_corrects[key] / modality_totals[key] for key in modality_totals}
    
    return total_rate, subject_rate, language_rate, modality_rate
        
        
def print_statistics(total_rate, subject_rate, language_rate, modality_rate):
    print("---------------------------")
    print("Total correct rate: ", total_rate)
    print("---------------------------")
    print("Subject correct rate: ")
    for key, value in subject_rate.items():
        print(key, value)
    print("---------------------------")
    print("Language correct rate: ")
    for key, value in language_rate.items():
        print(key, value)
    print("---------------------------")
    print("Modality correct rate: ")
    for key, value in modality_rate.items():
        print(key, value)
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--hf_data_path', type = str, default="./data/")
    parser.add_argument('--model_output_dir', type=str, default="./model_output/")
    parser.add_argument('--result_dir', type=str, default="./result/")
    parser.add_argument("--split", type=str, default="val", help="only answers of the validation set are released")
    parser.add_argument("--model", type=str, default="gpt-4o")

    
    args = parser.parse_args()
    
    args.output_json_path = os.path.join(args.model_output_dir, args.model, args.model+"_"+args.split+".json")
    assert os.path.exists(args.output_json_path), "The model's output json file doesn't exist!"
    output_json = read_json(args.output_json_path)
    
    args.result_dir = os.path.join(args.result_dir, args.model)
    os.makedirs(args.result_dir, exist_ok=True)
    
    # load data
    datasets = load_data(args.hf_data_path, args.split)
    
    evaluate(args, datasets, output_json)
    
    generate_result_json(args)
    
    output_json_path = os.path.join(args.result_dir, args.model+"_"+args.split+".json")
    
    total_rate, subject_rate, language_rate, modality_rate = calculate_statistics(read_json(output_json_path))
    print_statistics(total_rate, subject_rate, language_rate, modality_rate)
    

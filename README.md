# OlympicArena: Benchmarking Multi-discipline Cognitive Reasoning for Superintelligent AI

<p align="center"> <img src="images/overview.png" style="width: 85%;" id="title-icon">       </p>

<p align="center">
  🤗 <a href="https://huggingface.co/datasets/GAIR/OlympicArena" target="_blank">Hugging Face</a>
</p>

## Contents

- [Introduction](#introduction)
- [How to use?](#how-to-use)
  - [Setup](#setup)
  - [Load Data](#load-data)
  - [Inference](#inference)
  - [Evaluation](#evaluation)
  - [Submit your result](#submit-your-result)
- [Citation](#citation)


## Introduction

**OlympicArena** is a comprehensive, highly-challenging, and rigorously curated benchmark featuring a detailed, fine-grained evaluation mechanism designed to assess advanced AI capabilities across a broad spectrum of Olympic-level challenges. We aim to advance AI towards superintelligence, equipping it to address more complex challenges in science and beyond.

## How to use?

### Setup

To begin using the OlympicArena benchmark, you need to install the required dependencies. You can do this by running the following command:

```bash
pip install -r requirements.txt
```

If you need to define your own model for inference or evaluation, you will also need to install any additional packages required by your model (e.g., transformers). 

### Load Data

We have released the data for seven disciplines on [Hugging Face](https://huggingface.co/datasets/GAIR/OlympicArena). Each discipline is divided into val and test splits. The val split includes the answers for small-scale testing, while the answers for the test split are not publicly available. You can submit your results to our platform for evaluation (refer to [Submit your result](#submit-your-result)).

Loading the data is very simple. You can use the following code snippet:

```python
from datasets import load_dataset

# Load the dataset for a specific discipline, e.g., Math
dataset = load_dataset("GAIR/OlympicArena", "Math", split="val")

print(dataset[0])
```

Each data entry contains the following fields:

- `id`: The unique identifier for each problem
- `problem`: The problem statement
- `prompt`: The prompt used as input to the model (as used in the paper); we also encourage users to try their own prompts
- `figure_urls`: Links to images that appear in the problem, in order
- `answer`: The answer to the problem
- `answer_type`: The type of the answer
- `unit`: The unit corresponding to the answer
- `answer_sequence`: The sequence in which the model should provide answers if multiple quantities are required
- `type_sequence`: The sequence of `answer_type` for each quantity if multiple quantities are required
- `test_cases`: Test cases used for evaluation in CS code generation problems
- `subject`: The subject of the problem
- `language`: The language of the problem, where EN represents English and ZH represents Chinese
- `modality`: The modality type of the problem statement, where `text-only` indicates the problem statement does not contain images, and `multi-modal` indicates the problem statement contains images


If you only want to use a specific subset of our dataset (e.g., only English problems, or only text-only problems), you just need to modify the load_data code snippet ([./code/utils.py](./code/utils.py)):

```python
def load_data(hf_data_path, split, language=None, modality=None):
    subjects = ["Math", "Physics", "Chemistry", "Biology", "Geography", "Astronomy", "CS"]
    datasets = []
    for subject in subjects:
        dataset = load_dataset(hf_data_path, subject, split=split)
        if language:
            dataset = dataset.filter(lambda x: x['language'] == language)
        if modality:
            dataset = dataset.filter(lambda x: x['modality'] == modality)
        
        datasets.append(dataset)
    return concatenate_datasets(datasets)
```

### Inference

To run inference, first navigate to the code directory:
```bash
cd code
```

Then, execute the following command to run the inference script:

```bash
python inference.py \
    --hf_data_path GAIR/OlympicArena \
    --model_output_dir ./model_output/ \
    --split val \
    --model gpt-4o \
    --batch 15 \
    --api_key YOUR_API_KEY \
    --base_url YOUR_BASE_URL \
    --save_error
```

- `--hf_data_path`: Path to the Hugging Face dataset (default: "GAIR/OlympicArena")
- `--model_output_dir`: Directory to save the model output (default: "./model_output/")
- `--split`: Dataset split to use for inference, either "val" or "test"
- `--model`: Model name to use for inference
- `--batch`: Batch size for inference
- `--api_key`: Your API key, if required
- `--base_url`: Base URL for the API, if required
- `--save_error`: Save errors as None (default: False). If set, any problem that fails or encounters an error during inference will be saved with an answer of `None`.

After inference is complete, a JSON file containing the inference outputs will be generated in `model_output_dir/model`, which can be used for evaluation.

If you want to use your own model for inference, you can enter the `model` folder and define your model as a subclass of `BaseModel`.


### Evaluation

You can only run evaluation locally on the val set (because the answers for the test set are not publicly available). First, ensure that the corresponding JSON file representing the inference outputs is generated in the inference step.

Then you can execute the following script from the command line:

```bash
python evaluation.py \
     --hf_data_path GAIR/OlympicArena \
     --model_output_dir ./model_output/ \
     --result_dir ./result/ \
     --split val \
     --model gpt-4o
```

Finally, we will print the overall accuracy, accuracy for different subjects, accuracy for different languages, and accuracy for different modalities.

### Submit your result

We are working hard to build a platform that allows you to submit your results for automated evaluation.

## Citation


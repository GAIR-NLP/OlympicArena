import contextlib
import io
import sys
import os
import tempfile
import multiprocessing
import signal
import subprocess

import numpy as np
import itertools
from typing import Union, List

def execute_code(args):
    code, test_cases = args
    with create_tempdir(), swallow_io() as (inp, out, err):
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.py') as code_file:
            code_file_name = code_file.name
            code_file.write(code)
            code_file.flush()
        all_passed = True
        for test in test_cases:
            input_data = test['input']
            try:
                with time_limit(5):
                    result = subprocess.run(
                        ['python', code_file_name],
                        input=input_data,
                        text=True,
                        capture_output=True,
                        timeout=5  # Timeout for each code execution
                    )
                if result.stdout.strip() != test['output'].strip():
                    all_passed = False
                    break
            except (TimeoutException, subprocess.TimeoutExpired):
                return "Timeout"
            except subprocess.CalledProcessError:
                all_passed = False
                break
            except Exception as e:
                return "Error"
            
    os.unlink(code_file_name)  # Clean up the temp file
    return "Passed" if all_passed else "Error"

def convert_to_list_of_dicts(input_output_dict):
    input_list = input_output_dict.get("input", [])
    output_list = input_output_dict.get("output", [])
    
    if len(input_list) != len(output_list):
        raise ValueError("Input and output lists must be of the same length")
    
    return [{"input": inp, "output": out} for inp, out in zip(input_list, output_list)]


def code_executor(codes, test_cases):
    test_cases = convert_to_list_of_dicts(test_cases)
    code_test_pairs = [(code, test_cases) for code in codes]
    results = []
    
    for pair in code_test_pairs:
        result = execute_code(pair)
        results.append(result)
    
    return results

class TimeoutException(Exception):
    pass

@contextlib.contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        
@contextlib.contextmanager
def swallow_io():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = new_out, new_err
    sys.stdin = io.StringIO()
    try:
        yield sys.stdin, new_out, new_err
    finally:
        sys.stdout, sys.stderr = old_out, old_err
        sys.stdin = sys.__stdin__
        
@contextlib.contextmanager
def create_tempdir():
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        try:
            yield
        finally:
            os.chdir(original_dir)


def estimate_pass_at_k(
    num_samples: Union[int, List[int], np.ndarray],
    num_correct: Union[List[int], np.ndarray],
    k: int
) -> np.ndarray:
    def estimator(n: int, c: int, k: int) -> float:
        if n - c < k:
            return 1.0
        return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

    if isinstance(num_samples, int):
        num_samples_it = itertools.repeat(num_samples, len(num_correct))
    else:
        assert len(num_samples) == len(num_correct)
        num_samples_it = iter(num_samples)

    return np.array([estimator(int(n), int(c), k) for n, c in zip(num_samples_it, num_correct)])

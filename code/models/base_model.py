from abc import ABC, abstractmethod
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import *
import re
import concurrent.futures
import time
from tqdm import tqdm
import threading


class BaseModel(ABC):
    """
    Abstract base class for different models' implementations.
    """

    def __init__(self, mode=None):
        # mode in ["multi-modal", "text-only"]
        self.mode = mode
    
    def generate_prompt(self, example): 
        """
        It is also encouraged to construct your own prompt for better performance.
        """
        return example["prompt"]
        
    

    @abstractmethod
    def generate_single(self, example):
        """
        Generate a single response using the appropriate method based on whether figures are provided.
        """
        pass

    def generate_batch(self, example_lst, save_callback, max_workers=20):
        """
        Support inference in batch
        """
        results = [None] * len(example_lst)
        # Use ThreadPoolExecutor to execute tasks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {}
            for index, example in enumerate(example_lst):
                future = executor.submit(self.generate_single, example)
                future_to_index[future] = index
            for future in tqdm(concurrent.futures.as_completed(future_to_index),
                           total=len(example_lst),
                           desc="Generating Responses",
                           unit="response"):
                index = future_to_index[future]
                try:
                    result = future.result()
                    save_callback(index, result, False)
                except Exception as exc:
                    print(f"Generated exception for {example_lst[index]}: {exc}")

    
    def generate_batch_N(self, example_lst, N, save_callback, max_workers=20):
        """
        Specifically for CS inference:
        Support inference in batch where each input message is processed to generate multiple outputs.
        This function generates N responses for each input and saves them once all are ready.
        If any response in a batch is None due to an error, the whole batch for that input will be saved as None.
        """
        index_to_futures = {}
        index_to_results = {}
        lock = threading.Lock()

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            for index, example in enumerate(example_lst):
                future_list = [executor.submit(self.generate_single, example) for _ in range(N)]
                index_to_futures[index] = future_list
                index_to_results[index] = []  # initialize results list for each input index

            # Monitoring all futures until they complete
            futures = [f for sublist in index_to_futures.values() for f in sublist]
            for future in tqdm(concurrent.futures.as_completed(futures),
                            total=N*len(example_lst),
                            desc="Generating Responses",
                            unit="response"):
                found_index = None
                for idx, futures in index_to_futures.items():
                    if future in futures:
                        found_index = idx
                        break
                
                if found_index is None:
                    continue
                
                results_list = index_to_results[found_index]
                with lock:
                    if results_list is None:
                        continue  # Skip processing if results are already set to None due to an error

                    try:
                        result = future.result()
                        results_list.append(result)
                        if None in results_list:
                            results_list = None  # Invalidate the entire batch if any result is None
                    except Exception as exc:
                        print(f"Generated exception for {example_lst[found_index]}: {exc}")
                        results_list = None  # Invalidate the entire batch on exception

                    if (results_list is None or len(results_list) == N):
                        save_callback(found_index, results_list, True)
                        
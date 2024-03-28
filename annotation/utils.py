import streamlit as st
import json
import os
import base64
from pathlib import Path
import tempfile
import re

def choose_subject_and_competition(d):
    subjects = d.keys()
    subject = st.selectbox('选择学科', options=subjects, index=0)
    competitions = d[subject]
    competition = st.selectbox('选择竞赛', options=competitions, index=0)
    return subject, competition
    
def list_files_in_directory(directory):
    """列出目录中所有文件的名称，不包括文件后缀，且每个文件名称只显示一次"""
    all_files = os.listdir(directory)
    # 移除文件扩展名并去重
    file_names = set(os.path.splitext(file)[0] for file in all_files if file.endswith(('.md', '.pdf')))
    return sorted(list(file_names))  # 返回排序后的文件名列表

def load_annotation(folder_path):
    if os.path.exists(folder_path):
        # with open(file_path, "r", encoding="utf-8") as file:
        #     data = json.load(file)
        # return data
        annotated_list = []
        for file in os.listdir(folder_path):
            if file == ".DS_Store":
                continue
            file_path = os.path.join(folder_path, file)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                annotated_list.append((file[:-5], data))
        annotated_list = sorted(annotated_list)
        return annotated_list
            
    return None


@st.cache_data
def get_pdf_display_content(file_path):
    # Convert the PDF file to a base64 string but don't display it
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    return base64_pdf

def display_pdf(base64_pdf):
    pdf_display = f"""
    <div style="position: relative; width: 100%; height: 0; padding-bottom: 100%;">
        <iframe src="data:application/pdf;base64,{base64_pdf}" 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
                type="application/pdf">
        </iframe>
    </div>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)


def delete_option(index, list_key):
    """从指定的会话状态列表中删除一个元素"""
    if list_key in st.session_state:
        del st.session_state[list_key][index]

def reset_session_state():
    if st.session_state.get('reset_needed', False):
        st.session_state["input_reset_counter"] = st.session_state.get('input_reset_counter', 0) + 1
        st.session_state['options_list'] = []
        st.session_state['figure_urls'] = []
        st.session_state['reset_needed'] = False
        st.session_state['multi_parts'] = [] # 一题多问
        st.session_state['multi_solutions'] = [] # 一题多解
        st.session_state['set_answers'] = []

def check_annotation(annotation):
    required_fields = ['answer_type', 'problem', 'answer', 'figure_exists']
    for field in required_fields:
        if field not in annotation or (annotation[field] is None or annotation[field] == ''):
            return f"错误: 缺少必填字段 '{field}'"
    if 'need_context' in annotation and annotation['need_context'] == '是':
        if 'context' not in annotation or not annotation['context']:
            return "错误: 缺少必要的上下文信息"
    if annotation['answer_type'] in ['1', '2']:
        if 'options' not in annotation or not annotation['options']:
            return "错误: 缺少选项信息"
    if not isinstance(annotation['figure_exists'], bool):
        return "错误: 'figure_exists' 字段应该为布尔类型"
    if annotation['figure_exists']:
        if 'figure_urls' not in annotation or not annotation['figure_urls']:
            return "错误: 缺少图像URL"
    return

# def save_to_file(annotation, folder_path, index):
#     if not os.path.exists(folder_path):
#         os.makedirs(folder_path)
#     file_path = os.path.join(folder_path, str(index)+'.json')
#     with open(file_path, 'w', encoding="utf-8") as f:
#         json.dump(annotation, f, indent=4, ensure_ascii=False)
        
def save_to_file(data, output_folder, file_timestamp):
    # Ensure the folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Construct the file path with the provided timestamp
    file_path = os.path.join(output_folder, f"{file_timestamp}.json")  # 使用提供的时间戳作为文件名
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def delete_file(output_folder, file_timestamp):
    file_path = os.path.join(output_folder, f"{file_timestamp}.json")  # 使用提供的时间戳作为文件名
    if os.path.exists(file_path):
        os.remove(file_path)
        
        
def find_figure_urls(text): # pure urls
    url_pattern = r'https://cdn.mathpix.com/cropped/[^\s\)]+?\.jpg[^\s\)]*|https://i.postimg.cc/[^\s\)]+?/image\.png'
    urls = re.findall(url_pattern, text)
    url_dict = {f'figure{i+1}': url for i, url in enumerate(urls)}
    return url_dict


def normalize_display_figure(text):
    md_url_pattern = r"!\[.*?\]\((https://cdn.mathpix.com/cropped/[^\s\)]+?\.jpg[^\s\)]*|https://i.postimg.cc/[^\s\)]+?/image\.png)\)"
    def replace_with_img_tag(match):
        img_url = match.group(1)
        return f'<img src="{img_url}" width="200" style="height: auto;">'
    normalized_text = re.sub(md_url_pattern, replace_with_img_tag, text)
    return normalized_text
    

def replace_url_with_not(text, lst):
    url_2_index = {}
    for i, entry in enumerate(lst):
        url_2_index[entry['url']] = i+1
    for url in url_2_index.keys():
        text = text.replace(url, "**[figure"+str(url_2_index[url])+"]**")
    return text

def identify_choices(text):
    patterns = [
        r"([A-Za-z])[\.\s]+\s*(.+?)(?=(\n[A-Za-z][\.\s]+\s|$\n?))",
        r"(\d+)[\.\s]+\s*(.+?)(?=(\n\d+[\.\s]+\s|$\n?))"
    ]
    for pattern in patterns:
        lst = []
        matches = re.finditer(pattern, text, re.DOTALL)
        for match in matches:
            if match:
                choice_description = ' '.join(match.group(2).split())
                if choice_description not in lst:
                    lst.append(choice_description)
        if len(lst) > 1:
            return lst
        
    return None
    
    
if __name__ == "__main__":
    # print(find_figure_urls("https://cdn.mathpix.com/cropped/2024_03_14_b9e515217a571029676eg-09.jpg?height=1168&width=726&top_left_y=1432&top_left_x=151)"))
    
    text = """1. The surface salinity at low latitudes can 

be explained by high evaporation rates

2. The surface salinity at mid latitudes can be explained by high precipitation rates

3. For mid latitudes, the Eastern region receives more abundant rainfall than the Western region

4. For mid latitudes, the Western region receives more abundant rainfall than the Eastern region"""
    print(identify_choices(text))

import streamlit as st
from utils import *
import argparse
import os
from datetime import datetime

answer_type_options_ = {
    'NV': '数值题',
    'SET': '集合',
    'IN': '区间',
    'EX': '表达式',
    'EQ': '方程',
    'TUP': '元组'
}

answer_type_options = {
    'SC': '单选题',
    'MC': '多选题',
    'TF': '判断题',
    'NV': '数值题',
    'SET': '集合',
    'IN': '区间',
    'EX': '表达式',
    'EQ': '方程',
    'TUP': '元组', # e.g. find all pairs of (x, y) that ...
    'MPV': '一题多个待求量',
    'MA': '一题多个答案',
    'OT': '其他（需要人类评估）'
}


def init_page():
    st.set_page_config(layout="wide")
    col1, col2 = st.columns([10, 3.5])
    return col1, col2

def show_document(args, column, d):
    with column:
        col1, col2, col3 = st.columns(3)
        with col1:
            subjects = list(d.keys())
            subject = st.selectbox('选择学科', options=subjects, index=0)
        with col2:
            competitions = d[subject]
            competition = st.selectbox('选择竞赛', options=competitions, index=0)
        args.subject, args.competition = subject, competition
        folder_path = os.path.join(args.data_dir, subject, competition)
        assert os.path.exists(folder_path)
        with col3:
            file_names = list_files_in_directory(folder_path)
            selected_file = st.selectbox('选择文件', options=file_names, index=0)
            args.file_name = selected_file
        if selected_file:
            col_left, col_right = st.columns([3, 2])
            with col_left:
                st.header(selected_file+'.pdf')
                pdf_file_path = os.path.join(folder_path, f"{selected_file}.pdf")
                base64_pdf_content = get_pdf_display_content(pdf_file_path)
                display_pdf(base64_pdf_content)
            with col_right:
                md_file_path = os.path.join(folder_path, f"{selected_file}.md")
                if os.path.exists(md_file_path):
                    st.header(selected_file+'.md')
                    with open(md_file_path, "r", encoding='utf-8') as file:
                        markdown_content = file.read()
                        st.text_area('hide', markdown_content, height=800, label_visibility="collapsed")
                else:
                    st.header('No markdown file provided!')
        
        enhanced_file_names = ['不启用'] + file_names  # Add "不启用" option
        selected_file_enhanced = st.selectbox('选择文件(可选)', options=enhanced_file_names, index=0)
        
        if selected_file_enhanced != '不启用':
            enhanced_col_left, enhanced_col_right = st.columns([3, 2])  # Create new variables for clarity
            with enhanced_col_left:
                st.header(selected_file_enhanced + '.pdf')
                pdf_file_path = os.path.join(folder_path, f"{selected_file_enhanced}.pdf")
                if os.path.exists(pdf_file_path):
                    base64_pdf_content = get_pdf_display_content(pdf_file_path)
                    display_pdf(base64_pdf_content)
            with enhanced_col_right:
                st.header(selected_file_enhanced + '.md')
                md_file_path = os.path.join(folder_path, f"{selected_file_enhanced}.md")
                if os.path.exists(md_file_path):
                    with open(md_file_path, "r", encoding='utf-8') as file:
                        markdown_content = file.read()
                        st.text_area('hide', markdown_content, height=800, label_visibility="collapsed")
                else:
                    st.header('No markdown file provided!')
        
def load(args):
    if 'question_number' not in st.session_state:
        st.session_state.question_number = 0
        
    if os.path.exists(args.output_folder):
        files = [f for f in os.listdir(args.output_folder) if os.path.isfile(os.path.join(args.output_folder, f))]
        if files:
            question_number = len(files)
            st.session_state.question_number = question_number

def show_annotate(args, column):
    with column:
        a, b = st.columns(2)
        with a:
            st.subheader('标注信息')
        with b:
            st.subheader('num: ' + str(st.session_state.question_number))
        st.markdown('**所有图片用[figure编号]形式标注，如[figure1]**')
        col_subject, col_competition, col_file_name = st.columns(3)
        with col_subject:
            st.text_input('学科', value=args.subject, disabled=True)
        with col_competition:
            st.text_input('竞赛名称', value=args.competition, disabled=True)
        with col_file_name:
            st.text_input('文件名称', value=args.file_name, disabled=True)
        
def annotate_problem_and_context(args):
    need_context = st.radio('是否需要添加上下文 [context?]', ('否', '是'), key=f"need_context_{st.session_state.get('input_reset_counter', 0)}")
    args.need_context = need_context
    if need_context == '是':
        context = st.text_area('上下文 [context*]', '', key=f"context_{st.session_state.get('input_reset_counter', 0)}")
        args.context = context
        st.markdown('上下文预览:')
        st.markdown(context, unsafe_allow_html=True)
    problem = st.text_area('题干 [problem*]', '', key=f"problem_{st.session_state.get('input_reset_counter', 0)}")
    args.problem = problem
    st.markdown('题干预览:')
    st.markdown(problem, unsafe_allow_html=True)
    
def annotate_solution(args):
    have_solution = st.radio('是否有解析', ('否', '是'), key=f"have_solution_{st.session_state.get('input_reset_counter', 0)}")
    args.have_solution = have_solution
    if have_solution == "是":
        solution = st.text_area('解析 [solution]', '', key=f"solution_{st.session_state.get('input_reset_counter', 0)}")
        args.solution = solution
        st.markdown('解析预览:')
        st.markdown(solution, unsafe_allow_html=True)

def annotate_type_single_choice(args): # 单选题
    if 'options_list' not in st.session_state:
        st.session_state.options_list = []
    
    new_option = st.text_input('添加新选项', value='', key=f"new_option_{st.session_state.get('input_reset_counter', 0)}")
    if st.button('添加选项'):
        if new_option:
            st.session_state.options_list.append(new_option)

    if 'options_list' in st.session_state:
        for i, option in enumerate(st.session_state.options_list):
            col1, col2 = st.columns([10, 3])
            option_markdown = f'选项 {chr(65+i)}: {option}'
            col1.markdown(option_markdown, unsafe_allow_html=True)
            delete_button = col2.button('删除', key=f'delete_{i}')
            if delete_button:
                delete_option(i, 'options_list')
                st.experimental_rerun()

    if st.session_state.options_list:
        option_labels = [chr(65+i) for i in range(len(st.session_state.options_list))]  # A, B, C, D...
        answer_label = st.selectbox('答案 [answer*]', options=option_labels, key=f"answer_label_{st.session_state.get('input_reset_counter', 0)}") # 字母
        answer = st.session_state.options_list[ord(answer_label) - 65] # 索引，从0开始
        args.answer_label = answer_label
        st.write(f"选中的答案内容: {answer}")
    else:
        st.write("请添加至少一个选项")

def annotate_type_multi_choice(args): # 多选题
    if 'options_list' not in st.session_state:
        st.session_state.options_list = []
    new_option = st.text_input('添加新选项', value='', key=f"new_option_{st.session_state.get('input_reset_counter', 0)}")
    if st.button('添加选项'):
        if new_option:
            st.session_state.options_list.append(new_option)

    if 'options_list' in st.session_state:
        for i, option in enumerate(st.session_state.options_list):
            col1, col2 = st.columns([10, 3])
            option_markdown = f'选项 {chr(65+i)}: {option}'
            col1.markdown(option_markdown, unsafe_allow_html=True)
            delete_button = col2.button('删除', key=f'delete_{i}')
            if delete_button:
                delete_option(i, 'options_list')
                st.experimental_rerun()

    if st.session_state.options_list:
        option_labels = [chr(65+i) for i in range(len(st.session_state.options_list))]  # A, B, C, D...
        selected_answer_labels = st.multiselect('答案 [answer*]', options=option_labels, key=f"answer_label_{st.session_state.get('input_reset_counter', 0)}")  # Use multiselect instead of selectbox
        selected_answers = [st.session_state.options_list[ord(label) - 65] for label in selected_answer_labels]  # Get selected answers based on labels
        args.answer_label = selected_answer_labels # 字符串列表
        if selected_answers:
            st.write(f"选中的答案内容: {', '.join(selected_answers)}")
        else:
            st.write("请至少选择一个选项作为答案")
    else:
        st.write("请添加至少一个选项")

def annotate_type_judge(args): # 判断题
    judgment_answer = st.radio(
        "判断题答案 [answer*]", 
        ['True', 'False'], 
        index=0,
        key=f"judgment_answer_{st.session_state.get('input_reset_counter', 0)}"
    )

    args.answer_label = judgment_answer  # This will be either 'True' or 'False'
    st.write(f"选中的答案内容: {judgment_answer}")

def annotate_type_single_blank(args):
    numeric_answer = st.text_input(
        "答案 [answer*] (支持TeX，例如: `$\\log_{2}9$`)", 
        '',
        key=f"numeric_answer_{st.session_state.get('input_reset_counter', 0)}"
    )
    st.write(f"答案预览: {numeric_answer}")
    args.answer_label = numeric_answer # 字符串
    
    unit = st.text_input(
        "单位 [unit*] 若没有单位，此项空着",
        '',
        key=f"unit_{st.session_state.get('input_reset_counter', 0)}"
    )
    if unit.strip():
        args.unit = unit
    else:
        args.unit = None

def annotate_type_multi_problem(args): # 一题多问
    if 'multi_parts' not in st.session_state:
        st.session_state.multi_parts = []

    part_question = st.text_input("名称(例如：the value of $x$)", '', key=f"part_question_{st.session_state.get('input_reset_counter', 0)}")
    part_type = st.selectbox("类型", list(answer_type_options_.keys()), key=f"part_type_{st.session_state.get('input_reset_counter', 0)}", format_func=lambda x: f'{x}: {answer_type_options_[x]}')
    part_answer = st.text_input("答案 (支持TeX，例如: `$\\log_{2}9$`)", '', key=f"part_answer_{st.session_state.get('input_reset_counter', 0)}")
    part_unit = st.text_input("单位 (若没有单位，留空)", '', key=f"part_unit_{st.session_state.get('input_reset_counter', 0)}")
    
    if st.button('添加待求量', key=f"add_new_part_{st.session_state.get('input_reset_counter', 0)}"):
        if part_question and part_answer:  # Ensure there is a question part and an answer before adding
            st.session_state.multi_parts.append({
                'question': part_question,
                'type': part_type,
                'answer': part_answer,
                'unit': part_unit if part_unit.strip() else None
            })
    for i, part in enumerate(st.session_state.multi_parts):
        col_part, col_delete = st.columns([9, 1])
        col_part.markdown(f"待求量{i+1}: 名称: {part['question']}, 答案: {part['answer']}, 单位: {part['unit']}")
        delete_button = col_delete.button("删除", key=f"delete_part_{i}_{st.session_state.get('input_reset_counter', 0)}")
        if delete_button:
            delete_option(i, 'multi_parts')
            st.experimental_rerun()
    
    answer_sequence = []
    part_types = []
    answer_label = []
    unit = []
    for item in st.session_state.multi_parts:
        answer_sequence.append(item['question'])
        part_types.append(item['type'])
        answer_label.append(item['answer'])
        unit.append(item['unit'])
    args.answer_sequence, args.type, args.answer_label, args.unit = answer_sequence, part_types, answer_label, unit
        
def annotate_type_multi_answer(args): # 一题多解
    if 'multi_solutions' not in st.session_state:
        st.session_state.multi_solutions = []
        
    solution_answer = st.text_input("答案 (支持TeX，例如: `$\\sqrt{2}$`)", '', key=f"solution_answer_{st.session_state.get('input_reset_counter', 0)}")
    solution_type = st.selectbox("类型", list(answer_type_options_.keys()), key=f"solution_type_{st.session_state.get('input_reset_counter', 0)}", format_func=lambda x: f'{x}: {answer_type_options_[x]}')
    solution_unit = st.text_input("单位 (若没有单位，留空)", '', key=f"solution_unit_{st.session_state.get('input_reset_counter', 0)}")

    if st.button('添加答案'):
        if solution_answer:
            st.session_state.multi_solutions.append({
                'answer': solution_answer,
                'type': solution_type,
                'unit': solution_unit if solution_unit.strip() else None
            })
                    
    for i, solution in enumerate(st.session_state.multi_solutions):
        col_solution, col_delete = st.columns([9, 1])
        unit_text = f", 单位: {solution['unit']}" if solution['unit'] else ""
        col_solution.markdown(f"解答{i+1}: 答案: {solution['answer']}{unit_text}")
        delete_button = col_delete.button("删除", key=f"delete_solution_{i}_{st.session_state.get('input_reset_counter', 0)}")
        if delete_button:
            delete_option(i, 'multi_solutions')
            st.experimental_rerun()
    
    answer_label = []
    solution_type_lst = []
    unit = []
    for item in st.session_state.multi_solutions:
        answer_label.append(item['answer'])
        solution_type_lst.append(item['type'])
        unit.append(item['unit'])
    args.answer_label, args.type, args.unit = answer_label, solution_type_lst, unit
    
def annotate_type_set(args):  # 集合
    if 'set_answers' not in st.session_state:
        st.session_state.set_answers = []
    new_element = st.text_input(
        "添加新元素到集合 (支持TeX，例如: `$\\sqrt{2}$`, `$\\frac{1}{2}$`)",
        '',
        key=f"new_element_{st.session_state.get('input_reset_counter', 0)}"
    )
    if st.button('添加元素', key=f"add_element_{st.session_state.get('input_reset_counter', 0)}"):
        if new_element:
            st.session_state.set_answers.append(new_element)
    for i, element in enumerate(st.session_state.set_answers):
        col_element, col_delete = st.columns([9, 1])
        with col_element:
            st.markdown(f"元素{i+1}: {element}")
        with col_delete:
            if st.button("删除", key=f"delete_element_{i}_{st.session_state.get('input_reset_counter', 0)}"):
                st.session_state.set_answers.pop(i)
                st.experimental_rerun()

    args.answer_label = st.session_state.set_answers

    unit = st.text_input(
        "单位 [unit*] 若没有单位，此项空着",
        '',
        key=f"unit_{st.session_state.get('input_reset_counter', 0)}"
    )
    if unit.strip():
        args.unit = unit
    else:
        args.unit = None

def annotate_type_human_eval(args):
    numeric_answer = st.text_input(
        "答案 [answer*] (支持TeX，例如: `$\\log_{2}9$`)", 
        '',
        key=f"numeric_answer_{st.session_state.get('input_reset_counter', 0)}"
    )
    st.write(f"答案预览: {numeric_answer}")
    args.answer_label = numeric_answer # 字符串

    scenario = st.text_input(
        "问题场景描述（如：化学方程式书写；理由阐述题）",
        '',
        key=f"scenario_{st.session_state.get('input_reset_counter', 0)}"
    )
    args.scenario = scenario

def annotate_figures(args):
    figure_exists = st.radio('是否有图片[figure?*]', ('否', '是'), key=f"figure_exists_{st.session_state.get('input_reset_counter', 0)}")
    args.figure_exists = figure_exists
    if figure_exists == '是':
        figure_dependent = st.radio('该题目是否依赖图片[figure_dependent?]', ('依赖', '不依赖'), index=('依赖', '不依赖').index(st.session_state.get('figure_dependent', '依赖')))
        args.figure_dependent = figure_dependent
        figure_type_options = {
            '1': '几何图形（数学相关，平面、几何等）',
            '2': '任何图表（表格、柱状图、折线图等表示统计数据信息的）',
            '3': '自然风光（地理风景、星空）',
            '4': '科学相关（如物理示意图、化学有机物、生物细胞 基因、地理地图、工程机械等）',
            '5': '抽象物体（抽象物体和概念，可能包括符号、算法图、流程图等）',
            '6': '其他',
        }
        if 'figure_urls' not in st.session_state:
            st.session_state.figure_urls = []

        new_url = st.text_input('添加新图片链接', value='', key=f"new_url_{st.session_state.get('input_reset_counter', 0)}")
        if st.button('添加图片链接'):
            if new_url:
                st.session_state.figure_urls.append({'url': new_url, 'type': None})  # 添加字典而不是单纯的URL
        
        if 'figure_urls' in st.session_state:
            for i, entry in enumerate(st.session_state.figure_urls):
                col1, col2, col3, col4 = st.columns([3, 5.5, 3.5, 1])  # 分配空间给图片预览，图片类型选择，URL文本，和删除按钮
                url = entry['url']
                if url:
                    try:
                        col1.image(url, caption=f'Figure {i+1}', use_column_width=True)  # 使用URL显示图片
                    except Exception as e:
                        col1.write(f"Image at {url} cannot be displayed.")

                selected_type = col2.selectbox(f"图片类型 for Figure {i+1}", options=list(figure_type_options.keys()), format_func=lambda x: f"{x}: {figure_type_options[x]}", index=0, key=f'figure_type_{i}')
                st.session_state.figure_urls[i]['type'] = selected_type  # 更新图片类型

                col3.write(f'URL: {url[:20]}...')

                delete_button = col4.button('删除', key=f'delete_url_{i}')
                if delete_button:
                    delete_option(i, 'figure_urls')
                    st.experimental_rerun()

def save_annotation(args):
    if st.session_state.get('options_list', []):
        options_list = st.session_state.get('options_list', [])
        option_dict_with_choice = {}
        for i in range(len(options_list)):
            choice = chr(65+i)
            option_dict_with_choice[choice] = options_list[i]
    else:
        option_dict_with_choice = None
        
    id_url = {}
    if args.figure_exists == "是":
        figure_urls = st.session_state.get('figure_urls', [])
        assert figure_urls
        for i in range(1, len(figure_urls)+1):
            id_url[i] = {'url': figure_urls[i-1]['url'], 'type': figure_urls[i-1]['type']}

    annotations = {
        'answer_type': args.answer_type, # 必填
        'context': args.context if args.need_context == "是" else None,
        'problem': args.problem, # 必填
        'options': option_dict_with_choice if option_dict_with_choice and args.answer_type in ['SC', 'MC'] else None,
        'answer': args.answer_label, # 必填
        'unit': args.unit if args.answer_type not in ['SC', 'MC', 'TF', 'OT', 'TUP'] else None,
        'answer_sequence': args.answer_sequence if args.answer_type == 'MPV' else None,
        'type_sequence': args.type if args.answer_type in ['MPV', 'MA'] else None,
        'solution': args.solution if args.have_solution == '是' and args.solution != '' else None,
        'figure_exists': True if args.figure_exists == "是" else False, # 必填
        'figure_dependent': None if args.figure_exists != "是" else (args.figure_dependent == "依赖"),
        'figure_urls': id_url if args.figure_exists == "是" else None,
        'scenario': args.scenario if args.answer_type == 'OT' else None,
        
        'subject': args.subject,
        'competition': args.competition,
        'file_name': args.file_name
        
        }

    flag = check_annotation(annotations)
    if flag:
        return False, flag
    else:
        return True, annotations
    
def save_problem(args):
    if st.button('保存本题'):
        valid, message = save_annotation(args)
        if valid:
            if 'new_file_flag' not in st.session_state:
                st.session_state.new_file_flag = True
            if 'current_time' not in st.session_state:
                st.session_state.current_time = datetime.now().strftime("%m_%d_%H_%M_%S")
                
            if st.session_state.new_file_flag:
                st.session_state.current_time = datetime.now().strftime("%m_%d_%H_%M_%S")
                save_to_file(message, args.output_folder, st.session_state.current_time)
                st.session_state.new_file_flag = False
            else:
                save_to_file(message, args.output_folder, st.session_state.current_time)
        # if valid:
        #     save_to_file(message, args.output_folder, st.session_state.question_number)

def next_problem(args):
    if st.button('保存&下一题'):
        valid, message = save_annotation(args)
        if valid:
            if 'new_file_flag' not in st.session_state:
                st.session_state.new_file_flag = True
            if st.session_state.new_file_flag:
                st.session_state.current_time = datetime.now().strftime("%m_%d_%H_%M_%S")

            save_to_file(message, args.output_folder, st.session_state.current_time)
            st.session_state.new_file_flag = True
            st.session_state.question_number += 1
            st.session_state['reset_needed'] = True
            reset_session_state()
            st.experimental_rerun()
        else:
            print(message)


def next_problem_without_clean(args):
    if st.button('保存&下一题(不清空)'):
        valid, message = save_annotation(args)
        if valid:
            if 'new_file_flag' not in st.session_state:
                st.session_state.new_file_flag = True
            if st.session_state.new_file_flag:
                st.session_state.current_time = datetime.now().strftime("%m_%d_%H_%M_%S")

            save_to_file(message, args.output_folder, st.session_state.current_time)
            st.session_state.new_file_flag = True
            st.session_state.question_number += 1
            st.experimental_rerun()
        else:
            print(message)


def annotate(args, column):
    with column:
        answer_type = st.selectbox('答案类型 [answer_type*]', options=list(answer_type_options.keys()), format_func=lambda x: f'{x}: {answer_type_options[x]}', index=0)
        args.answer_type = answer_type
        annotate_problem_and_context(args)
        
        if answer_type == 'SC': # 单选
            annotate_type_single_choice(args)
        elif answer_type == 'MC': # 多选
            annotate_type_multi_choice(args)
        elif answer_type == 'TF': # 判断
            annotate_type_judge(args)
        elif answer_type in ['NV', 'IN', 'EX', 'EQ', 'TUP']: # 数值 区间 表达式 方程(open questions)
            annotate_type_single_blank(args)
        elif answer_type == 'MPV': # 一题多问
            annotate_type_multi_problem(args)
        elif answer_type == 'MA': # 一题多解
            annotate_type_multi_answer(args)
        elif answer_type == 'SET': # 集合
            annotate_type_set(args)
        else:
            annotate_type_human_eval(args)
        
        annotate_solution(args)
        annotate_figures(args)
        col_current, col_next, col_next_without_clean = st.columns(3)
        with col_current:
            save_problem(args)
        with col_next:
            next_problem(args)
        with col_next_without_clean:
            next_problem_without_clean(args)
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="./data/", help="待标注的文档位置")
    parser.add_argument("--output_dir", type=str, default="./output/")
    args = parser.parse_args()
    
    subject_competition_dict = {}
    for subject in os.listdir(args.data_dir):
        if subject not in subject_competition_dict:
            subject_competition_dict[subject] = []
        for competition in os.listdir(os.path.join(args.data_dir, subject)):
            subject_competition_dict[subject].append(competition)
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    col1, col2 = init_page()
    show_document(args, col1, subject_competition_dict)
    args.output_folder = os.path.join(args.output_dir, args.subject, args.competition, args.file_name)
    load(args) # get current question_number

    show_annotate(args, col2)
    annotate(args, col2)

import streamlit as st
from utils import *
import argparse
import os
from datetime import datetime
from answer_type import *


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
    'NV': '数值题    (例：1900, $\log_{2}9$)',
    'SET': '集合    (例：{1, 2, 3})',
    'IN': '区间    (例： (1, 3])',
    'EX': '表达式    (例： $4 x^{2}-8 x+2$)',
    'EQ': '方程    (例： $y-x=\\frac{1}{2}$)',
    'TUP': '元组    (例： (3, 4))', # e.g. find all pairs of (x, y) that ...
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
            
        args.output_folder = os.path.join(args.output_dir, args.subject, args.competition, args.file_name)
        load(args) # get current question_number
    
        # modify
        args.annotated_list = load_annotation(args.output_folder)
        if args.annotated_list:
            show_sidebar(args)    
        
            
        if 'display_pdf' not in st.session_state:
            st.session_state['display_pdf'] = True
        display_pdf_option = st.checkbox('开启PDF预览', value=st.session_state['display_pdf'])
            
        if selected_file:
            if not os.path.exists(os.path.join(folder_path, f"{selected_file}.md")):
                st.header(selected_file+'.pdf')
                pdf_file_path = os.path.join(folder_path, f"{selected_file}.pdf")
                base64_pdf_content = get_pdf_display_content(pdf_file_path)
                display_pdf(base64_pdf_content)
            else:
                if display_pdf_option:
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
                                st.text_area('hide', markdown_content, height=800, label_visibility="collapsed", key="md1")
                        else:
                            st.header('No markdown file provided!')
                else: # no pdf
                    md_file_path = os.path.join(folder_path, f"{selected_file}.md")
                    if os.path.exists(md_file_path):
                        st.header(selected_file+'.md')
                        with open(md_file_path, "r", encoding='utf-8') as file:
                            markdown_content = file.read()
                            st.text_area('hide', markdown_content, height=800, label_visibility="collapsed", key="md2")
                    else:
                        st.header('No markdown file provided!')
        
        enhanced_file_names = ['不启用'] + file_names  # Add "不启用" option
        selected_file_enhanced = st.selectbox('选择文件(可选)', options=enhanced_file_names, index=0)
        
        if selected_file_enhanced != '不启用':
            if not os.path.exists(os.path.join(folder_path, f"{selected_file_enhanced}.md")):
                st.header(selected_file_enhanced + '.pdf')
                pdf_file_path = os.path.join(folder_path, f"{selected_file_enhanced}.pdf")
                if os.path.exists(pdf_file_path):
                    base64_pdf_content = get_pdf_display_content(pdf_file_path)
                    display_pdf(base64_pdf_content)
            else:
                if display_pdf_option:
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
                                st.text_area('hide', markdown_content, height=800, label_visibility="collapsed", key="md3")
                        else:
                            st.header('No markdown file provided!')
                else:
                    st.header(selected_file_enhanced + '.md')
                    md_file_path = os.path.join(folder_path, f"{selected_file_enhanced}.md")
                    if os.path.exists(md_file_path):
                        with open(md_file_path, "r", encoding='utf-8') as file:
                            markdown_content = file.read()
                            st.text_area('hide', markdown_content, height=800, label_visibility="collapsed", key="md4")
                    else:
                        st.header('No markdown file provided!')
                        
                        
        
def load(args):
    if 'question_number' not in st.session_state:
        st.session_state.question_number = 0
    
    if os.path.exists(args.output_folder):
        files = [f for f in os.listdir(args.output_folder) if f.endswith(".json") and os.path.isfile(os.path.join(args.output_folder, f))]
        if files:
            question_number = len(files)
            st.session_state.question_number = question_number
        else:
            st.session_state.question_number = 0
    else:
        st.session_state.question_number = 0

def show_annotate(args, column):
    with column:
        a, b = st.columns(2)
        with a:
            st.subheader('标注信息')
        with b:
            st.subheader('num: ' + str(st.session_state.question_number))
        col_subject, col_competition, col_file_name = st.columns(3)
        with col_subject:
            st.text_input('学科', value=args.subject, disabled=True)
        with col_competition:
            st.text_input('竞赛名称', value=args.competition, disabled=True)
        with col_file_name:
            st.text_input('文件名称', value=args.file_name, disabled=True)


def annotate_problem_context(args):
    if st.session_state.get('modify_mode', False):
        p_index = 1 if hasattr(args, 'context') and args.context else 0
    else:
        p_index = 0
    need_context = st.radio('是否需要添加上下文', ('否', '是'), key=f"need_context_{st.session_state.get('input_reset_counter', 0)}", index=p_index)
    args.need_context = need_context
    if need_context == '是':
        context = st.text_area('上下文', value=args.context if st.session_state.get('modify_mode', False) else '', key=f"context_{st.session_state.get('input_reset_counter', 0)}")
        args.context = context
        st.markdown('上下文预览:')
        st.markdown(context, unsafe_allow_html=True)
    else:
        args.context = None
    problem = st.text_area('**题干**', value=args.problem if st.session_state.get('modify_mode', False) else '', key=f"problem_{st.session_state.get('input_reset_counter', 0)}", height=175)
    args.problem = problem
    st.markdown('题干预览:')
    st.markdown(problem, unsafe_allow_html=True)
    # annotate_figures_auto(args)
    # st.markdown(replace_url_with_not(problem, st.session_state.figure_urls) if args.figure_exists else problem, unsafe_allow_html=True)
    
    if st.session_state.get('modify_mode', False):
        p_index = list(answer_type_options.keys()).index(args.answer_type)
    else:
        p_index = 0
    answer_type = st.selectbox('**答案类型**', options=list(answer_type_options.keys()), format_func=lambda x: f'{x}: {answer_type_options[x]}', index=p_index)
    args.answer_type = answer_type
    

def annotate_solution(args):
    if st.session_state.get('modify_mode', False):
        p_index = 1 if args.solution else 0
    else:
        p_index = 0
    have_solution = st.radio('是否有解析', ('否', '是'), index=p_index, key=f"have_solution_{st.session_state.get('input_reset_counter', 0)}")
    args.have_solution = have_solution
    if have_solution == "是":
        solution = st.text_area('解析', value=args.solution if st.session_state.get('modify_mode', False) else '', key=f"solution_{st.session_state.get('input_reset_counter', 0)}")
        args.solution = solution
        st.markdown('解析预览:')
        st.markdown(solution, unsafe_allow_html=True)
        # annotate_figures_auto(args)
        # st.markdown(replace_url_with_not(solution, st.session_state.figure_urls) if args.figure_exists else solution, unsafe_allow_html=True)
    else:
        args.solution = None

def annotate_figures(args):
    st.write("**注：图片的标注涵盖题干、选择题选项、解析，编号在一道题内连续**")
    p_index = 1 if st.session_state.get('modify_mode', False) and args.figure_exists else 0
    figure_exists = st.radio('**是否有图片(题干、选项、解析)**', ('否', '是'), key=f"figure_exists_{st.session_state.get('input_reset_counter', 0)}", index = p_index)
    args.figure_exists = figure_exists
    if figure_exists == '是':
        if st.session_state.get('modify_mode', False):
            if args.figure_dependent or args.figure_dependent == None:
                p_index = 0
            else:
                p_index = 1
        else:
            p_index = 0
        figure_dependent = st.radio('该题目是否依赖图片', ('依赖', '不依赖'), key=f"figure_dependent_{st.session_state.get('input_reset_counter', 0)}", index=p_index)
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
            
        if st.session_state.get('modify_mode', False) and st.session_state.get('refresh_flag', False):
            st.session_state.figure_urls = []
            if args.figure_urls:
                for figure_id in args.figure_urls.keys():
                    st.session_state.figure_urls.append({'url': args.figure_urls[figure_id]['url'], 'type': args.figure_urls[figure_id]['type']})

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

                p_index = list(figure_type_options.keys()).index(entry['type']) if st.session_state.get('modify_mode', False) and entry['type'] else 0
                selected_type = col2.selectbox(f"图片类型 for Figure {i+1}", options=list(figure_type_options.keys()), format_func=lambda x: f"{x}: {figure_type_options[x]}", index=p_index, key=f'figure_type_{i}')
                st.session_state.figure_urls[i]['type'] = selected_type  # 更新图片类型

                col3.write(f'URL: {url[:20]}...')

                delete_button = col4.button('删除', key=f'delete_url_{i}')
                if delete_button:
                    delete_option(i, 'figure_urls')
                    st.experimental_rerun()

def annotate_figures_auto(args):
    option_content = "  ".join(st.session_state.get('options_list', "")) if args.answer_type in ['SC', 'MC'] else ""
    try:
        solution = args.solution if args.solution else ""
    except Exception as e:
        solution = ''
    text_contain_fig = args.problem + " " + option_content + " " + solution
    url_dict = find_figure_urls(text_contain_fig)
    if url_dict:
        st.write("**检测出本题有图片**")
        args.figure_exists = "是"
        if st.session_state.get('modify_mode', False):
            if args.figure_dependent or args.figure_dependent == None:
                p_index = 0
            else:
                p_index = 1
        else:
            p_index = 0
        figure_dependent = st.radio('该题目是否依赖图片', ('依赖', '不依赖'), key=f"figure_dependent_{st.session_state.get('input_reset_counter', 0)}", index=p_index)
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
            
        if st.session_state.get('modify_mode', False) and st.session_state.get('refresh_flag', False):
            st.session_state.figure_urls = []
            if args.figure_urls:
                for figure_id in args.figure_urls.keys():
                    st.session_state.figure_urls.append({'url': args.figure_urls[figure_id]['url'], 'type': args.figure_urls[figure_id]['type']})
        elif st.session_state.get('modify_mode', False) and not st.session_state.get('refresh_flag', False):
            existing_urls = [figure['url'] for figure in st.session_state.figure_urls]
            updated_figure_urls = []
            for url in url_dict.values():
                if url in existing_urls:
                    matching_figure = next((figure for figure in st.session_state.figure_urls if figure['url'] == url), None)
                    if matching_figure:
                        updated_figure_urls.append({"url": url, "type": matching_figure["type"]})
                else:
                    updated_figure_urls.append({"url": url, "type": None})
            st.session_state.figure_urls = updated_figure_urls
        else:
            st.session_state.figure_urls = [{'url': url, 'type': None} for url in url_dict.values()]
        
        for i, entry in enumerate(st.session_state.figure_urls):
            col1, col2, col3 = st.columns([3, 6, 3])  # 分配空间
            url = entry['url']
            try:
                col1.image(url, caption=f'figure{i+1}', use_column_width=True)  # 显示图片
            except Exception as e:
                col1.write("Failed!")
            p_index = list(figure_type_options.keys()).index(entry['type']) if st.session_state.get('modify_mode', False) and entry['type'] else 0
            selected_type = col2.selectbox(f"figure{i+1} 的类型", options=list(figure_type_options.keys()), format_func=lambda x: f"{x}: {figure_type_options[x]}", index=p_index, key=f'figure_type_{i}')
            st.session_state.figure_urls[i]['type'] = selected_type  # 更新图片类型
            col3.write(f'URL: {url[:50]}...')  # 显示URL
    else:
        st.write("**未检测出图片**")
        args.figure_exists = "否"
    

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
            st.experimental_rerun()

def save_modified(args):
    if st.button('保存更改'):
        valid, message = save_annotation(args)
        if valid:
            save_to_file(message, args.output_folder, st.session_state.current_file_name)


def quit_modify_mode():
    if st.button('退出修改模式'):
        st.session_state.modify_mode = False
        st.session_state.refresh_flag = True # 用来处理列表、字典变量的修改
        st.session_state['reset_needed'] = True
        reset_session_state()
        st.experimental_rerun()

def delete_problem(args):
    if st.button('删除本题'):
        delete_file(args.output_folder, st.session_state.current_file_name)
        st.session_state.modify_mode = False
        st.session_state.refresh_flag = True
        st.session_state['reset_needed'] = True
        reset_session_state()
        st.experimental_rerun()


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
        
        annotate_problem_context(args)
        
        if args.answer_type == 'SC': # 单选
            annotate_type_single_choice(args)
        elif args.answer_type == 'MC': # 多选
            annotate_type_multi_choice(args)
        elif args.answer_type == 'TF': # 判断
            annotate_type_judge(args)
        elif args.answer_type in ['NV', 'IN', 'EX', 'EQ', 'TUP']: # 数值 区间 表达式 方程(open questions)
            annotate_type_single_blank(args)
        elif args.answer_type == 'MPV': # 一题多问
            annotate_type_multi_problem(args)
        elif args.answer_type == 'MA': # 一题多解
            annotate_type_multi_answer(args)
        elif args.answer_type == 'SET': # 集合
            annotate_type_set(args)
        else:
            annotate_type_human_eval(args)
        
        annotate_solution(args)
        # annotate_figures(args)
        annotate_figures_auto(args)
        st.session_state.refresh_flag = False
        
        if st.session_state.get('modify_mode', False):
            col_save, col_delete, col_quit_modify = st.columns(3)
            with col_save:
                save_modified(args)
            with col_delete:
                delete_problem(args)
            with col_quit_modify:
                quit_modify_mode()
        else: 
            col_current, col_next, col_next_without_clean = st.columns(3)
            with col_current:
                save_problem(args)
            with col_next:
                next_problem(args)
            with col_next_without_clean:
                next_problem_without_clean(args)
        
    
def show_sidebar(args):
    with st.sidebar:
        st.title("此文档已标注:")
        for num, (file_name, json_content) in enumerate(args.annotated_list):
            problem_title = json_content['problem']
            if st.button(f'**{file_name}**\n\n{problem_title[:100]}...'):
                # args.current_json = json_content
                st.session_state.modify_mode = True
                st.session_state.refresh_flag = True
                st.session_state.current_json = json_content
                st.session_state.current_file_name = file_name
                for key, value in json_content.items():
                    setattr(args, key, value)
            elif st.session_state.get('current_json', False):
                for key, value in st.session_state.current_json.items():
                    setattr(args, key, value)


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
    show_document(args, col1, subject_competition_dict) # choose subject and competition
    # args.output_folder = os.path.join(args.output_dir, args.subject, args.competition, args.file_name)
    # load(args) # get current question_number
    
    # # modify
    # args.annotated_list = load_annotation(args.output_folder)
    # if args.annotated_list:
    #     show_sidebar(args)
    
    show_annotate(args, col2)
    annotate(args, col2)

import streamlit as st
from utils import *
import argparse
import os
from datetime import datetime
from answer_type import *


answer_type_options_ = {
    'NV': 'Numeric question',
    'SET': 'Set',
    'IN': 'Interval',
    'EX': 'Expression',
    'EQ': 'Equation',
    'TUP': 'Tuple'
}

answer_type_options = {
    'SC': 'Single choice',
    'MC': 'Multiple choice',
    'TF': 'True/False',
    'NV': 'Numeric question (e.g., 1900, $\log_{2}9$)',
    'SET': 'Set (e.g., {1, 2, 3})',
    'IN': 'Interval (e.g., (1, 3])',
    'EX': 'Expression (e.g., $4 x^{2}-8 x+2$)',
    'EQ': 'Equation (e.g., $y-x=\\frac{1}{2}$)',
    'TUP': 'Tuple (e.g., (3, 4))', # e.g. find all pairs of (x, y) that ...
    'MPV': 'Multiple values per question',
    'MA': 'Multiple answers per question',
    'OT': 'Other (requires human evaluation)'
}


def init_page():
    st.set_page_config(layout="wide")
    col1, col2 = st.columns([10, 3.5])
    col3, col4 = st.columns([10, 3.5])
    return col1, col2, col3, col4

def show_document(args, column_up, column_down, d):
    with column_up:
        col1, col2, col3 = st.columns(3)
        with col1:
            subjects = list(d.keys())
            subject = st.selectbox('Select subject', options=subjects, index=0)
        with col2:
            competitions = d[subject]
            competition = st.selectbox('Select competition', options=competitions, index=0)
        args.subject, args.competition = subject, competition
        folder_path = os.path.join(args.data_dir, subject, competition)
        assert os.path.exists(folder_path)
        with col3:
            file_names = list_files_in_directory(folder_path)
            selected_file = st.selectbox('Select file', options=file_names, index=0)
            args.file_name = selected_file
        
        # Determine the final storage location
        # For a particular test paper
        args.output_folder = os.path.join(args.output_dir, args.subject, args.competition, args.file_name)
        # For the current competition
        args.output_folder_com = os.path.join(args.output_dir, args.subject, args.competition)
        
        load(args) # get current question_number
    
        # modify
        args.annotated_list = load_annotation(args.output_folder)
        if args.annotated_list:
            show_sidebar(args)    
        
            
        if 'display_pdf' not in st.session_state:
            st.session_state['display_pdf'] = True
        display_pdf_option = st.checkbox('Enable PDF preview', value=st.session_state['display_pdf'])
        
        # st.header(selected_file+'.pdf')
        
    with column_down:
        if selected_file:
            if not os.path.exists(os.path.join(folder_path, f"{selected_file}.md")):
                # st.header(selected_file+'.pdf')
                pdf_file_path = os.path.join(folder_path, f"{selected_file}.pdf")
                base64_pdf_content = get_pdf_display_content(pdf_file_path)
                display_pdf(base64_pdf_content)
            else:
                if display_pdf_option:
                    col_left, col_right = st.columns([3, 2])
                    with col_left:
                        # st.header(selected_file+'.pdf')
                        pdf_file_path = os.path.join(folder_path, f"{selected_file}.pdf")
                        base64_pdf_content = get_pdf_display_content(pdf_file_path)
                        display_pdf(base64_pdf_content)
                    with col_right:
                        md_file_path = os.path.join(folder_path, f"{selected_file}.md")
                        if os.path.exists(md_file_path):
                            # st.header(selected_file+'.md')
                            with open(md_file_path, "r", encoding='utf-8') as file:
                                markdown_content = file.read()
                                st.text_area('hide', markdown_content, height=800, label_visibility="collapsed", key="md1")
                        else:
                            st.header('No markdown file provided!')
                else: # no pdf
                    md_file_path = os.path.join(folder_path, f"{selected_file}.md")
                    if os.path.exists(md_file_path):
                        # st.header(selected_file+'.md')
                        with open(md_file_path, "r", encoding='utf-8') as file:
                            markdown_content = file.read()
                            st.text_area('hide', markdown_content, height=800, label_visibility="collapsed", key="md2")
                    else:
                        st.header('No markdown file provided!')
        
        enhanced_file_names = ['Do not use'] + file_names  # Add "Do not use" option
        selected_file_enhanced = st.selectbox('Select file (optional)', options=enhanced_file_names, index=0)
        
        if selected_file_enhanced != 'Do not use':
            if not os.path.exists(os.path.join(folder_path, f"{selected_file_enhanced}.md")):
                # st.header(selected_file_enhanced + '.pdf')
                pdf_file_path = os.path.join(folder_path, f"{selected_file_enhanced}.pdf")
                if os.path.exists(pdf_file_path):
                    base64_pdf_content = get_pdf_display_content(pdf_file_path)
                    display_pdf(base64_pdf_content)
            else:
                if display_pdf_option:
                    enhanced_col_left, enhanced_col_right = st.columns([3, 2])  # Create new variables for clarity
                    with enhanced_col_left:
                        # st.header(selected_file_enhanced + '.pdf')
                        pdf_file_path = os.path.join(folder_path, f"{selected_file_enhanced}.pdf")
                        if os.path.exists(pdf_file_path):
                            base64_pdf_content = get_pdf_display_content(pdf_file_path)
                            display_pdf(base64_pdf_content)
                    with enhanced_col_right:
                        # st.header(selected_file_enhanced + '.md')
                        md_file_path = os.path.join(folder_path, f"{selected_file_enhanced}.md")
                        if os.path.exists(md_file_path):
                            with open(md_file_path, "r", encoding='utf-8') as file:
                                markdown_content = file.read()
                                st.text_area('hide', markdown_content, height=800, label_visibility="collapsed", key="md3")
                        else:
                            st.header('No markdown file provided!')
                else:
                    # st.header(selected_file_enhanced + '.md')
                    md_file_path = os.path.join(folder_path, f"{selected_file_enhanced}.md")
                    if os.path.exists(md_file_path):
                        with open(md_file_path, "r", encoding='utf-8') as file:
                            markdown_content = file.read()
                            st.text_area('hide', markdown_content, height=800, label_visibility="collapsed", key="md4")
                    else:
                        st.header('No markdown file provided!')
                        
                        
        
def load(args):
    # Number of annotated questions in the current test paper
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
    
    # Total number of annotated questions in the current competition
    if "question_number_com" not in st.session_state:
        st.session_state.question_number_com = 0

    question_number_com = 0
    if os.path.exists(args.output_folder_com):
        for root, dirs, files in os.walk(args.output_folder_com):
            for file in files:
                if file.endswith(".json"):
                    question_number_com += 1
        st.session_state.question_number_com = question_number_com
    else:
        st.session_state.question_number_com = 0
        
        

def show_annotate(args, column_up, column_down):
    with column_up:
        b, c = st.columns(2)
        # with a:
        #     st.subheader('Annotation information')
        with b:
            st.subheader('Current file annotated: ' + str(st.session_state.question_number))
        with c:
            st.subheader('Current competition annotated: ' + str(st.session_state.question_number_com))
        col_subject, col_competition, col_file_name = st.columns(3)
        with col_subject:
            st.text_input('Subject', value=args.subject, disabled=True)
        with col_competition:
            st.text_input('Competition name', value=args.competition, disabled=True)
        with col_file_name:
            st.text_input('File name', value=args.file_name, disabled=True)
        
    with column_down.container(height=800):
        annotate(args, column_down)


def annotate_problem_context(args):
    if st.session_state.get('modify_mode', False):
        p_index = 1 if hasattr(args, 'context') and args.context else 0
    else:
        p_index = 0
    need_context = st.radio('Do you need to add context information (supplement information from **previous questions**)?', ('No', 'Yes'), key=f"need_context_{st.session_state.get('input_reset_counter', 0)}", index=p_index)
    args.need_context = need_context
    if need_context == 'Yes':
        context = st.text_area('Context information', value=args.context if st.session_state.get('modify_mode', False) else '', key=f"context_{st.session_state.get('input_reset_counter', 0)}")
        args.context = context
        st.markdown('Context preview:')
        st.markdown(normalize_display_figure(context), unsafe_allow_html=True)
    else:
        args.context = None
    problem = st.text_area('**Problem**', value=args.problem if st.session_state.get('modify_mode', False) else '', key=f"problem_{st.session_state.get('input_reset_counter', 0)}", height=175)
    # print(problem, st.session_state[f"problem_{st.session_state.get('input_reset_counter', 0)}"], f"problem_{st.session_state.get('input_reset_counter', 0)}")
    args.problem = problem
    st.markdown('Problem preview:')
    st.markdown(normalize_display_figure(problem), unsafe_allow_html=True)
    # annotate_figures_auto(args)
    # st.markdown(replace_url_with_not(problem, st.session_state.figure_urls) if args.figure_exists else problem, unsafe_allow_html=True)
    
    if st.session_state.get('modify_mode', False):
        p_index = list(answer_type_options.keys()).index(args.answer_type)
    else:
        p_index = 0
    answer_type = st.selectbox('**Answer type**', options=list(answer_type_options.keys()), format_func=lambda x: f'{x}: {answer_type_options[x]}', index=p_index)
    args.answer_type = answer_type
    

def annotate_solution(args):
    if st.session_state.get('modify_mode', False):
        p_index = 1 if args.solution else 0
    else:
        p_index = 0
    have_solution = st.radio('Is there a solution?', ('No', 'Yes'), index=p_index, key=f"have_solution_{st.session_state.get('input_reset_counter', 0)}")
    args.have_solution = have_solution
    if have_solution == "Yes":
        solution = st.text_area('Solution', value=args.solution if st.session_state.get('modify_mode', False) else '', key=f"solution_{st.session_state.get('input_reset_counter', 0)}")
        args.solution = solution
        st.markdown('Solution preview:')
        st.markdown(normalize_display_figure(solution), unsafe_allow_html=True)
        # annotate_figures_auto(args)
        # st.markdown(replace_url_with_not(solution, st.session_state.figure_urls) if args.figure_exists else solution, unsafe_allow_html=True)
    else:
        args.solution = None

def annotate_figures(args):
    st.write("**Note: The annotation of figures covers the problem statement, multiple choice options, and solution, with numbering continuous within a question.**")
    p_index = 1 if st.session_state.get('modify_mode', False) and args.figure_exists else 0
    figure_exists = st.radio('**Are there figures (in problem statement, options, or solution)?**', ('No', 'Yes'), key=f"figure_exists_{st.session_state.get('input_reset_counter', 0)}", index = p_index)
    args.figure_exists = figure_exists
    if figure_exists == 'Yes':
        if st.session_state.get('modify_mode', False):
            if args.figure_dependent or args.figure_dependent == None:
                p_index = 0
            else:
                p_index = 1
        else:
            p_index = 0
        figure_dependent = st.radio('Does this question depend on the figures?', ('Dependent', 'Independent'), key=f"figure_dependent_{st.session_state.get('input_reset_counter', 0)}", index=p_index)
        args.figure_dependent = figure_dependent
        figure_type_options = {
            '1': 'Geometric figures (math related, plane, geometry, etc.)',
            '2': 'Any chart (tables, bar charts, line charts, etc. representing statistical data)',
            '3': 'Natural scenery (geographical landscapes, starry sky)',
            '4': 'Science related (e.g., physical diagrams, chemical organics, biological cells, genes, geographical maps, engineering machinery, etc.)',
            '5': 'Abstract objects (abstract objects and concepts, possibly including symbols, algorithm diagrams, flowcharts, etc.)',
            '6': 'Others',
        }
        if 'figure_urls' not in st.session_state:
            st.session_state.figure_urls = []
            
        if st.session_state.get('modify_mode', False) and st.session_state.get('refresh_flag', False):
            st.session_state.figure_urls = []
            if args.figure_urls:
                for figure_id in args.figure_urls.keys():
                    st.session_state.figure_urls.append({'url': args.figure_urls[figure_id]['url'], 'type': args.figure_urls[figure_id]['type']})

        new_url = st.text_input('Add new figure URL', value='', key=f"new_url_{st.session_state.get('input_reset_counter', 0)}")
        if st.button('Add figure URL'):
            if new_url:
                st.session_state.figure_urls.append({'url': new_url, 'type': None})  # Add dictionary instead of just URL
        
        if 'figure_urls' in st.session_state:
            for i, entry in enumerate(st.session_state.figure_urls):
                col1, col2, col3, col4 = st.columns([3, 5.5, 3.5, 1])  # Allocate space for image preview, image type selection, URL text, and delete button
                url = entry['url']
                if url:
                    try:
                        col1.image(url, caption=f'Figure {i+1}', use_column_width=True)  # Display image using URL
                    except Exception as e:
                        col1.write(f"Image at {url} cannot be displayed.")

                p_index = list(figure_type_options.keys()).index(entry['type']) if st.session_state.get('modify_mode', False) and entry['type'] else 0
                selected_type = col2.selectbox(f"Figure type for Figure {i+1}", options=list(figure_type_options.keys()), format_func=lambda x: f"{x}: {figure_type_options[x]}", index=p_index, key=f'figure_type_{i}')
                st.session_state.figure_urls[i]['type'] = selected_type  # Update figure type

                col3.write(f'URL: {url[:20]}...')

                delete_button = col4.button('Delete', key=f'delete_url_{i}')
                if delete_button:
                    delete_option(i, 'figure_urls')
                    st.rerun()

def annotate_figures_auto(args):
    option_content = "  ".join(st.session_state.get('options_list', "")) if args.answer_type in ['SC', 'MC'] else ""
    try:
        solution = args.solution if args.solution else ""
    except Exception as e:
        solution = ''
    try:
        context = args.context if args.context else ""
    except Exception as e:
        context = ""
    text_contain_fig = context + " " + args.problem + " " + option_content + " " + solution + " "
    url_dict = find_figure_urls(text_contain_fig)
    if url_dict:
        st.write("**Figures detected in this question**")
        args.figure_exists = "Yes"
        # if st.session_state.get('modify_mode', False):
        #     if args.figure_dependent or args.figure_dependent == None:
        #         p_index = 0
        #     else:
        #         p_index = 1
        # else:
        #     p_index = 0
        # figure_dependent = st.radio('Does this question depend on the figures?', ('Dependent', 'Independent'), key=f"figure_dependent_{st.session_state.get('input_reset_counter', 0)}", index=p_index)
        # args.figure_dependent = figure_dependent
        figure_type_options = {
            '1': 'Geometric figures (math related, plane, geometry, etc.)',
            '2': 'Any chart (tables, bar charts, line charts, etc. representing statistical data)',
            '3': 'Natural scenery (geographical landscapes, starry sky)',
            '4': 'Science related (e.g., physical diagrams, chemical organics, biological cells, genes, geographical maps, engineering machinery, etc.)',
            '5': 'Abstract objects (abstract objects and concepts, possibly including symbols, algorithm diagrams, flowcharts, etc.)',
            '6': 'Others',
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
            # col1, col2, col3 = st.columns([3, 6, 3])  # Allocate space
            col1, col2 = st.columns([5, 5])  # Allocate space
            url = entry['url']
            try:
                col1.image(url, caption=f'figure{i+1}', use_column_width=True)  # Display image
            except Exception as e:
                col1.write("Failed!")
            p_index = list(figure_type_options.keys()).index(entry['type']) if st.session_state.get('modify_mode', False) and entry['type'] else 0
            selected_type = col2.selectbox(f"figure{i+1} type", options=list(figure_type_options.keys()), format_func=lambda x: f"{x}: {figure_type_options[x]}", index=p_index, key=f'figure_type_{i}')
            st.session_state.figure_urls[i]['type'] = selected_type  # Update figure type
            # col3.write(f'URL: {url[:50]}...')  # Display URL
    else:
        st.write("**No figures detected**")
        args.figure_exists = "No"
    

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
    if args.figure_exists == "Yes":
        figure_urls = st.session_state.get('figure_urls', [])
        assert figure_urls
        for i in range(1, len(figure_urls)+1):
            id_url[i] = {'url': figure_urls[i-1]['url'], 'type': figure_urls[i-1]['type']}

    annotations = {
        'answer_type': args.answer_type, # Required
        'context': args.context if args.need_context == "Yes" else None,
        'problem': args.problem, # Required
        'options': option_dict_with_choice if option_dict_with_choice and args.answer_type in ['SC', 'MC'] else None,
        'answer': args.answer_label, # Required
        'unit': args.unit if args.answer_type not in ['SC', 'MC', 'TF', 'OT', 'TUP'] else None,
        'answer_sequence': args.answer_sequence if args.answer_type == 'MPV' else None,
        'type_sequence': args.type if args.answer_type in ['MPV', 'MA'] else None,
        'solution': args.solution if args.have_solution == 'Yes' and args.solution != '' else None,
        'figure_exists': True if args.figure_exists == "Yes" else False, # Required
        # 'figure_dependent': None if args.figure_exists != "Yes" else (args.figure_dependent == "Dependent"),
        'figure_urls': id_url if args.figure_exists == "Yes" else None,
        # 'scenario': args.scenario if args.answer_type == 'OT' else None,
        
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
    if st.button('Save this problem'):
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
            st.rerun()

def save_modified(args):
    if st.button('Save changes'):
        valid, message = save_annotation(args)
        if valid:
            save_to_file(message, args.output_folder, st.session_state.current_file_name)


def quit_modify_mode():
    if st.button('Exit modify mode'):
        st.session_state.modify_mode = False
        st.session_state.refresh_flag = True # To handle modifications of list and dictionary variables
        st.session_state['reset_needed'] = True
        reset_session_state()
        st.rerun()

def delete_problem(args):
    if st.button('Delete this problem'):
        delete_file(args.output_folder, st.session_state.current_file_name)
        st.session_state.modify_mode = False
        st.session_state.refresh_flag = True
        st.session_state['reset_needed'] = True
        reset_session_state()
        st.rerun()


def next_problem(args):
    if st.button('Save & Next problem'):
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
            st.rerun()
        else:
            print(message)


def next_problem_without_clean(args):
    if st.button('Save & Next problem (without clearing)'):
        valid, message = save_annotation(args)
        if valid:
            if 'new_file_flag' not in st.session_state:
                st.session_state.new_file_flag = True
            if st.session_state.new_file_flag:
                st.session_state.current_time = datetime.now().strftime("%m_%d_%H_%M_%S")

            save_to_file(message, args.output_folder, st.session_state.current_time)
            st.session_state.new_file_flag = True
            st.session_state.question_number += 1
            st.rerun()
        else:
            print(message)


def annotate(args, column):
    # with column.container(height=1000):
    
    annotate_problem_context(args)
    
    if args.answer_type == 'SC': # Single choice
        annotate_type_single_choice(args)
    elif args.answer_type == 'MC': # Multiple choice
        annotate_type_multi_choice(args)
    elif args.answer_type == 'TF': # True/False
        annotate_type_judge(args)
    elif args.answer_type in ['NV', 'IN', 'EX', 'EQ', 'TUP']: # Numeric, Interval, Expression, Equation (open questions)
        annotate_type_single_blank(args)
    elif args.answer_type == 'MPV': # Multiple values per question
        annotate_type_multi_problem(args)
    elif args.answer_type == 'MA': # Multiple answers per question
        annotate_type_multi_answer(args)
    elif args.answer_type == 'SET': # Set
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
        st.title("This document is annotated:")
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
            elif st.session_state.get('current_json', False) and st.session_state.get("modify_mode", False):
                for key, value in st.session_state.current_json.items():
                    setattr(args, key, value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="./data/", help="Location of documents to be annotated")
    parser.add_argument("--output_dir", type=str, default="./output/")
    args = parser.parse_args()
    
    subject_competition_dict = {}
    for subject in os.listdir(args.data_dir):
        if subject == ".DS_Store":
            continue
        if subject not in subject_competition_dict:
            subject_competition_dict[subject] = []
        for competition in os.listdir(os.path.join(args.data_dir, subject)):
            if competition == ".DS_Store":
                continue
            subject_competition_dict[subject].append(competition)
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    col1, col2, col3, col4 = init_page()
    show_document(args, col1, col3, subject_competition_dict) # choose subject and competition
    # args.output_folder = os.path.join(args.output_dir, args.subject, args.competition, args.file_name)
    # load(args) # get current question_number
    
    # # modify
    # args.annotated_list = load_annotation(args.output_folder)
    # if args.annotated_list:
    #     show_sidebar(args)
    
    show_annotate(args, col2, col4)
    # annotate(args, col2)

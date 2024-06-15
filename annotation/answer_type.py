import streamlit as st
from utils import *
from main import answer_type_options, answer_type_options_

def annotate_type_single_choice(args): # Single choice question
    if 'options_list' not in st.session_state:
        st.session_state.options_list = []
    
    if st.session_state.get('modify_mode', False) and st.session_state.get('refresh_flag', False):
        st.session_state.options_list = []
        if args.options:
            for option_content in args.options.values():
                st.session_state.options_list.append(option_content)          
                
    # automatic identity choices
    if 'auto_identity_choices' not in st.session_state:
        st.session_state['auto_identity_choices'] = False
    auto_identity_choices = st.checkbox('Use automatic option identification', value=st.session_state['auto_identity_choices'])
    if auto_identity_choices:
        raw_text = st.text_area("Input text segment with options (supports most cases, some may need adjustments):", value="", key=f"auto_text_input_{st.session_state.get('input_reset_counter', 0)}")
        if st.button('Identify automatically'):
            identified_options = identify_choices(raw_text+"\n")  # Assuming identify_choices is your function
            if identified_options:
                st.session_state.options_list = identified_options
                st.rerun()

    
    new_option = st.text_input('Add new option', value='', key=f"new_option_{st.session_state.get('input_reset_counter', 0)}")
    if st.button('Add option'):
        if new_option:
            st.session_state[f'option_{len(st.session_state.options_list)}'] = new_option
            st.session_state.options_list.append(new_option)
            
    # reload option_{i}
    if st.session_state.get('options_list', False):
        for i in range(len(st.session_state.get('options_list'))):
            st.session_state[f'option_{i}'] = st.session_state.options_list[i]


    if 'options_list' in st.session_state:
        for i, option in enumerate(st.session_state.options_list):
            col1, col2 = st.columns([10, 3])
            edited_option = col1.text_input(f'Option {chr(65 + i)}', value=st.session_state[f'option_{i}'], key=f"edited_option_{i}_{st.session_state.get('input_reset_counter', 0)}")
            col1.markdown("**Preview:** "+normalize_display_figure(st.session_state[f'option_{i}']), unsafe_allow_html=True)
            if edited_option != option:
                st.session_state.options_list[i] = edited_option
                st.session_state[f'option_{i}'] = edited_option
                st.rerun()
            # col1.markdown(option_markdown, unsafe_allow_html=True)
            
            delete_button = col2.button('Delete', key=f'delete_{i}')
            if delete_button:
                delete_option(i, 'options_list')
                st.session_state.pop(f'option_{i}', None)
                st.rerun()


    if st.session_state.options_list:
        option_labels = [chr(65+i) for i in range(len(st.session_state.options_list))]  # A, B, C, D...
        p_index = option_labels.index(args.answer) if st.session_state.get('modify_mode', False) and type(args.answer) == str else 0
        answer_label = st.selectbox('Answer [answer*]', options=option_labels, index=p_index, key=f"answer_label_{st.session_state.get('input_reset_counter', 0)}") # Letter
        answer = st.session_state.options_list[ord(answer_label) - 65] # Index, starting from 0
        args.answer_label = answer_label
        st.write(f"Selected answer content: {normalize_display_figure(answer)}", unsafe_allow_html=True)
        # annotate_figures_auto(args)
        # st.markdown(f"Selected answer content: {replace_url_with_not(answer, st.session_state.figure_urls) if args.figure_exists else answer}", unsafe_allow_html=True)
    else:
        st.write("Please add at least one option")

def annotate_type_multi_choice(args): # Multiple choice question
    if 'options_list' not in st.session_state:
        st.session_state.options_list = []
        
    if st.session_state.get('modify_mode', False) and st.session_state.get('refresh_flag', False):
        st.session_state.options_list = []
        if args.options:
            for option_content in args.options.values():
                st.session_state.options_list.append(option_content)
                
    # automatic identity choices
    if 'auto_identity_choices' not in st.session_state:
        st.session_state['auto_identity_choices'] = False
    auto_identity_choices = st.checkbox('Use automatic option identification', value=st.session_state['auto_identity_choices'])
    if auto_identity_choices:
        raw_text = st.text_area("Input text segment with options (supports most cases, some may need adjustments):", value="", key=f"auto_text_input_{st.session_state.get('input_reset_counter', 0)}")
        if st.button('Identify automatically'):
            identified_options = identify_choices(raw_text+"\n")  # Assuming identify_choices is your function
            if identified_options:
                st.session_state.options_list = identified_options
                st.rerun()
                
    new_option = st.text_input('Add new option', value='', key=f"new_option_{st.session_state.get('input_reset_counter', 0)}")
    if st.button('Add option'):
        if new_option:
            st.session_state[f'option_{len(st.session_state.options_list)}'] = new_option
            st.session_state.options_list.append(new_option)
            
    # reload option_{i}
    if st.session_state.get('options_list', False):
        for i in range(len(st.session_state.get('options_list'))):
            st.session_state[f'option_{i}'] = st.session_state.options_list[i]

    if 'options_list' in st.session_state:
        for i, option in enumerate(st.session_state.options_list):
            col1, col2 = st.columns([10, 3])
            edited_option = col1.text_input(f'Option {chr(65 + i)}', value=st.session_state[f'option_{i}'], key=f"edited_option_mul_{i}_{st.session_state.get('input_reset_counter', 0)}")
            col1.markdown("**Preview:** "+normalize_display_figure(st.session_state[f'option_{i}']), unsafe_allow_html=True)
            if edited_option != option:
                st.session_state.options_list[i] = edited_option
                st.session_state[f'option_{i}'] = edited_option
                st.rerun()
            # option_markdown = f'Option {chr(65+i)}: {option}'
            # col1.markdown(option_markdown, unsafe_allow_html=True)
            
            delete_button = col2.button('Delete', key=f'delete_{i}')
            if delete_button:
                delete_option(i, 'options_list')
                st.session_state.pop(f'option_{i}', None)
                st.rerun()

    if st.session_state.options_list:
        option_labels = [chr(65+i) for i in range(len(st.session_state.options_list))]  # A, B, C, D...
        p_list = args.answer if st.session_state.get('modify_mode', False) and type(args.answer)==list else None
        selected_answer_labels = st.multiselect('Answer [answer*]', default=p_list, options=option_labels, key=f"answer_label_{st.session_state.get('input_reset_counter', 0)}")  # Use multiselect instead of selectbox
        selected_answers = [st.session_state.options_list[ord(label) - 65] for label in selected_answer_labels]  # Get selected answers based on labels
        args.answer_label = selected_answer_labels # List of strings
        if selected_answers:
            temp_str = normalize_display_figure('\n\n'.join(selected_answers))
            st.write(f"Selected answer content: \n\n {temp_str}", unsafe_allow_html=True)
            # annotate_figures_auto(args)
            # temp_str = ', '.join(selected_answers)
            # st.markdown(f"Selected answer content: {replace_url_with_not(temp_str, st.session_state.figure_urls) if args.figure_exists else temp_str}", unsafe_allow_html=True)
        else:
            st.write("Please select at least one option as the answer")
    else:
        st.write("Please add at least one option")

def annotate_type_judge(args): # True/False question
    p_index = 1 if st.session_state.get('modify_mode', False) and args.answer=='False' else 0
    judgment_answer = st.radio(
        "True/False answer [answer*]", 
        ['True', 'False'], 
        index=p_index,
        key=f"judgment_answer_{st.session_state.get('input_reset_counter', 0)}"
    )

    args.answer_label = judgment_answer  # This will be either 'True' or 'False'
    st.write(f"Selected answer content: {judgment_answer}")

def annotate_type_single_blank(args):
    numeric_answer = st.text_input(
        "Answer [answer*] (supports TeX)", 
        key=f"numeric_answer_{st.session_state.get('input_reset_counter', 0)}",
        value=args.answer if st.session_state.get('modify_mode', False) and type(args.answer)==str else ''
    )
    st.write(f"Answer preview: {numeric_answer}")
    args.answer_label = numeric_answer # String
    
    unit = st.text_input(
        "Unit [unit*] (leave blank if no unit)",
        key=f"unit_{st.session_state.get('input_reset_counter', 0)}",
        value=args.unit if st.session_state.get('modify_mode', False) and args.unit else ''
    )
    if unit.strip():
        args.unit = unit
    else:
        args.unit = None

def annotate_type_multi_problem(args): # Multiple values per question
    if 'multi_parts' not in st.session_state:
        st.session_state.multi_parts = []
        
    if st.session_state.get('modify_mode', False) and st.session_state.get('refresh_flag', False):
        st.session_state.multi_parts = []
        if args.answer_sequence:
            for i in range(len(args.answer_sequence)):
                st.session_state.multi_parts.append(
                    {'question': args.answer_sequence[i],
                     'type': args.type_sequence[i],
                     'answer': args.answer[i],
                     'unit': args.unit[i]
                     }
                )
                
    part_question = st.text_input("Description (e.g., the value of $x$)", '', key=f"part_question_{st.session_state.get('input_reset_counter', 0)}")
    part_type = st.selectbox("Type", list(answer_type_options_.keys()), key=f"part_type_{st.session_state.get('input_reset_counter', 0)}", format_func=lambda x: f'{x}: {answer_type_options_[x]}')
    part_answer = st.text_input("Answer (supports TeX)", '', key=f"part_answer_{st.session_state.get('input_reset_counter', 0)}")
    part_unit = st.text_input("Unit (leave blank if no unit)", '', key=f"part_unit_{st.session_state.get('input_reset_counter', 0)}")
    
    if st.button('Add new value', key=f"add_new_part_{st.session_state.get('input_reset_counter', 0)}"):
        if part_question and part_answer:  # Ensure there is a question part and an answer before adding
            st.session_state.multi_parts.append({
                'question': part_question,
                'type': part_type,
                'answer': part_answer,
                'unit': part_unit if part_unit and part_unit.strip() else None
            })
    for i, part in enumerate(st.session_state.multi_parts):
        col_part, col_delete = st.columns([9, 1])
        col_part.markdown(f"Value {i+1}: Name: {part['question']}, Answer: {part['answer']}, Unit: {part['unit']}")
        delete_button = col_delete.button("Delete", key=f"delete_part_{i}_{st.session_state.get('input_reset_counter', 0)}")
        if delete_button:
            delete_option(i, 'multi_parts')
            st.rerun()
    
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
        
def annotate_type_multi_answer(args): # Multiple answers per question
    if 'multi_solutions' not in st.session_state:
        st.session_state.multi_solutions = []
        
    if st.session_state.get('modify_mode', False) and st.session_state.get('refresh_flag', False):
        st.session_state.multi_solutions = []
        if args.answer:
            for i in range(len(args.answer)):
                st.session_state.multi_solutions.append(
                    {
                        'answer': args.answer[i],
                        'type': args.type_sequence[i],
                        'unit': args.unit[i]
                     }
                )
        
    solution_answer = st.text_input("Answer (supports TeX, e.g., `$\\sqrt{2}$`)", '', key=f"solution_answer_{st.session_state.get('input_reset_counter', 0)}")
    solution_type = st.selectbox("Type", list(answer_type_options_.keys()), key=f"solution_type_{st.session_state.get('input_reset_counter', 0)}", format_func=lambda x: f'{x}: {answer_type_options_[x]}')
    solution_unit = st.text_input("Unit (leave blank if no unit)", '', key=f"solution_unit_{st.session_state.get('input_reset_counter', 0)}")

    if st.button('Add answer'):
        if solution_answer:
            st.session_state.multi_solutions.append({
                'answer': solution_answer,
                'type': solution_type,
                'unit': solution_unit if solution_unit.strip() else None
            })
                    
    for i, solution in enumerate(st.session_state.multi_solutions):
        col_solution, col_delete = st.columns([9, 1])
        unit_text = f", Unit: {solution['unit']}" if solution['unit'] else ""
        col_solution.markdown(f"Solution {i+1}: Answer: {solution['answer']}{unit_text}")
        delete_button = col_delete.button("Delete", key=f"delete_solution_{i}_{st.session_state.get('input_reset_counter', 0)}")
        if delete_button:
            delete_option(i, 'multi_solutions')
            st.rerun()
    
    answer_label = []
    solution_type_lst = []
    unit = []
    for item in st.session_state.multi_solutions:
        answer_label.append(item['answer'])
        solution_type_lst.append(item['type'])
        unit.append(item['unit'])
    args.answer_label, args.type, args.unit = answer_label, solution_type_lst, unit
    
def annotate_type_set(args):  # Set
    if 'set_answers' not in st.session_state:
        st.session_state.set_answers = []
        
    if st.session_state.get('modify_mode', False) and st.session_state.get('refresh_flag', False):
        st.session_state.set_answers = []
        if args.answer:
            for item in args.answer:
                st.session_state.set_answers.append(item)
    
    new_element = st.text_input(
        "Add new element to the set (supports TeX, e.g., `$\\sqrt{2}$`, `$\\frac{1}{2}$`)",
        '',
        key=f"new_element_{st.session_state.get('input_reset_counter', 0)}"
    )
    if st.button('Add element', key=f"add_element_{st.session_state.get('input_reset_counter', 0)}"):
        if new_element:
            st.session_state.set_answers.append(new_element)
    for i, element in enumerate(st.session_state.set_answers):
        col_element, col_delete = st.columns([9, 1])
        with col_element:
            st.markdown(f"Element {i+1}: {element}")
        with col_delete:
            if st.button("Delete", key=f"delete_element_{i}_{st.session_state.get('input_reset_counter', 0)}"):
                delete_option(i, 'set_answers')
                st.rerun()

    args.answer_label = st.session_state.set_answers

    unit = st.text_input(
        "Unit [unit*] (leave blank if no unit)",
        value=args.unit if st.session_state.get('modify_mode', False) and args.unit else '',
        key=f"unit_{st.session_state.get('input_reset_counter', 0)}"
    )
    if unit.strip():
        args.unit = unit
    else:
        args.unit = None

def annotate_type_human_eval(args):
    
    numeric_answer = st.text_area(
        "Answer [answer*] (supports TeX)", 
        value=args.answer if st.session_state.get('modify_mode', False) else '',
        key=f"numeric_answer_{st.session_state.get('input_reset_counter', 0)}"
    )
    st.write(f"Answer preview: {numeric_answer}")
    args.answer_label = numeric_answer # String

    # scenario = st.text_input(
    #     "Description of the problem scenario (leave blank if not applicable)",
    #     value=args.scenario if st.session_state.get('modify_mode', False) else '',
    #     key=f"scenario_{st.session_state.get('input_reset_counter', 0)}"
    # )
    # args.scenario = scenario

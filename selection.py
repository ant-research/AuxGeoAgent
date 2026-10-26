import sys
import os
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from absl import flags
import problem as pr
import graph as gh
import ddar

DEFINITIONS = None
RULES = None

def split_question_by_last_semicolon(question_text):
    if ';' not in question_text:
        return question_text.strip(), ""
    
    last_semicolon_index = question_text.rfind(';')
    if last_semicolon_index == -1:
        return question_text.strip(), ""
    
    question_part = question_text[:last_semicolon_index + 1].strip()
    point_part = question_text[last_semicolon_index + 1:].strip()
    
    return question_part, point_part

def extract_points_from_point_string(point_str):
    points = set()
    
    if not point_str:
        return points
    
    equal_pos = point_str.find('=')
    if equal_pos == -1:
        return points
    
    left_part = point_str[:equal_pos].strip()
    matches = re.findall(r'\b([a-z][a-z0-9]*)\b', left_part)
    points.update(matches)
    
    return points

def extract_points_from_conclusion(conclusion):
    parts = conclusion.split()
    if len(parts) < 2:
        return set()
    
    points = set()
    for part in parts[1:]:
        if part and part[0].islower():
            points.add(part)
    
    return points

def filter_conclusions_by_point_points(missing_cons, point_points):
    filtered = []
    
    for con in missing_cons:
        con_points = extract_points_from_conclusion(con)
        if not con_points.intersection(point_points):
            filtered.append(con)
    
    return filtered

def create_temporary_problem_file(problem_name, question_text, temp_dir="temp_problems"):
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, f"{problem_name}.txt")
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(f"{problem_name}\n")
        f.write(f"{question_text}\n")
    
    return temp_file

def init_flags(problem_name, problems_file, mode="ddar"):
    flags.FLAGS.__dict__['__flags'].clear()
    
    flags.DEFINE_string('problems_file', problems_file, 'text file contains the problem strings.')
    flags.DEFINE_string('problem_name', problem_name, 'name of the problem to solve.')
    flags.DEFINE_string('mode', mode, 'either `ddar` (DD+AR) or `alphageometry`')
    flags.DEFINE_string('defs_file', 'defs.txt', 'definitions of available constructions to state a problem.')
    flags.DEFINE_string('rules_file', 'rules.txt', 'list of deduction rules used by DD.')
    flags.DEFINE_string('out_file', '', 'path to the solution output file.')
    
    flags.FLAGS.problems_file = problems_file
    flags.FLAGS.problem_name = problem_name
    flags.FLAGS.mode = mode
    flags.FLAGS.defs_file = 'defs.txt'
    flags.FLAGS.rules_file = 'rules.txt'
    flags.FLAGS.out_file = ''

def load_definitions_and_rules():
    global DEFINITIONS, RULES
    if DEFINITIONS is None:
        DEFINITIONS = pr.Definition.from_txt_file('defs.txt', to_dict=True)
    if RULES is None:
        RULES = pr.Theorem.from_txt_file('rules.txt', to_dict=True)

def run_ddar_for_problem(problem_name, question_text):
    try:
        temp_file = create_temporary_problem_file(problem_name, question_text)
        init_flags(problem_name, temp_file)
        
        problems = pr.Problem.from_txt_file(temp_file, to_dict=True, translate=False, target_name=problem_name)
        
        if problem_name not in problems:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return []
        
        this_problem = problems[problem_name]
        g, _, success = gh.Graph.build_problem(this_problem, DEFINITIONS)
        if not success:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return []
        
        g, level_times, status, branches, all_add = ddar.solve(g, RULES, this_problem, max_level=8192)
        
        conclusions = []
        for dep in all_added:
            points = [p.name for p in dep.args]  
            con = f"{dep.name} {' '.join(points)}"
            conclusions.append(con)
        
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return conclusions
        
    except Exception as e:
        if 'temp_file' in locals() and os.path.exists(temp_file):
            os.remove(temp_file)
        return []

def process_single_problem(problem_data):
    problem_id = problem_data['id']
    original_question = problem_data['question']
    original_conclusions = problem_data.get('conclusions', [])
    
    try:
        modified_question, point_part = split_question_by_last_semicolon(original_question)
        new_conclusions = run_ddar_for_problem(problem_id, modified_question)
        
        missing_conclusions = []
        if original_conclusions:
            original_set = set(original_conclusions)
            new_set = set(new_conclusions)
            missing_conclusions = list(original_set - new_set)
        
        point_points = extract_points_from_point_string(point_part)
        filtered_conclusions = filter_conclusions_by_point_points(missing_conclusions, point_points)
        
        return {
            'id': problem_id,
            'question': modified_question,
            'point': point_part,
            'conclusions': filtered_conclusions,
            'error': None
        }
        
    except Exception as e:
        return {
            'id': problem_id,
            'question': None,
            'point': None,
            'conclusions': [],
            'error': str(e)
        }

def main_process(input_jsonl, output_jsonl):

    temp_dir = "temp_problems1"
    
    if os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir)

    load_definitions_and_rules()
    
    problems_data = []
    with open(input_jsonl, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line.strip())
            problems_data.append(data)
    
    total = len(problems_data)
    start_index = 0
    
    if start_index < len(problems_data):
        problems_data = problems_data[start_index:]
    else:
        return
    
    completed = 0
    start_time = time.time()
    errors = []
    
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {executor.submit(process_single_problem, data): data['id'] for data in problems_data}
        
        with open(output_jsonl, 'w', encoding='utf-8') as out_f:
            for future in as_completed(futures):
                result = future.result()
                completed += 1
                
                if result['error'] is None and result['conclusions']:
                    output_data = {
                        'id': result['id'],
                        'question': result['question'].rstrip('; ').rstrip(';'),
                        'point': result['point'],
                        'conclusions': result['conclusions']
                    }
                    out_f.write(json.dumps(output_data, ensure_ascii=False) + '\n')
                else:
                    errors.append(f"{result['id']}: {result['error']}")
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def simple_rename_ids(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
        line_count = 0
        for line_num, line in enumerate(infile, 1):
            if not line.strip():
                continue
                
            try:
                data = json.loads(line.strip())
                new_id = f"g_{line_num:06d}"
                data['id'] = new_id
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                line_count += 1
            except json.JSONDecodeError:
                continue

def extract_and_generate_new_data(input_file, output_file):
    new_data_list = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
                
            try:
                data = json.loads(line.strip())
                original_id = data['id']
                question = data['question']
                point = data['point']
                conclusions = data['conclusions']
                
                if not conclusions:
                    continue
                
                selected_conclusion = None
                
                for con in reversed(conclusions):
                    if not con or not con.strip():
                        continue
                    
                    parts = con.split()
                    if not parts:
                        continue
                    
                    con_type = parts[0]
                    
                    if selected_conclusion is None:
                        selected_conclusion = con
                    
                    if con_type == 'coll':
                        selected_conclusion = con
                        break
                    elif con_type == 'cyclic' and selected_conclusion and not selected_conclusion.startswith('coll'):
                        selected_conclusion = con
                    elif con_type == 'cong' and selected_conclusion and not selected_conclusion.startswith(('coll', 'cyclic')):
                        selected_conclusion = con
                    elif con_type == 'perp' and selected_conclusion and not selected_conclusion.startswith(('coll', 'cyclic', 'cong')):
                        selected_conclusion = con
                    elif con_type == 'eqangle' and selected_conclusion and not selected_conclusion.startswith(('coll', 'cyclic', 'cong', 'perp')):
                        selected_conclusion = con
                    elif con_type == 'para' and selected_conclusion and not selected_conclusion.startswith(('coll', 'cyclic', 'cong', 'perp', 'eqangle')):
                        selected_conclusion = con
                    elif con_type == 'eqratio' and selected_conclusion and not selected_conclusion.startswith(('coll', 'cyclic', 'cong', 'perp', 'eqangle', 'para')):
                        selected_conclusion = con
                    elif con_type == 'midp' and selected_conclusion and not selected_conclusion.startswith(('coll', 'cyclic', 'cong', 'perp', 'eqangle', 'para', 'eqratio')):
                        selected_conclusion = con
                    elif con_type == 'simtri' and selected_conclusion and not selected_conclusion.startswith(('coll', 'cyclic', 'cong', 'perp', 'eqangle', 'para', 'eqratio', 'midp')):
                        selected_conclusion = con
                    elif con_type == 'contri' and selected_conclusion and not selected_conclusion.startswith(('coll', 'cyclic', 'cong', 'perp', 'eqangle', 'para', 'eqratio', 'midp', 'simtri')):
                        selected_conclusion = con
                
                if selected_conclusion is None and conclusions:
                    selected_conclusion = conclusions[-1]
                
                if selected_conclusion:
                    new_id = f"{original_id}"
                    new_data = {
                        'id': new_id,
                        'question': question,
                        'auxiliary': point,
                        'conclusion': selected_conclusion
                    }
                    new_data_list.append(new_data)
                    
            except:
                continue
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for data in new_data_list:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    return len(new_data_list), new_data_list


def convert_jsonl_to_txt(input_file, output_file):
    
    with open(input_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        
        for line in f_in:
            try:
                data = json.loads(line.strip())
                f_out.write(str(data.get('id', '')) + '\n')
                question = data.get('question', '')
                auxiliary = data.get('auxiliary', '')
                conclusion = data.get('conclusion', '')
                line_content = f"{question}; {auxiliary} ? {conclusion}\n"
                f_out.write(line_content)
            except json.JSONDecodeError:
                continue

def main():
    input_jsonl = "geo_constr_easy_con_agentic.jsonl"
    output_jsonl = "geo_constr_con_aux.jsonl"
    main_process(input_jsonl, output_jsonl)
    simple_rename_ids("geo_constr_con_aux.jsonl", "geo_constr_con_aux_id.jsonl")
    extract_and_generate_new_data("geo_constr_con_aux_id.jsonl", "geo_constr_aux_con.jsonl")
    convert_jsonl_to_txt("geo_constr_aux_con.jsonl","geo_constr_aux.txt" )
    

if __name__ == "__main__":
    main()
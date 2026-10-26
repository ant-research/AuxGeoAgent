import sys
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from absl import flags
import problem as pr
import graph as gh
import ddar

DEFINITIONS = None
RULES = None

def init_flags(problem_name, problems_file="geo_constr_easy.txt", mode="ddar"):
    flags.FLAGS.__dict__['__flags'].clear()
    
    flags.DEFINE_string(
        'problems_file',
        problems_file,
        'text file contains the problem strings.'
    )
    flags.DEFINE_string(
        'problem_name',
        problem_name,
        'name of the problem to solve.'
    )
    flags.DEFINE_string(
        'mode', mode, 'either `ddar` (DD+AR) or `alphageometry`'
    )
    flags.DEFINE_string(
        'defs_file',
        'defs.txt',
        'definitions of available constructions to state a problem.',
    )
    flags.DEFINE_string(
        'rules_file', 'rules.txt', 'list of deduction rules used by DD.'
    )
    flags.DEFINE_string(
        'out_file', '',
        'path to the solution output file.'
    )
    
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

def get_question_from_txt(problem_name, problems_file="geo_constr_easy.txt"):
    try:
        with open(problems_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line == problem_name:
                if i + 1 < len(lines):
                    return lines[i + 1].strip()
                else:
                    return None
        return None
    except Exception as e:
        print(f"Error reading question from txt file: {e}")
        return None

def get_problem_names_from_file(problems_file="geo_constr_easy.txt"):
    """从文件中读取所有问题名"""
    problem_names = []
    try:
        with open(problems_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i in range(0, len(lines), 2):
            if i < len(lines):
                problem_name = lines[i].strip()
                problem_names.append(problem_name)
        
        return problem_names
    except Exception as e:
        print(f"Error reading problem names from file: {e}")
        return []

def run_ddar_single(problem_name, problems_file="geo_constr_easy.txt"):
    try:
        question_text = get_question_from_txt(problem_name, problems_file)
        if question_text is None:
            return problem_name, None, None, None, f"Question text not found for {problem_name}"
        
        init_flags(problem_name, problems_file)
        
        problems = pr.Problem.from_txt_file(
            problems_file, 
            to_dict=True, 
            translate=False,
            target_name=problem_name
        )
        
        if problem_name not in problems:
            return problem_name, question_text, None, None, f"Problem {problem_name} not found"
        
        this_problem = problems[problem_name]
        
        g, _, success = gh.Graph.build_problem(this_problem, DEFINITIONS)
        if not success:
            return problem_name, question_text, None, None, "Failed to build graph"
        
        g, level_times, status, branches, all_added = ddar.solve(
            g, RULES, this_problem, max_level=8192
        )

        depth = len(level_times)
        
        con_added = []
        for dep in all_added:
            points = [p.name for p in dep.args]  
            con = f"{dep.name} {' '.join(points)}"
            con_added.append(con)
        
        return problem_name, question_text, con_added, depth, None
        
    except Exception as e:
        import traceback
        error_msg = f"Exception: {str(e)}\n{traceback.format_exc()}"
        return problem_name, None, None, None, error_msg

def main():
    print("Loading definitions and rules...")
    load_definitions_and_rules()
    print("Definitions and rules loaded.")
    
    problems_file = "geo_constr_easy.txt"
    problem_names = get_problem_names_from_file(problems_file)
    total = len(problem_names)
    
    if total == 0:
        print("No problems found in the file.")
        return
    
    completed = 0
    start_time = time.time()
    
    report_interval = 100
    errors_log = []
    
    output_file = "geo_constr_easy_con.jsonl"
    
    if not os.path.exists(output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("")
    
    print(f"Starting parallel processing with 32 workers...")
    print(f"Total problems: {total}")
    
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = {executor.submit(run_ddar_single, name): name for name in problem_names}
        
        for future in as_completed(futures):
            problem_name, question_text, con_added, depth, error = future.result()
            completed += 1
            
            if (
                con_added is not None
                and question_text is not None
                and depth is not None
            ):
                data = {
                    "id": problem_name,
                    "question": question_text,
                    "conclusions": con_added,
                    "depth": depth
                }
                with open(output_file, "a", encoding="utf-8") as f:
                    json_str = json.dumps(data, ensure_ascii=False)
                    f.write(json_str + "\n")
                                
            if completed % report_interval == 0 or completed == total:
                elapsed = time.time() - start_time
                speed = completed / elapsed if elapsed > 0 else 0
                eta = (total - completed) / speed if speed > 0 else 0
                
                sys.stdout.write(
                    f"\rProgress: {completed}/{total} "
                    f"({completed/total*100:.1f}%) | "
                    f"Speed: {speed:.2f} problems/sec | "
                    f"ETA: {eta/60:.1f} min | "
                    f"Errors: {len(errors_log)}"
                )
                sys.stdout.flush()
    
    total_time = time.time() - start_time
    print(f"\n\nProcessing completed!")
    print(f"Total time: {total_time:.2f} seconds ({total_time/3600:.2f} hours)")
    print(f"Average speed: {total / total_time:.2f} problems/sec")
    
    if errors_log:
        print(f"Encountered {len(errors_log)} errors. See errors.log for details.")
        print("First few errors:")
        for err in errors_log[:5]:
            print(f"  - {err}")
    else:
        print("No errors encountered.")

if __name__ == "__main__":
    main()
import json
import glob

def extract_add_clause(original_question, reduced_question):
    if not original_question or not reduced_question:
        return ""
    original_clauses = [c.strip() for c in original_question.split(';') if c.strip()]
    reduced_clauses = [c.strip() for c in reduced_question.split(';') if c.strip()]
    original_set = set(original_clauses)
    reduced_set = set(reduced_clauses)
    diff = original_set - reduced_set
    if len(diff) == 1:
        return list(diff)[0]
    elif len(diff) > 1:
        return list(diff)[0]
    else:
        return ""

def find_failed_items(jsonl_files):
    failed_items = []
    for file_path in jsonl_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        solution = data.get('solution', '')
                        if solution == "failed to solve":
                            failed_items.append(data)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            continue
    return failed_items

def load_txt_problems(txt_file):
    id_to_problem = {}
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
            for i in range(0, len(lines), 2):
                if i + 1 < len(lines):
                    id_line = lines[i]
                    problem_line = lines[i + 1]
                    id_to_problem[id_line] = problem_line
    except FileNotFoundError:
        pass
    return id_to_problem

def load_original_data(jsonl_file):
    id_to_data = {}
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    item_id = data.get('id', '')
                    if item_id:
                        id_to_data[item_id] = data
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass
    return id_to_data

def process_failed_items(failed_items, id_to_problem, id_to_original_data):
    results = []
    for item in failed_items:
        item_id = item.get('id', '')
        if not item_id:
            continue
        if item_id not in id_to_problem:
            continue
        problem_line = id_to_problem[item_id]
        if '?' in problem_line:
            question1 = problem_line.split('?')[0].strip()
        else:
            question1 = problem_line
        if '_' in item_id:
            parts = item_id.split('_')
            if len(parts) >= 2:
                original_id = '_'.join(parts[:-1])
            else:
                original_id = item_id
        else:
            original_id = item_id
        if original_id not in id_to_original_data:
            continue
        original_data = id_to_original_data[original_id]
        question2 = original_data.get('question', '')
        original_auxiliary = original_data.get('auxiliary', '')
        original_conclusion = original_data.get('conclusion', '')
        original_solution = original_data.get('solution', '')
        depth = original_data.get('depth', '')
        max_step = original_data.get('max_step', '')
        conclusion = original_conclusion
        solution = original_solution
        add_clause = extract_add_clause(question2, question1)
        if add_clause:
            if original_auxiliary:
                new_auxiliary = f"{add_clause}; {original_auxiliary}"
            else:
                new_auxiliary = add_clause
        else:
            new_auxiliary = original_auxiliary
        result = {
            "id": original_id,
            "problem": problem_line,
            "auxiliary": new_auxiliary,
            "question": question1,
            "conclusion": conclusion,
            "solution": solution,
            "depth": depth,
            "max_step": max_step
        }
        results.append(result)
    return results

import json

def merge_specific_files(file_list, output_path):
    if not file_list:
        return
    
    all_data = []
    
    for filepath in file_list:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            all_data.append(data)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            continue
        except Exception:
            continue

    renumbered_data = []
    for i, data in enumerate(all_data, 1):
        new_id = f"p_{i:05d}"
        if isinstance(data, dict):
            data['id'] = new_id
        else:
            data = {'id': new_id, 'data': data}
        renumbered_data.append(data)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for data in renumbered_data:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    return len(renumbered_data)



def main():
    jsonl_pattern = "geo_constr_aux_processed_minus1.jsonl"
    txt_file = "geo_constr_aux_processed_minus1.txt"
    original_jsonl = "geo_constr_aux_processed.jsonl"
    output_file = "geo_constr_aux_processed_minus1_failed.jsonl"
    
    jsonl_files = sorted(glob.glob(jsonl_pattern))
    failed_items = find_failed_items(jsonl_files)
    id_to_problem = load_txt_problems(txt_file)
    id_to_original_data = load_original_data(original_jsonl)
    results = process_failed_items(failed_items, id_to_problem, id_to_original_data)
    
    
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for result in results:
            f_out.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    jsonl_pattern2 = "geo_constr_aux_processed_minus2.jsonl"
    txt_file2 = "geo_constr_aux_processed_minus2.txt"
    original_jsonl2 = "geo_constr_aux_processed.jsonl"
    output_file2 = "geo_constr_aux_processed_minus2_failed.jsonl"
    
    jsonl_files2 = sorted(glob.glob(jsonl_pattern2))
    failed_items2 = find_failed_items(jsonl_files2)
    id_to_problem2 = load_txt_problems(txt_file2)
    id_to_original_data2 = load_original_data(original_jsonl2)
    results2 = process_failed_items(failed_items2, id_to_problem2, id_to_original_data2)
    
    
    with open(output_file2, 'w', encoding='utf-8') as f_out:
        for result in results2:
            f_out.write(json.dumps(result, ensure_ascii=False) + '\n')

    file_list = [
        output_file,
        output_file2
    ]
    output_path = "merged_all.jsonl"

    count = merge_specific_files(file_list, output_path)


if __name__ == "__main__":
    main()
import json
import re
import itertools

def merge_single_solution_file(solution_file, source_data_path, final_output_path):
    solutions_dict = {}
    
    with open(solution_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                if item.get('solution'):
                    solutions_dict[item['id']] = {
                        'solution': item['solution'],
                        'depth': item.get('depth', 0)
                    }
    
    matched_data = []
    solution_ids = set(solutions_dict.keys())
    
    with open(source_data_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                item = json.loads(line)
                item_id = item.get('id')
                if item_id in solution_ids:
                    item['solution'] = solutions_dict[item_id]['solution']
                    item['depth'] = solutions_dict[item_id]['depth']
                    matched_data.append(item)
    
    with open(final_output_path, 'w', encoding='utf-8') as out_f:
        for item in matched_data:
            out_f.write(json.dumps(item, ensure_ascii=False) + '\n')

import json
import re

def point_in_solution(point_upper, solution):
    pattern = re.compile(re.escape(point_upper))
    for match in pattern.finditer(solution):
        pos = match.end()
        if pos >= len(solution):
            return True
        next_char = solution[pos]
        if next_char.isalpha() and next_char.islower():
            continue
        return True
    return False

def process_question(question, solution):
    if not question or not solution:
        return question
    
    clauses = []
    for clause_str in question.split(';'):
        clause_str = clause_str.strip()
        if not clause_str:
            continue
        if '=' not in clause_str:
            continue
        left, right = clause_str.split('=', 1)
        left = left.strip()
        right = right.strip()
        new_points_raw = [p.strip() for p in left.split() if p.strip()]
        new_points = [p.upper() for p in new_points_raw]
        right_parts = right.split()
        used_points = right_parts[1:] if len(right_parts) > 1 else []
        clauses.append({
            'raw': clause_str,
            'new_points': new_points,
            'new_points_lower': new_points_raw,
            'used_points': used_points,
            'index': len(clauses)
        })
    
    point_to_used_in = {}
    for i, clause in enumerate(clauses):
        for used_point in clause['used_points']:
            if used_point not in point_to_used_in:
                point_to_used_in[used_point] = []
            point_to_used_in[used_point].append(i)
    
    keep_cache = {}
    
    def should_keep_clause(clause_idx, visited=None):
        if clause_idx in keep_cache:
            return keep_cache[clause_idx]
        if visited is None:
            visited = set()
        clause = clauses[clause_idx]
        if clause_idx in visited:
            keep_cache[clause_idx] = False
            return False
        visited.add(clause_idx)
        for point_upper in clause['new_points']:
            if point_in_solution(point_upper, solution):
                keep_cache[clause_idx] = True
                return True
        for point_lower in clause['new_points_lower']:
            if point_lower in point_to_used_in:
                for parent_idx in point_to_used_in[point_lower]:
                    if parent_idx == clause_idx:
                        continue
                    if should_keep_clause(parent_idx, visited.copy()):
                        keep_cache[clause_idx] = True
                        return True
        keep_cache[clause_idx] = False
        return False
    
    kept_clauses = []
    for i in range(len(clauses)):
        if should_keep_clause(i):
            kept_clauses.append(clauses[i]['raw'])
    
    return '; '.join(kept_clauses)

def process_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            try:
                data = json.loads(line.strip())
                question = data.get('question', '') + '; ' + data.get('auxiliary', '') 
                solution = data.get('solution', '')
                if question and solution:
                    processed_question = process_question(question, solution)
                    data['question'] = processed_question
                f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
            except json.JSONDecodeError:
                continue
            except Exception:
                continue

import json

def parse_clauses1(question):
    if not question:
        return []
    clauses = []
    raw_clauses = question.split(';')
    for i, clause_str in enumerate(raw_clauses):
        clause_str = clause_str.strip()
        if not clause_str:
            continue
        if '=' not in clause_str:
            continue
        left, right = clause_str.split('=', 1)
        left = left.strip()
        right = right.strip()
        new_points = [p.strip() for p in left.split() if p.strip()]
        right_parts = right.split()
        if not right_parts:
            continue
        used_points = right_parts[1:] if len(right_parts) > 1 else []
        clauses.append({
            'raw': clause_str,
            'new_points': new_points,
            'used_points': used_points,
            'index': i,
            'is_last': (i == len(raw_clauses) - 1)
        })
    return clauses

def extract_conclusion_points1(conclusion):
    if not conclusion:
        return set()
    parts = conclusion.strip().split()
    if len(parts) <= 1:
        return set()
    return set(parts[1:])

def find_isolated_clauses1(clauses, conclusion_points):
    all_used_points = {}
    for clause in clauses:
        for point in clause['used_points']:
            if point not in all_used_points:
                all_used_points[point] = []
            all_used_points[point].append(clause['index'])
    isolated_indices = []
    for clause in clauses:
        is_isolated = True
        for new_point in clause['new_points']:
            if new_point in all_used_points:
                user_indices = all_used_points[new_point]
                for user_idx in user_indices:
                    if user_idx != clause['index']:
                        is_isolated = False
                        break
            if new_point in conclusion_points:
                is_isolated = False
                break
            if not is_isolated:
                break
        if is_isolated:
            isolated_indices.append(clause['index'])
    return isolated_indices

def remove_clause_and_format1(question, clause_index):
    raw_clauses = question.split(';')
    new_clauses = []
    for i, clause_str in enumerate(raw_clauses):
        if i != clause_index:
            new_clauses.append(clause_str.strip())
    filtered_clauses = [c for c in new_clauses if c]
    return '; '.join(filtered_clauses)

def process_file1(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        for line_num, line in enumerate(f_in, 1):
            try:
                data = json.loads(line.strip())
                original_id = data.get('id', f'unknown_{line_num}')
                question = data.get('question', '')
                conclusion = data.get('conclusion', '')
                if not question or not conclusion:
                    continue
                clauses = parse_clauses1(question)
                if not clauses:
                    continue
                conclusion_points = extract_conclusion_points1(conclusion)
                isolated_indices = find_isolated_clauses1(clauses, conclusion_points)
                for i, clause_idx in enumerate(isolated_indices, 1):
                    new_question = remove_clause_and_format1(question, clause_idx)
                    id_str = f"{original_id}_{i}"
                    question_line = f"{new_question} ? {conclusion}"
                    f_out.write(f"{id_str}\n")
                    f_out.write(f"{question_line}\n")
            except json.JSONDecodeError:
                continue
            except Exception:
                continue

import json
import itertools

def parse_clauses2(question):
    if not question:
        return []
    clauses = []
    raw_clauses = question.split(';')
    for i, clause_str in enumerate(raw_clauses):
        clause_str = clause_str.strip()
        if not clause_str:
            continue
        if '=' not in clause_str:
            continue
        left, right = clause_str.split('=', 1)
        left = left.strip()
        right = right.strip()
        new_points = [p.strip() for p in left.split() if p.strip()]
        right_parts = right.split()
        if not right_parts:
            continue
        used_points = right_parts[1:] if len(right_parts) > 1 else []
        clauses.append({
            'raw': clause_str,
            'new_points': new_points,
            'used_points': used_points,
            'index': i
        })
    return clauses

def extract_conclusion_points2(conclusion):
    if not conclusion:
        return set()
    parts = conclusion.strip().split()
    if len(parts) <= 1:
        return set()
    return set(parts[1:])

def check_clause_pair_validity2(clauses, clause_indices_to_remove, conclusion_points):
    idx1, idx2 = clause_indices_to_remove
    points_to_remove = set()
    points_to_remove.update(clauses[idx1]['new_points'])
    points_to_remove.update(clauses[idx2]['new_points'])
    if points_to_remove.intersection(conclusion_points):
        return False
    remaining_clauses = [i for i in range(len(clauses)) if i not in (idx1, idx2)]
    for clause_idx in remaining_clauses:
        clause = clauses[clause_idx]
        if any(point in clause['used_points'] for point in points_to_remove):
            return False
    return True

def remove_clauses_and_format2(question, clause_indices):
    raw_clauses = question.split(';')
    new_clauses = []
    for i, clause_str in enumerate(raw_clauses):
        clause_str = clause_str.strip()
        if clause_str and i not in clause_indices:
            new_clauses.append(clause_str)
    return '; '.join(new_clauses)

def process_file2(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f_in, \
         open(output_path, 'w', encoding='utf-8') as f_out:
        for line_num, line in enumerate(f_in, 1):
            try:
                data = json.loads(line.strip())
                original_id = data.get('id', f'unknown_{line_num}')
                question = data.get('question', '')
                conclusion = data.get('conclusion', '')
                if not question or not conclusion:
                    continue
                clauses = parse_clauses2(question)
                if len(clauses) < 3:
                    continue
                conclusion_points = extract_conclusion_points2(conclusion)
                clause_indices = list(range(len(clauses)))
                valid_pairs = []
                for idx1, idx2 in itertools.combinations(clause_indices, 2):
                    if check_clause_pair_validity2(clauses, (idx1, idx2), conclusion_points):
                        valid_pairs.append((idx1, idx2))
                for i, (idx1, idx2) in enumerate(valid_pairs, 1):
                    new_question = remove_clauses_and_format2(question, [idx1, idx2])
                    id_str = f"{original_id}_{i}"
                    question_line = f"{new_question} ? {conclusion}"
                    f_out.write(f"{id_str}\n")
                    f_out.write(f"{question_line}\n")
            except json.JSONDecodeError:
                continue
            except Exception:
                continue


if __name__ == "__main__":
    input_path = "/dnn_training_sys/ljy.junyi/ag_generated/dataset/geo_constr_aux_merged18_filtered_processed.jsonl"
    output_path = "/dnn_training_sys/ljy.junyi/ag_generated/dataset/geo_constr_aux_merged18_minus1.txt"
    process_file(input_path, output_path)

def main():
    input_path = "solutions_geo_constr_aux.jsonl"
    source_data_path = "geo_constr_aux_con.jsonl"
    filtered_path = "geo_constr_aux_solu.jsonl"
    # filtered_path = "geo_constr_aux_filtered.jsonl"
    intermediate_path = "geo_constr_aux_processed.jsonl"
    output_minus1_path = "geo_constr_aux_processed_minus1.txt"
    output_minus2_path = "geo_constr_aux_processed_minus2.txt"

    merge_single_solution_file(input_path,source_data_path,filtered_path)

    process_file(filtered_path, intermediate_path)
    process_file1(intermediate_path, output_minus1_path)
    process_file2(intermediate_path, output_minus2_path)


if __name__ == "__main__":
    main()
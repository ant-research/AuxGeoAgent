import json
import subprocess
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from functools import partial

def extract_proof_steps_and_depth(output):
    if not output:
        return "", 0
    depth = 0
    depth_pattern = r"Depth\s+(\d+)/\d+"
    depth_matches = re.findall(depth_pattern, output)
    if depth_matches:
        try:
            depth = int(depth_matches[-1])
        except:
            depth = 0
    start_marker = "* Proof steps:"
    start_idx = output.find(start_marker)
    if start_idx == -1:
        return "", depth
    start_idx += len(start_marker)
    proof_section = output[start_idx:]
    end_marker = "======"
    end_idx = proof_section.find(end_marker)
    if end_idx == -1:
        return proof_section.strip(), depth
    else:
        return proof_section[:end_idx].strip(), depth

def run_alphageometry_single_with_retry(question_id, input_file, max_retries=5, timeout=900):
    retry_count = 0
    last_error = ""
    while retry_count < max_retries:
        try:
            cmd = f'python -m alphageometry --alsologtostderr --problems_file={input_file} --problem_name={question_id} --mode=ddar'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                combined_output = result.stdout + result.stderr
                return question_id, combined_output, result.returncode, retry_count
            else:
                retry_count += 1
                last_error = f"returncode={result.returncode}"
                if retry_count < max_retries:
                    time.sleep(1)
        except subprocess.TimeoutExpired:
            retry_count += 1
            last_error = "TIMEOUT"
            if retry_count < max_retries:
                time.sleep(1)
        except Exception as e:
            retry_count += 1
            last_error = f"ERROR: {e}"
            if retry_count < max_retries:
                time.sleep(1)
    return question_id, f"FAILED after {max_retries} retries, last error: {last_error}", -1, max_retries

def process_and_write_single_question(question_id, input_file, output_file, lock, stats):
    try:
        _, output, returncode, retry_count = run_alphageometry_single_with_retry(
            question_id, input_file, max_retries=5, timeout=900
        )
        solution, depth = extract_proof_steps_and_depth(output)
        if returncode != 0:
            result = {
                "id": question_id,
                "solution": "",
                "depth": 0,
                "returncode": returncode,
                "has_proof_steps": False,
                "retry_count": retry_count,
                "error": output if isinstance(output, str) and output.startswith("FAILED") else None
            }
        else:
            result = {
                "id": question_id,
                "solution": solution,
                "depth": depth,
                "returncode": returncode,
                "has_proof_steps": "* Proof steps:" in (output if isinstance(output, str) else ""),
                "retry_count": retry_count
            }
        with lock:
            with open(output_file, 'a', encoding='utf-8') as out_f:
                out_f.write(json.dumps(result, ensure_ascii=False) + '\n')
                out_f.flush()
        with lock:
            stats["processed"] += 1
            if returncode == 0:
                stats["success"] += 1
                if depth > 0:
                    stats["total_depth"] += depth
                    stats["depth_count"] += 1
            else:
                stats["failed"] += 1
            stats["total_retries"] += retry_count
        return True, question_id, returncode, len(solution), retry_count, depth
    except Exception as e:
        error_result = {
            "id": question_id,
            "solution": "",
            "depth": 0,
            "returncode": -3,
            "has_proof_steps": False,
            "error": str(e),
            "retry_count": 5
        }
        with lock:
            with open(output_file, 'a', encoding='utf-8') as out_f:
                out_f.write(json.dumps(error_result, ensure_ascii=False) + '\n')
                out_f.flush()
            stats["processed"] += 1
            stats["failed"] += 1
            stats["total_retries"] += 5
        return False, question_id, -3, 0, 5, 0

def stream_read_questions(input_file, batch_size=1000):
    current_batch = []
    with open(input_file, 'r', encoding='utf-8') as f:
        line_count = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line_count % 2 == 0:
                current_batch.append(line)
            line_count += 1
            if len(current_batch) >= batch_size:
                yield current_batch
                current_batch = []
        if current_batch:
            yield current_batch

def filter_solutions_file(input_jsonl_file, output_filtered_file):
    filtered_count = 0
    with open(input_jsonl_file, 'r', encoding='utf-8') as f_in, \
         open(output_filtered_file, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get("solution") and data.get("solution").strip():
                    f_out.write(line + '\n')
                    filtered_count += 1
            except:
                continue
    return filtered_count

def main_realtime_write(input_file, output_file):
    total_questions = 0
    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line and i % 2 == 0:
                total_questions += 1
    lock = Lock()
    stats = {
        "processed": 0,
        "success": 0,
        "failed": 0,
        "total_retries": 0,
        "total_depth": 0,
        "depth_count": 0
    }
    batch_size = 1000
    concurrent_workers = 8
    for batch_questions in stream_read_questions(input_file, batch_size):
        batch_size_actual = len(batch_questions)
        with ThreadPoolExecutor(max_workers=concurrent_workers) as executor:
            process_func = partial(
                process_and_write_single_question,
                input_file=input_file,
                output_file=output_file,
                lock=lock,
                stats=stats
            )
            future_to_id = {}
            for qid in batch_questions:
                future = executor.submit(process_func, qid)
                future_to_id[future] = qid
            completed_count = 0
            while completed_count < batch_size_actual:
                for future in list(future_to_id.keys()):
                    if future.done():
                        try:
                            future.result()
                        except:
                            pass
                        completed_count += 1
                        del future_to_id[future]
                time.sleep(0.1)
        import gc
        gc.collect()
        time.sleep(2)
    
    filtered_file = output_file.replace('.jsonl', '_filtered.jsonl')
    filtered_count = filter_solutions_file(output_file, filtered_file)
    os.remove(output_file)
    os.rename(filtered_file, output_file)

if __name__ == "__main__":
    input_file = "geo_constr_aux.txt"
    output_file = "solutions_geo_constr_aux.jsonl"
    main_realtime_write(input_file, output_file)
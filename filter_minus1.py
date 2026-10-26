import subprocess
import json
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from functools import partial

def extract_proof_steps_and_depth(output):
    if not output:
        return "", 0, False
    has_failed_to_solve = False
    if isinstance(output, str) and re.search(r'failed\s+to\s+solve', output, re.IGNORECASE):
        has_failed_to_solve = True
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
        return "", depth, has_failed_to_solve
    start_idx += len(start_marker)
    proof_section = output[start_idx:]
    end_marker = "======"
    end_idx = proof_section.find(end_marker)
    if end_idx == -1:
        return proof_section.strip(), depth, has_failed_to_solve
    else:
        return proof_section[:end_idx].strip(), depth, has_failed_to_solve

def run_alphageometry_single_with_retry(question_id, input_file, max_retries=5, timeout=900):
    retry_count = 0
    all_attempts = []
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
            combined_output = result.stdout + result.stderr
            attempt_result = {
                'retry_num': retry_count,
                'returncode': result.returncode,
                'output': combined_output,
                'timeout': False,
                'error': None
            }
            has_proof_steps = "* Proof steps:" in combined_output
            has_failed_to_solve = False
            if isinstance(combined_output, str):
                has_failed_to_solve = bool(re.search(r'failed\s+to\s+solve', combined_output, re.IGNORECASE))
            proof_steps, depth, _ = extract_proof_steps_and_depth(combined_output)
            attempt_result.update({
                'has_proof_steps': has_proof_steps,
                'has_failed_to_solve': has_failed_to_solve,
                'proof_steps': proof_steps,
                'depth': depth
            })
            all_attempts.append(attempt_result)
            if has_proof_steps and not has_failed_to_solve:
                return question_id, all_attempts, retry_count
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1)
        except subprocess.TimeoutExpired:
            attempt_result = {
                'retry_num': retry_count,
                'returncode': -2,
                'output': f"TIMEOUT after {timeout} seconds",
                'timeout': True,
                'error': 'timeout',
                'has_proof_steps': False,
                'has_failed_to_solve': False,
                'proof_steps': '',
                'depth': 0
            }
            all_attempts.append(attempt_result)
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1)
        except Exception as e:
            attempt_result = {
                'retry_num': retry_count,
                'returncode': -1,
                'output': f"ERROR: {e}",
                'timeout': False,
                'error': str(e),
                'has_proof_steps': False,
                'has_failed_to_solve': False,
                'proof_steps': '',
                'depth': 0
            }
            all_attempts.append(attempt_result)
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(1)
    return question_id, all_attempts, max_retries

def process_and_write_single_question(question_id, input_file, output_file, lock, stats):
    try:
        _, all_attempts, retry_count = run_alphageometry_single_with_retry(
            question_id, input_file, max_retries=5, timeout=900
        )
        final_result = analyze_attempts(all_attempts, question_id)
        final_result["retry_count"] = retry_count
        final_result["attempts"] = len(all_attempts)
        with lock:
            stats["processed"] += 1
            stats["total_retries"] += retry_count
            if final_result["status"] == "success":
                stats["success"] += 1
                if final_result["depth"] > 0:
                    stats["total_depth"] += final_result["depth"]
                    stats["depth_count"] += 1
            elif final_result["status"] == "failed_to_solve":
                stats["failed"] += 1
                stats["failed_to_solve_count"] = stats.get("failed_to_solve_count", 0) + 1
            elif final_result["status"] == "timeout":
                stats["failed"] += 1
                stats["timeout_count"] = stats.get("timeout_count", 0) + 1
            elif final_result["status"] == "error":
                stats["failed"] += 1
                stats["error_count"] = stats.get("error_count", 0) + 1
        with lock:
            with open(output_file, 'a', encoding='utf-8') as out_f:
                out_f.write(json.dumps(final_result, ensure_ascii=False) + '\n')
                out_f.flush()
        return True, question_id, final_result["status"], len(final_result["solution"]), retry_count, final_result["depth"]
    except Exception as e:
        error_result = {
            "id": question_id,
            "solution": "",
            "depth": 0,
            "status": "error",
            "error": str(e),
            "retry_count": 5,
            "attempts": 5
        }
        with lock:
            with open(output_file, 'a', encoding='utf-8') as out_f:
                out_f.write(json.dumps(error_result, ensure_ascii=False) + '\n')
                out_f.flush()
            stats["processed"] += 1
            stats["failed"] += 1
            stats["total_retries"] += 5
            stats["error_count"] = stats.get("error_count", 0) + 1
        return False, question_id, "error", 0, 5, 0

def analyze_attempts(all_attempts, question_id):
    successful_attempts = [a for a in all_attempts if a.get('has_proof_steps') and not a.get('has_failed_to_solve')]
    if successful_attempts:
        last_success = successful_attempts[-1]
        return {
            "id": question_id,
            "solution": last_success.get('proof_steps', ''),
            "depth": last_success.get('depth', 0),
            "status": "success",
            "has_proof_steps": True,
            "has_failed_to_solve": False,
            "final_attempt": last_success['retry_num']
        }
    all_failed_to_solve = all([a.get('has_failed_to_solve', False) for a in all_attempts])
    if all_failed_to_solve:
        last_attempt = all_attempts[-1]
        return {
            "id": question_id,
            "solution": "failed to solve",
            "depth": 0,
            "status": "failed_to_solve",
            "has_proof_steps": False,
            "has_failed_to_solve": True,
            "final_attempt": last_attempt['retry_num']
        }
    all_timeouts = all([a.get('timeout', False) for a in all_attempts])
    if all_timeouts:
        return {
            "id": question_id,
            "solution": "",
            "depth": 0,
            "status": "timeout",
            "has_proof_steps": False,
            "has_failed_to_solve": False,
            "final_attempt": all_attempts[-1]['retry_num']
        }
    return {
        "id": question_id,
        "solution": "",
        "depth": 0,
        "status": "error",
        "has_proof_steps": False,
        "has_failed_to_solve": False,
        "final_attempt": all_attempts[-1]['retry_num'],
        "error": all_attempts[-1].get('error', 'unknown error')
    }

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

def main_realtime_write():
    input_file = "geo_constr_aux_processed_minus1.txt"
    output_file = "geo_constr_aux_processed_minus1.jsonl"
    if not os.path.exists(input_file):
        return
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
        "depth_count": 0,
        "failed_to_solve_count": 0,
        "timeout_count": 0,
        "error_count": 0
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

if __name__ == "__main__":
    main_realtime_write()
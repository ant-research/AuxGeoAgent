import random
import re
import json
import time
import os
import sys
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import subprocess
from itertools import islice

OPENAI_URL = ""  #your url
API_KEY = ""  #your api key
MODEL = "gemini-2.5-pro"

class ConstructionCategory(Enum):
    BASIC = "BASIC"
    BASIC_FREE = "BASIC_FREE"
    TRAJECTORY = "TRAJECTORY"
    UNIQUE = "UNIQUE"

@dataclass
class ConstructionTemplate:
    left_side: str       
    name: str           
    right_params: str  
    category: ConstructionCategory
    weight: float = 1.0  
    
    def get_left_points(self) -> List[str]:
        return self.left_side.split()
    
    def get_right_template_points(self) -> List[str]:
        return self.right_params.split()
        

class GeometryProblemGenerator:
    def __init__(self):
        self.constructions = self._create_all_constructions()
        self.used_points = []  
        
    def _create_all_constructions(self) -> Dict[ConstructionCategory, List[ConstructionTemplate]]:
        constructions = {
            ConstructionCategory.BASIC: [],
            ConstructionCategory.BASIC_FREE: [],
            ConstructionCategory.TRAJECTORY: [],
            ConstructionCategory.UNIQUE: []
        }
        

        trajectory_templates = [
            ("x", "on_line", "x a b", ConstructionCategory.TRAJECTORY, 27.0),
            ("x", "on_circle", "x o a", ConstructionCategory.TRAJECTORY, 13.0),
            ("x", "on_tline", "x a b c", ConstructionCategory.TRAJECTORY, 6.0),
            ("x", "on_bline", "x a b", ConstructionCategory.TRAJECTORY, 2.5),
            ("x", "on_pline", "x a b c", ConstructionCategory.TRAJECTORY, 2.0),
            ("x", "on_aline", "x a b c d e", ConstructionCategory.TRAJECTORY, 1.0),
            ("x", "on_dia", "x a b", ConstructionCategory.TRAJECTORY, 0.3),
            ("x", "on_circum", "x a b c", ConstructionCategory.TRAJECTORY, 2.0),
            ("x", "angle_bisector", "x a b c", ConstructionCategory.TRAJECTORY, 0.8),
            ("x", "eqdistance", "x a b c", ConstructionCategory.TRAJECTORY, 0.4),
            ("x", "eqangle3", "x a b d e f", ConstructionCategory.TRAJECTORY, 0.2),
        ]

        unique_templates = [
            ("x", "circumcenter", "x a b c", ConstructionCategory.UNIQUE, 11.0),
            ("x", "foot", "x a b c", ConstructionCategory.UNIQUE, 7.0),
            ("x", "midpoint", "x a b", ConstructionCategory.UNIQUE, 5.0),
            ("x", "incenter", "x a b c", ConstructionCategory.UNIQUE, 3.0),
            ("x", "orthocenter", "x a b c", ConstructionCategory.UNIQUE, 2.0),
            ("x", "mirror", "x a b", ConstructionCategory.UNIQUE, 1.0),
            ("x", "excenter", "x a b c", ConstructionCategory.UNIQUE, 0.8),
            ("x y z i", "centroid", "x y z i a b c", ConstructionCategory.UNIQUE, 0.4),
            ("a b c x", "parallelogram", "a b c x", ConstructionCategory.UNIQUE, 0.3),
            ("x", "segment", "a b", ConstructionCategory.UNIQUE, 0.2),
            ("x", "reflect", "x a b c", ConstructionCategory.UNIQUE, 2.0),
            ("x", "angle_mirror", "x a b c", ConstructionCategory.UNIQUE, 0.5),
            ("x", "circle", "x a b c", ConstructionCategory.UNIQUE, 0.5),
            ("x", "intersection_ll", "x a b c d", ConstructionCategory.UNIQUE, 0.3),
            ("x", "intersection_lp", "x a b c m n", ConstructionCategory.UNIQUE, 0.1),
            ("x", "intersection_lt", "x a b c d e", ConstructionCategory.UNIQUE, 0.1),
            ("x", "intersection_tt", "x a b c d e f", ConstructionCategory.UNIQUE, 0.1),
            ("x", "intersection_cc", "x o w a", ConstructionCategory.UNIQUE, 0.1),
            ("x", "intersection_lc", "x a o b", ConstructionCategory.UNIQUE, 0.2),
            ("x", "intersection_pp", "x a b c d e f", ConstructionCategory.UNIQUE, 0.1),
            ("x", "nsquare", "x a b", ConstructionCategory.UNIQUE, 0.1),
            ("x", "psquare", "x a b", ConstructionCategory.UNIQUE, 0.1),
            ("x", "shift", "x b c d", ConstructionCategory.UNIQUE, 0.1),
            ("x y z i", "ninepoints", "x y z i a b c", ConstructionCategory.UNIQUE, 0.05),
            ("x y", "trisect", "x y a b c", ConstructionCategory.UNIQUE, 0.1),
            ("x y", "trisegment", "x y a b", ConstructionCategory.UNIQUE, 0.1),
            ("x y", "cc_tangent0", "x y o a w b", ConstructionCategory.UNIQUE, 0.1),
            ("x y", "cc_tangent", "x y z i o a w b", ConstructionCategory.UNIQUE, 0.05),
            ("x y", "tangent", "x y a o b", ConstructionCategory.UNIQUE, 0.2),
            ("x y z i", "2l1c", "x y z i a b c o", ConstructionCategory.UNIQUE, 0.05),
            ("x y", "e5128", "x y a b c d", ConstructionCategory.UNIQUE, 0.1),
            ("x y z", "3peq", "x y z a b c", ConstructionCategory.UNIQUE, 0.1),
            ("x y z i", "incenter2", "x y z i a b c", ConstructionCategory.UNIQUE, 0.2),
            ("x y z i", "excenter2", "x y z i a b c", ConstructionCategory.UNIQUE, 0.1),
        ]

        basic_templates = [
            ("a b c", "triangle", "a b c", ConstructionCategory.BASIC, 6.0),
            ("a b c", "iso_triangle", "a b c", ConstructionCategory.BASIC, 0.2),
            ("a b c", "r_triangle", "a b c", ConstructionCategory.BASIC, 0.1),
            ("a b c", "risos", "a b c", ConstructionCategory.BASIC, 0.1),
            ("a b c", "ieq_triangle", "a b c", ConstructionCategory.BASIC, 0.1),
            ("a b c d", "quadrangle", "a b c d", ConstructionCategory.BASIC, 0.1),
            ("a b c d", "eq_trapezoid", "a b c d", ConstructionCategory.BASIC, 0.1),
            ("a b c d", "eq_quadrangle", "a b c d", ConstructionCategory.BASIC, 0.05),
            ("a b c d", "eqdia_quadrangle", "a b c d", ConstructionCategory.BASIC, 0.03),
            ("a b c d", "r_trapezoid", "a b c d", ConstructionCategory.BASIC, 0.03),
            ("a b c d e", "pentagon", "a b c d e", ConstructionCategory.BASIC, 0.02),
        ]

        basic_free_templates = [
            ("a", "free", "a", ConstructionCategory.BASIC_FREE, 0.7),
        ]
        
        for templates, category in [
            (basic_templates, ConstructionCategory.BASIC),
            (basic_free_templates, ConstructionCategory.BASIC_FREE),
            (trajectory_templates, ConstructionCategory.TRAJECTORY),
            (unique_templates, ConstructionCategory.UNIQUE)
        ]:
            for left, name, right, cat, weight in templates:
                constructions[cat].append(ConstructionTemplate(left, name, right, cat, weight))
        
        return constructions
    
    def _weighted_choice(self, templates: List[ConstructionTemplate]) -> ConstructionTemplate:
        weights = [t.weight for t in templates]
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        r = random.random()
        cumulative = 0.0
        
        for template, weight in zip(templates, normalized_weights):
            cumulative += weight
            if r <= cumulative:
                return template
        
        return templates[-1]
    
    def _get_new_letter(self) -> str:
        letters = [chr(ord('a') + i) for i in range(26)]
        for letter in letters:
            if letter not in self.used_points:
                return letter
        i = 0
        while True:
            name = f"p{i}"
            if name not in self.used_points:
                return name
            i += 1


import requests
import time
import re
import threading

class GeminiAnalyzer:
    
    def __init__(self, api_key=None, base_url=None, 
                 geometry_generator=None,
                 knowledge_file="auxiliary_knowledge_en.txt",
                 model="gemini-2.5-pro"):
        
        self.geometry_generator = geometry_generator
        self.analysis_history = []
        self.knowledge_file = knowledge_file
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        
        self.lock = threading.Lock()
        
        self.geometric_knowledge = self._load_geometric_knowledge()
        print(f"Loaded geometric auxiliary knowledge ({len(self.geometric_knowledge)} characters)")
        
        self._initialize_construction_templates()
        
        print("GeminiAnalyzer initialized with Gemini-2.5pro and geometric knowledge")

    def _load_geometric_knowledge(self):
        with open(self.knowledge_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _initialize_construction_templates(self):
        if self.geometry_generator:
            self.construction_templates = self._extract_construction_templates()

    def _extract_construction_templates(self):
        templates_info = {}
        
        for category, templates in self.geometry_generator.constructions.items():
            category_templates = []
            for template in templates:
                info = f"{template.name}: {template.left_side} = {template.name} {template.right_params} ({category.value})"
                category_templates.append(info)
            templates_info[category.value] = category_templates
        
        return templates_info

    def _get_trajectory_templates_list(self):
        if self.geometry_generator:
            templates = []
            for template in self.geometry_generator.constructions.get(ConstructionCategory.TRAJECTORY, []):
                templates.append(f"{template.left_side} = {template.name} {template.right_params}")
            return "\n".join(templates[:])
        else:
            trajectory_templates = self.construction_templates.get("TRAJECTORY", [])
            return "\n".join(trajectory_templates[:])
    
    def _get_unique_templates_list(self):
        if self.geometry_generator:
            templates = []
            for template in self.geometry_generator.constructions.get(ConstructionCategory.UNIQUE, []):
                templates.append(f"{template.left_side} = {template.name} {template.right_params}")
            return "\n".join(templates[:])
        else:
            unique_templates = self.construction_templates.get("UNIQUE", [])
            return "\n".join(unique_templates[:])
    
    def _create_analysis_prompt(self, current_problem, conclusions, analysis_result, current_depth):
        
        points_list = analysis_result['points']
        constructions_list = analysis_result['constructions']
        
        construction_types = {}
        for constr in constructions_list:
            ctype = constr['type']
            construction_types[ctype] = construction_types.get(ctype, 0) + 1
        
        construction_stats = "\n".join([f"- {ctype}: {count} times" 
                                       for ctype, count in construction_types.items()])
        
        history_text = ""
        if self.analysis_history:
            history_text = "\n\nPrevious Analysis Reports:\n"
            for i, (step, analysis) in enumerate(self.analysis_history[-2:]):
                history_text += f"Step {step}:\n{analysis[:]}...\n{'-'*40}\n"
        
        prompt = f"""You are an expert in geometric reasoning. Your task is to analyze the current geometric configuration and suggest potential auxiliary points.

Current Construction Commands:
{current_problem}

Current Geometric Points: {', '.join(points_list)}

Construction Types Used:
{construction_stats}

Current Deductive Depth:
{current_depth}

Current Derived Geometric Relations (Conclusions, first 60):
{chr(10).join(conclusions[:60])}

{history_text}

Geometric Auxiliary Point Knowledge Reference:
{self.geometric_knowledge}

Analysis Task:
Write a detailed analysis report including:

1. Describe the current geometric configuration:
   - What geometric objects exist (points, lines, circles, triangles, etc.)
   - What relationships have been derived (collinearity, congruence, perpendicularity, etc.)
   - What patterns or symmetries can be observed
   - The overall structure of the geometric configuration

2. Based on the geometric knowledge reference, suggest 2-3 potential directions for adding new auxiliary points:
   - Identify which geometric conditions from the knowledge reference apply to the current configuration
   - Suggest possible types of auxiliary points that could reveal new relationships
   - Consider both standard constructions and creative possibilities
   - Focus on points that could help derive more conclusions

Important Guidelines:
- DO NOT provide specific construction commands or formal notation
- DO suggest general ideas like "add a point on the circumcircle" or "create a symmetric point"
- Base suggestions on the geometric knowledge, but adapt to the specific configuration
- Maintain geometric reasoning, not just pattern matching
- Each suggestion should explain WHY that auxiliary point might be useful

Your analysis report should first describe the configuration, then provide suggestions:"""
        
        return prompt
    
    def _create_generation_prompt(self, analysis_report, current_problem, analysis_result):
        
        points_list = analysis_result['points']
        used_points = set(points_list)
        
        all_letters = [chr(ord('a') + i) for i in range(26)]
        available_new_points = [p for p in all_letters if p not in used_points]
        
        trajectory_options = self._get_trajectory_templates_list()
        unique_options = self._get_unique_templates_list()
        
        prompt = f"""Based on the geometric analysis, generate construction command(s).

FULL ANALYSIS REPORT:
{analysis_report}

Current Problem:
{current_problem}

Current Points: {', '.join(points_list)}
Available new point letters: {', '.join(available_new_points[:10])}

IMPORTANT RULES:
1. LEFT side points (before '='): Use NEW letters from available list
2. RIGHT side points (after construction name): Use ONLY existing points from the current points list above
3. Choose constructions that make geometric sense for THIS specific configuration
4. Base your choice on the analysis report, not just standard templates
5. Use ACTUAL points from this problem, not template letters like a,b,c

Available Construction Templates:

TRAJECTORY constructions:
{trajectory_options}

UNIQUE constructions:
{unique_options}

Examples showing how points work:
Template: x = midpoint x a b
Actual: p = midpoint p a b  (p is new, a,b are existing points from this problem)

Template: x y = trisect x y a b c  
Actual: p q = trisect p q a b c  (p,q are new, a,b,c are existing points from this problem)

Template: x = on_line x a b, on_circle x o a
Actual: p = on_line p a b, on_circle p o a  (p is new, a,b,o are existing points from this problem)

CRITICAL OUTPUT FORMAT REQUIREMENTS:
1. Your response must START with the construction command(s)
2. Output ONLY the construction command(s), no analysis, no explanation
3. Use exactly one of these formats:
   - For single unique: [new_point] = [construction] [new_point] [existing_point1] [existing_point2] ...
   - For single TRAJECTORY: [new_point] = [construction] [new_point] [existing_point1] [existing_point2] ...
   - For two TRAJECTORY: [new_point] = [construction1] [points1], [construction2] [points2]
4. Do NOT include any other text before or after the construction commands

Generate exactly and only the construction command(s) in the required format:"""
        
        return prompt

    def _call_gemini_api(self, prompt, process_id=0):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 8192,
            "temperature": 0.1
        }
        
        attempt = 0
        while True:
            attempt += 1
            try:
                time.sleep(attempt * 0.5)
                
                with self.lock:
                    print(f"  [GeminiAnalyzer] API call attempt {attempt}...")
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=180
                )
                
                if response.status_code == 200:
                    result = response.json()
                    with self.lock:
                        print(f"  [GeminiAnalyzer] Attempt {attempt} successful")
                    return result["choices"][0]["message"]["content"]
                else:
                    with self.lock:
                        print(f"  [GeminiAnalyzer] API error: {response.status_code} (attempt {attempt})")
                    
                    if response.status_code == 429:
                        wait = 30 + attempt * 5
                    elif response.status_code >= 500:
                        wait = 20
                    else:
                        wait = 10
                    
                    with self.lock:
                        print(f"  [GeminiAnalyzer] Waiting {wait} seconds before retry...")
                    time.sleep(wait)
                    
            except requests.exceptions.Timeout:
                with self.lock:
                    print(f"  [GeminiAnalyzer] Request timeout (attempt {attempt}), waiting 20 seconds before retry...")
                time.sleep(20)
            except Exception as e:
                with self.lock:
                    print(f"  [GeminiAnalyzer] API exception: {e} (attempt {attempt}), waiting 10 seconds before retry...")
                time.sleep(10)

    def _call_model(self, prompt, process_id=0):
        try:
            start_time = time.time()
            response = self._call_gemini_api(prompt, process_id)
            elapsed_time = time.time() - start_time
            print(f"API response time: {elapsed_time:.2f} seconds")
            return response
        except Exception as e:
            print(f"API call failed: {e}")
            return "Analysis completed. Please retry the construction generation."

    def _parse_construction_commands(self, response):
        commands = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            line = re.sub(r'^\d+[\.\)]\s*', '', line)
            line = re.sub(r'^[•\-*]\s*', '', line)
            line = re.sub(r'^[Oo]ption\s+[A-Z]:\s*', '', line)
            line = re.sub(r'^[Ee]xample\s+\d+:\s*', '', line)
            
            if '=' in line:
                if ',' in line:
                    left_part, right_part = line.split('=', 1)
                    left_part = left_part.strip()
                    right_part = right_part.strip()
                    
                    construction_parts = [p.strip() for p in right_part.split(',')]
                    
                    left_tokens = left_part.split()
                    left_valid = all(len(p) == 1 and p.isalpha() and p.islower() for p in left_tokens)
                    
                    if not left_valid or len(left_tokens) < 1:
                        continue
                    
                    all_right_valid = True
                    for part in construction_parts:
                        part_tokens = part.split()
                        if len(part_tokens) < 2:
                            all_right_valid = False
                            break
                        
                        for token in part_tokens[1:]:
                            clean_token = token.strip(',')
                            if len(clean_token) != 1 or not clean_token.isalpha() or not clean_token.islower():
                                all_right_valid = False
                                break
                        
                        if not all_right_valid:
                            break
                    
                    if left_valid and all_right_valid:
                        commands.append(line)
                        
                else:
                    left, right = line.split('=', 1)
                    left_tokens = left.strip().split()
                    right_tokens = right.strip().split()
                    
                    if len(left_tokens) >= 1 and len(right_tokens) >= 2:
                        left_valid = all(len(p) == 1 and p.isalpha() and p.islower() for p in left_tokens)
                        right_valid = all(len(p) == 1 and p.isalpha() and p.islower() for p in right_tokens[1:])
                        
                        if left_valid and right_valid:
                            commands.append(line)
        
        return commands[:2]
    
    def generate_constructions(self, analysis_report, current_problem, analysis_result):
        print("\n[Generation phase] Generating construction commands based on analysis report...")
        
        try:
            generation_prompt = self._create_generation_prompt(analysis_report, current_problem, analysis_result)
            print("Generation prompt:")
            print(generation_prompt[:500] + "..." if len(generation_prompt) > 500 else generation_prompt)
            
            generation_response = self._call_model(generation_prompt)
            print("Generation response:")
            print(generation_response)
            
            commands = self._parse_construction_commands(generation_response)
            
            if not commands:
                print("⚠ No valid construction commands parsed")
                return []
            
            print(f"\n✓ Generated {len(commands)} construction commands:")
            for i, cmd in enumerate(commands, 1):
                print(f"  {i}. {cmd}")
            
            return commands
            
        except Exception as e:
            print(f"Failed to generate construction commands: {e}")
            return []
    
    def analyze_problem(self, current_problem, conclusions, analysis_result, current_depth, step):
        print(f"\n[Step {step}] Geometric problem analysis (with auxiliary point knowledge reference)...")
        
        analysis_prompt = self._create_analysis_prompt(current_problem, conclusions, analysis_result,  current_depth)
        
        try:
            analysis_response = self._call_model(analysis_prompt)
            
            self.analysis_history.append((step, analysis_response))
            
            print(f"✓ Analysis completed, report length: {len(analysis_response)} characters")
            return analysis_response
            
        except Exception as e:
            print(f"Analysis failed: {e}")
            raise e
    
    def clear_history(self):
        self.analysis_history.clear()


class DDARRunner:
    
    def __init__(self, defs_file='defs.txt', rules_file='rules.txt'):
        sys.path.append('..')
        
        from absl import flags
        import problem as pr
        import graph as gh
        import ddar
        
        self.flags = flags
        self.pr = pr
        self.gh = gh
        self.ddar = ddar
        
        self.definitions = pr.Definition.from_txt_file(defs_file, to_dict=True)
        self.rules = pr.Theorem.from_txt_file(rules_file, to_dict=True)
    
    def init_flags(self, problem_name, problem_text):
        temp_file = f"temp_{problem_name}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(f"{problem_name}\n")
            f.write(f"{problem_text}\n")
        
        self.flags.FLAGS.__dict__['__flags'].clear()
        
        self.flags.DEFINE_string('problems_file', temp_file, 'text file contains the problem strings.')
        self.flags.DEFINE_string('problem_name', problem_name, 'name of the problem to solve.')
        self.flags.DEFINE_string('mode', 'ddar', 'either ddar (DD+AR) or alphageometry')
        self.flags.DEFINE_string('defs_file', 'defs.txt', 'definitions of available constructions.')
        self.flags.DEFINE_string('rules_file', 'rules.txt', 'list of deduction rules used by DD.')
        self.flags.DEFINE_string('out_file', '', 'path to the solution output file.')
        
        self.flags.FLAGS.problems_file = temp_file
        self.flags.FLAGS.problem_name = problem_name
        self.flags.FLAGS.mode = 'ddar'
        self.flags.FLAGS.defs_file = 'defs.txt'
        self.flags.FLAGS.rules_file = 'rules.txt'
        self.flags.FLAGS.out_file = ''
        
        return temp_file
    
    def run_ddar(self, problem_text: str, problem_name: str = "current_problem") -> Tuple[Optional[int], Optional[List[str]], str]:
        try:
            temp_file = self.init_flags(problem_name, problem_text)
            
            problems = self.pr.Problem.from_txt_file(
                temp_file,
                to_dict=True,
                translate=False,
                target_name=problem_name
            )
            
            if problem_name not in problems:
                return None, None, f"Problem {problem_name} not found"
            
            this_problem = problems[problem_name]
            
            g, _, success = self.gh.Graph.build_problem(this_problem, self.definitions)
            if not success:
                return None, None, "Failed to build graph"
            
            g, level_times, status, branches, all_added = self.ddar.solve(
                g, self.rules, this_problem, max_level=1000
            )
            
            con_added = []
            for dep in all_added:
                points = [p.name for p in dep.args]
                con = f"{dep.name} {' '.join(points)}"
                con_added.append(con)
            
            try:
                os.remove(temp_file)
            except:
                pass
                
            return len(level_times), con_added, ""
            
        except Exception as e:
            import traceback
            error_msg = f"Exception: {str(e)}\n{traceback.format_exc()}"
            return None, None, error_msg

def analyze_problem_structure(problem: str) -> Dict[str, Any]:
    points = set()
    constructions = []
    
    for cmd in problem.split(';'):
        cmd = cmd.strip()
        if not cmd:
            continue
        
        if '=' in cmd:
            left, right = cmd.split('=', 1)
            left_points = left.strip().split()
            right_parts = right.strip().split()
            
            for p in left_points:
                if len(p) == 1 and p.isalpha():
                    points.add(p)
            
            if len(right_parts) > 1:
                for p in right_parts[1:]:
                    if len(p) == 1 and p.isalpha():
                        points.add(p)
            
            if right_parts:
                constr_type = right_parts[0]
                constr_points = right_parts[1:]
                constructions.append({
                    'type': constr_type,
                    'points': constr_points,
                    'new_points': left_points
                })
    
    return {
        'points': sorted(list(points)),
        'constructions': constructions,
        'num_constructions': len(constructions)
    }

def extract_existing_points(problem_text: str) -> List[str]:
    points = set()
    for cmd in problem_text.split(';'):
        cmd = cmd.strip()
        if cmd and '=' in cmd:
            left, right = cmd.split('=', 1)
            for part in [left.strip(), right.strip()]:
                for p in part.split():
                    if len(p) == 1 and p.isalpha() and p.islower():
                        points.add(p)
    return sorted(list(points))

def is_construction_valid(new_construction: str, existing_points: List[str], current_problem: str) -> bool:
    if not new_construction or '=' not in new_construction:
        print(f"❌ Construction command format error: missing equal sign or empty")
        return False
    
    try:
        left_part, right_part = new_construction.split('=', 1)
        left_points = left_part.strip().split()
        right_part = right_part.strip()
        
        for point in left_points:
            if point in existing_points:
                print(f"❌ Left point {point} already exists")
                return False
            if len(point) != 1 or not point.islower() or not point.isalpha():
                print(f"❌ Left point {point} format error")
                return False
        
        all_current_points = set(existing_points) | set(left_points)
        
        if ',' in right_part:
            construction_parts = [p.strip() for p in right_part.split(',')]
            for part in construction_parts:
                part_tokens = part.split()
                if len(part_tokens) < 2:
                    print(f"❌ Construction part format error: {part}")
                    return False
                
                for token in part_tokens[1:]:
                    if token not in all_current_points:
                        print(f"❌ Point {token} in construction {part} is not existing or newly defined")
                        print(f"   Available points: {sorted(all_current_points)}")
                        return False
        else:
            right_tokens = right_part.split()
            if len(right_tokens) < 2:
                print(f"❌ Construction format error: right part too short: {new_construction}")
                return False
            
            for token in right_tokens[1:]:
                if token not in all_current_points:
                    print(f"❌ Point {token} is not existing or newly defined")
                    print(f"   Available points: {sorted(all_current_points)}")
                    return False
        
        for cmd in current_problem.split(';'):
            cmd = cmd.strip()
            if cmd and '=' in cmd:
                existing_left, existing_right = cmd.split('=', 1)
                existing_right = existing_right.strip()
                
                if existing_right == right_part:
                    print(f"❌ Construction duplicate: similar construction already exists {cmd}")
                    return False
        
        return True
    except Exception as e:
        print(f"❌ Error parsing construction command: {e}")
        import traceback
        traceback.print_exc()
        return False


def main_with_ddar_corrected(input_jsonl: str, output_jsonl: str):

    generator = GeometryProblemGenerator()
    analyzer = GeminiAnalyzer(
        api_key=API_KEY, 
        base_url=OPENAI_URL,
        model=MODEL,
        geometry_generator=generator,
        knowledge_file="auxiliary_knowledge_en.txt"
    )
    
    ddar_runner = DDARRunner(defs_file='defs.txt', rules_file='rules.txt')
    
    total_count = 0
    success_count = 0
    failed_count = 0
    constructions_added_history = []
    
    with open(input_jsonl, 'r', encoding='utf-8') as infile, \
         open(output_jsonl, 'w', encoding='utf-8') as outfile:
        
        start_line = 1
        
        for i, line in enumerate(islice(infile, start_line - 1, None), start=start_line):
            analyzer.clear_history()
            problem = json.loads(line.strip())
            problem_text = problem.get('question', '')
            
            current_problem = problem_text
            current_conclusions = problem.get('conclusions', [])
            current_depth = problem.get('depth')
            
            if not problem_text:
                problem['auxiliary'] = ""
                problem['final_question'] = current_problem
                problem['final_conclusions'] = current_conclusions
                problem['constructions_added'] = 0
                problem['total_attempts'] = 0
                problem['status'] = 'empty'
                outfile.write(json.dumps(problem, ensure_ascii=False) + '\n')
                continue
            
            total_count += 1
            
            existing_points = extract_existing_points(current_problem)
            
            constructions_added = 0
            total_attempts = 0
            max_constructions = 3
            max_attempts = 10
            auxiliary_commands = []
            
            while constructions_added < max_constructions and total_attempts < max_attempts:
                total_attempts += 1
                
                try:
                    analysis_result = analyze_problem_structure(current_problem)
                    
                    analysis = analyzer.analyze_problem(current_problem, current_conclusions, analysis_result, current_depth=current_depth,
                    step=total_attempts)
                    commands = analyzer.generate_constructions(analysis, current_problem, analysis_result)

                    if not commands:

                        continue
                    
                    is_all_valid = True
                    invalid_reason = ""
                    for cmd in commands:
                        if not is_construction_valid(cmd, existing_points,current_problem):
                            is_all_valid = False
                            invalid_reason = f"construction command format error: {cmd}"
                            break
                    
                    if not is_all_valid:
                        
                        continue
                    
                    new_auxiliary = '; '.join(commands)
                    
                    new_problem = current_problem + ('; ' + new_auxiliary if current_problem else new_auxiliary)
                    
                    new_depth, new_conclusions, error = ddar_runner.run_ddar(
                        new_problem, f"problem_{i}_attempt_{total_attempts}"
                    )
                    
                    if new_depth is None and not new_conclusions:
                        
                        continue
                    
                    old_set = set(current_conclusions or [])
                    new_set = set(new_conclusions or [])
                    new_conclusions_count = len(new_set - old_set)

                    depth_improved = (
                    current_depth is not None
                    and new_depth is not None
                    and new_depth > current_depth)

                    
                    if depth_improved or new_conclusions_count > 0:
                        constructions_added += 1
                        auxiliary_commands.extend(commands)
                        
                        current_problem = new_problem
                        
                        if new_conclusions:
                            current_conclusions = new_conclusions

                        if new_depth is not None:
                            current_depth = new_depth
                        
                        existing_points = extract_existing_points(current_problem)
                    
                except Exception as e:
                    pass
                

            final_auxiliary = '; '.join(auxiliary_commands) if auxiliary_commands else ""
            problem['auxiliary'] = final_auxiliary
            problem['final_question'] = current_problem
            problem['final_conclusions'] = current_conclusions
            problem['final_depth'] = current_depth
            problem['constructions_added'] = constructions_added
            problem['total_attempts'] = total_attempts
            problem['status'] = 'success' if constructions_added > 0 else 'failed'
            
            if constructions_added > 0:
                success_count += 1
            else:
                failed_count += 1
                
            constructions_added_history.append(constructions_added)
            
            outfile.write(json.dumps(problem, ensure_ascii=False) + '\n')
            outfile.flush()

if __name__ == "__main__":
    main_with_ddar_corrected(
        input_jsonl="geo_constr_easy_con.jsonl",
        output_jsonl="geo_constr_easy_con_agentic.jsonl"
    )
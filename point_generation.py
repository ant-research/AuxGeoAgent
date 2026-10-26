import random
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import copy

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
    
    def _get_distance_based_probability(self, point_index: int, total_points: int) -> float:
        distance_from_end = total_points - 1 - point_index
        
        if distance_from_end == 0:
            return 0.4
        elif distance_from_end == 1:
            return 0.25
        elif distance_from_end == 2:
            return 0.15
        elif distance_from_end == 3:
            return 0.08
        elif distance_from_end == 4:
            return 0.05
        else:
            decay_factor = 0.7
            base_prob = 0.03 * (decay_factor ** (distance_from_end - 4))
            return max(base_prob, 0.001)
    
    def _select_point_with_distance_bias(self, available_points: List[str], recent_points: List[str] = None) -> str:
        if not available_points:
            return None
            
        weights = []
        total_points = len(available_points)
        
        for i, point in enumerate(available_points):
            base_weight = self._get_distance_based_probability(i, total_points)
            
            is_recent = (recent_points and point in recent_points)
            if is_recent:
                distance_from_end = total_points - 1 - i
                recent_bonus = 0.3 * (1.0 / (distance_from_end + 1))
                base_weight += recent_bonus
            
            weights.append(base_weight)
        
        total_weight = sum(weights)
        if total_weight > 0:
            normalized_weights = [w / total_weight for w in weights]
        else:
            normalized_weights = [1.0 / len(available_points)] * len(available_points)
        
        r = random.random()
        cumulative = 0.0
        
        for point, weight in zip(available_points, normalized_weights):
            cumulative += weight
            if r <= cumulative:
                return point
        
        return available_points[-1]
    
    def generate_similar_command(self, original_command: str, used_points: List[str], 
                                available_points_for_right: List[str] = None) -> str:
        parts = original_command.split('=')
        if len(parts) != 2:
            return original_command
            
        left_side = parts[0].strip()
        right_side = parts[1].strip()
        
        right_parts = right_side.split()
        if not right_parts:
            return original_command
            
        construction_name = right_parts[0]
        original_right_points = right_parts[1:]
        
        num_points_to_change = random.randint(1, min(2, len(original_right_points)))
        
        positions_to_change = random.sample(range(len(original_right_points)), num_points_to_change)
        
        if available_points_for_right is None:
            available_points_for_right = used_points.copy()
        
        recent_points = []
        if available_points_for_right:
            recent_points = available_points_for_right[-min(3, len(available_points_for_right)):]
        
        new_right_points = original_right_points.copy()
        
        for pos in positions_to_change:
            current_point = original_right_points[pos]
            
            available_filtered = [p for p in available_points_for_right if p != current_point]
            
            if self.name == "on_tline":
                if pos == 2:
                    b_pos = 1
                    if b_pos < len(original_right_points):
                        b_point = original_right_points[b_pos]
                        available_filtered = [p for p in available_filtered if p != b_point]
            
            elif self.name == "on_aline":
                if pos == 1:
                    a_pos = 0
                    if a_pos < len(original_right_points):
                        a_point = original_right_points[a_pos]
                        available_filtered = [p for p in available_filtered if p != a_point]
                elif pos >= 2:
                    cde_positions = [2, 3, 4]
                    for other_pos in cde_positions:
                        if other_pos != pos and other_pos < len(original_right_points):
                            other_point = original_right_points[other_pos]
                            if other_point in available_filtered:
                                available_filtered.remove(other_point)
            
            elif self.name == "eqangle3":
                if pos == 1:
                    a_pos = 0
                    if a_pos < len(original_right_points):
                        a_point = original_right_points[a_pos]
                        available_filtered = [p for p in available_filtered if p != a_point]
                elif pos >= 2:
                    def_positions = [2, 3, 4]
                    for other_pos in def_positions:
                        if other_pos != pos and other_pos < len(original_right_points):
                            other_point = original_right_points[other_pos]
                            if other_point in available_filtered:
                                available_filtered.remove(other_point)
            
            if available_filtered:
                new_point = self._select_point_with_distance_bias(available_filtered, recent_points)
                new_right_points[pos] = new_point
        
        new_right_side = f"{construction_name} {' '.join(new_right_points)}"
        return f"{left_side} = {new_right_side}"
    
    def generate_command(self, new_points_map: Dict[str, str], used_points: List[str], 
                        available_points_for_right: List[str] = None) -> str:
        left_points = self.get_left_points()
        right_template = self.get_right_template_points()
        
        actual_points = {}
        
        for i, template_point in enumerate(left_points):
            if template_point in new_points_map:
                actual_points[template_point] = new_points_map[template_point]
            else:
                new_letter = self._get_new_letter(used_points)
                actual_points[template_point] = new_letter
                used_points.append(new_letter)
        
        if available_points_for_right is None:
            available_points_for_right = used_points.copy()
        
        if not available_points_for_right:
            available_points_for_right = used_points.copy()
        
        recent_points = []
        if available_points_for_right:
            recent_points = available_points_for_right[-min(3, len(available_points_for_right)):]
        
        for i, template_point in enumerate(right_template):
            if template_point not in actual_points:
                if available_points_for_right:
                    if self.name == "on_tline":
                        if i == 2:
                            b_template = right_template[1]
                            if b_template in actual_points:
                                b_point = actual_points[b_template]
                                available_filtered = [p for p in available_points_for_right 
                                                    if p != b_point]
                                if available_filtered:
                                    chosen_point = self._select_point_with_distance_bias(available_filtered, recent_points)
                                else:
                                    new_point = self._get_new_letter(used_points)
                                    used_points.append(new_point)
                                    chosen_point = new_point
                            else:
                                chosen_point = self._select_point_with_distance_bias(available_points_for_right, recent_points)
                        else:
                            chosen_point = self._select_point_with_distance_bias(available_points_for_right, recent_points)
                    
                    elif self.name == "on_aline":
                        if i == 1:
                            a_template = right_template[0]
                            if a_template in actual_points:
                                a_point = actual_points[a_template]
                                available_filtered = [p for p in available_points_for_right 
                                                    if p != a_point]
                                if available_filtered:
                                    chosen_point = self._select_point_with_distance_bias(available_filtered, recent_points)
                                else:
                                    new_point = self._get_new_letter(used_points)
                                    used_points.append(new_point)
                                    chosen_point = new_point
                            else:
                                chosen_point = self._select_point_with_distance_bias(available_points_for_right, recent_points)
                        
                        elif i >= 2:
                            assigned_cde = []
                            for idx in [2, 3, 4]:
                                if idx < i:
                                    other_template = right_template[idx]
                                    if other_template in actual_points:
                                        assigned_cde.append(actual_points[other_template])
                            
                            if assigned_cde:
                                available_filtered = [p for p in available_points_for_right 
                                                    if p not in assigned_cde]
                                if available_filtered:
                                    chosen_point = self._select_point_with_distance_bias(available_filtered, recent_points)
                                else:
                                    new_point = self._get_new_letter(used_points)
                                    used_points.append(new_point)
                                    chosen_point = new_point
                            else:
                                chosen_point = self._select_point_with_distance_bias(available_points_for_right, recent_points)
                        else:
                            chosen_point = self._select_point_with_distance_bias(available_points_for_right, recent_points)
                    
                    elif self.name == "eqangle3":
                        if i == 1:
                            a_template = right_template[0]
                            if a_template in actual_points:
                                a_point = actual_points[a_template]
                                available_filtered = [p for p in available_points_for_right 
                                                    if p != a_point]
                                if available_filtered:
                                    chosen_point = self._select_point_with_distance_bias(available_filtered, recent_points)
                                else:
                                    new_point = self._get_new_letter(used_points)
                                    used_points.append(new_point)
                                    chosen_point = new_point
                            else:
                                chosen_point = self._select_point_with_distance_bias(available_points_for_right, recent_points)
                        
                        elif i >= 2:
                            assigned_def = []
                            for idx in [2, 3, 4]:
                                if idx < i:
                                    other_template = right_template[idx]
                                    if other_template in actual_points:
                                        assigned_def.append(actual_points[other_template])
                            
                            if assigned_def:
                                available_filtered = [p for p in available_points_for_right 
                                                    if p not in assigned_def]
                                if available_filtered:
                                    chosen_point = self._select_point_with_distance_bias(available_filtered, recent_points)
                                else:
                                    new_point = self._get_new_letter(used_points)
                                    used_points.append(new_point)
                                    chosen_point = new_point
                            else:
                                chosen_point = self._select_point_with_distance_bias(available_points_for_right, recent_points)
                        else:
                            chosen_point = self._select_point_with_distance_bias(available_points_for_right, recent_points)
                    
                    else:
                        assigned_points = []
                        for j in range(len(right_template)):
                            if j != i and right_template[j] in actual_points:
                                if right_template[j] != template_point:
                                    assigned_points.append(actual_points[right_template[j]])
                        
                        if assigned_points:
                            available_filtered = [p for p in available_points_for_right 
                                                if p not in assigned_points]
                            
                            if available_filtered:
                                chosen_point = self._select_point_with_distance_bias(available_filtered, recent_points)
                            else:
                                new_point = self._get_new_letter(used_points)
                                used_points.append(new_point)
                                chosen_point = new_point
                        else:
                            chosen_point = self._select_point_with_distance_bias(available_points_for_right, recent_points)
                    
                    actual_points[template_point] = chosen_point
        
        actual_left = ' '.join([actual_points[p] for p in left_points])
        actual_right_points = [actual_points[p] for p in right_template]
        actual_right = f"{self.name} {' '.join(actual_right_points)}"
        
        return f"{actual_left} = {actual_right}"
    
    def _get_new_letter(self, used_points: List[str]) -> str:
        letters = [chr(ord('a') + i) for i in range(26)]
        for letter in letters:
            if letter not in used_points:
                return letter
        i = 0
        while True:
            name = f"p{i}"
            if name not in used_points:
                return name
            i += 1

class GeometryProblemGenerator:
    def __init__(self):
        self.constructions = self._create_all_constructions()
        self.used_points = set()
        
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
            ("a b", "segment", "a b", ConstructionCategory.UNIQUE, 0.2),
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
    
    def _sample_basic(self) -> str:
        basic_cons = self.constructions[ConstructionCategory.BASIC]
        template = self._weighted_choice(basic_cons)
        
        left_points = template.get_left_points()
        new_points_map = {}
        
        for template_point in left_points:
            new_letter = self._get_new_letter()
            new_points_map[template_point] = new_letter
            self.used_points.append(new_letter)
        
        command = template.generate_command(new_points_map, self.used_points)
        return command
    
    def _sample_basic_free_single(self) -> str:
        basic_free_cons = self.constructions[ConstructionCategory.BASIC_FREE]
        template = self._weighted_choice(basic_free_cons)
        
        left_points = template.get_left_points()
        new_points_map = {}
        
        for template_point in left_points:
            new_letter = self._get_new_letter()
            new_points_map[template_point] = new_letter
            self.used_points.append(new_letter)
        
        return template.generate_command(new_points_map, self.used_points)
    
    def _sample_two_trajectory_connected(self) -> str:
        trajectory_cons = self.constructions[ConstructionCategory.TRAJECTORY]
        
        if len(trajectory_cons) < 2:
            template = self._weighted_choice(trajectory_cons)
            cons1 = template
            cons2 = template
        else:
            cons1 = self._weighted_choice(trajectory_cons)
            remaining = [c for c in trajectory_cons if c.name != cons1.name]
            if remaining:
                cons2 = self._weighted_choice(remaining)
            else:
                cons2 = cons1
        
        new_point_x = self._get_new_letter()
        self.used_points.append(new_point_x)
        
        new_points_map1 = {"x": new_point_x}
        new_points_map2 = {"x": new_point_x}
        
        available_points = [p for p in self.used_points if p != new_point_x] 
        
        cmd1_full = cons1.generate_command(new_points_map1, self.used_points, available_points)
        cmd2_full = cons2.generate_command(new_points_map2, self.used_points, available_points)
        
        right1 = cmd1_full.split('=', 1)[1].strip()
        right2 = cmd2_full.split('=', 1)[1].strip()
        
        return f"{new_point_x} = {right1}, {right2}"
    
    def _sample_one_unique(self) -> str:
        unique_cons = self.constructions[ConstructionCategory.UNIQUE]
        template = self._weighted_choice(unique_cons)
        
        left_points = template.get_left_points()
        new_points_map = {}
        
        for template_point in left_points:
            new_letter = self._get_new_letter()
            new_points_map[template_point] = new_letter
            self.used_points.append(new_letter)
        
        left_new_points = set(new_points_map.values())
        available_points = [p for p in self.used_points if p not in left_new_points]
        
        return template.generate_command(new_points_map, self.used_points, available_points)
    
    def _sample_stage3_single_operation(self) -> List[str]:
        commands = []
        
        if random.random() < 0.5:
            main_command = self._sample_two_trajectory_connected()
        else:
            main_command = self._sample_one_unique()
        
        commands.append(main_command)
        
        if random.random() < 0.2:
            parts = main_command.split('=')
            if len(parts) == 2:
                left_side = parts[0].strip()
                right_side = parts[1].strip()
                
                if ',' in right_side:
                    first_constr = right_side.split(',')[0].strip()
                    right_parts = first_constr.split()
                else:
                    right_parts = right_side.split()
                
                if right_parts:
                    construction_name = right_parts[0]
                    original_right_points = right_parts[1:]
                    
                    num_right_points = len(original_right_points)
                    
                    if num_right_points == 2:
                        num_points_to_change = 1
                    else:
                        num_points_to_change = random.randint(1, min(2, num_right_points))
                    
                    template = None
                    for category in [ConstructionCategory.TRAJECTORY, ConstructionCategory.UNIQUE]:
                        for t in self.constructions[category]:
                            if t.name == construction_name:
                                template = t
                                break
                        if template:
                            break
                    
                    if template:
                        main_left_points = left_side.split()
                        
                        all_points_before = set(self.used_points.copy())
                        
                        new_left_point = self._get_new_letter()
                        self.used_points.append(new_left_point)
                        
                        available_points = [p for p in all_points_before if p not in main_left_points]
                        
                        new_points_map = {}
                        left_template_points = template.get_left_points()
                        
                        for i, template_point in enumerate(left_template_points):
                            if i == 0:
                                new_points_map[template_point] = new_left_point
                            else:
                                if available_points:
                                    chosen_point = template._select_point_with_distance_bias(available_points)
                                    new_points_map[template_point] = chosen_point
                        
                        similar_command = template.generate_command(new_points_map, self.used_points, available_points)
                        commands.append(similar_command)
        
        return commands
    
    def _sample_stage3(self) -> List[str]:
        commands = []
        num_operations = random.randint(2, 4)
        
        for _ in range(num_operations):
            operation_commands = self._sample_stage3_single_operation()
            commands.extend(operation_commands)
        
        return commands
    
    def _sample_stage23_loop(self) -> List[str]:
        commands = []
        
        stage3_commands = self._sample_stage3()
        commands.extend(stage3_commands)
        
        return commands
    
    def generate_problem(self) -> str:
        self.used_points = []
        all_commands = []
        
        stage1_command = self._sample_basic()
        all_commands.append(stage1_command)
        
        num_free_points = random.randint(1, 2)
        for _ in range(num_free_points):
            free_command = self._sample_basic_free_single()
            all_commands.append(free_command)
        
        num_main_loops = random.randint(2, 4)
        
        for _ in range(num_main_loops):
            loop_commands = self._sample_stage23_loop()
            all_commands.extend(loop_commands)
        
        return '; '.join(all_commands)
    
    def generate_multiple_problems(self, count: int = 100000) -> List[str]:
        problems = []
        
        for i in range(count):
            problems.append(self.generate_problem())
        
        return problems


def main():
    filename = "geo_constr_easy.txt" 
    generator = GeometryProblemGenerator()
    
    problems = generator.generate_multiple_problems(30000)
   
    with open(filename, 'w', encoding='utf-8') as f:
        for i, problem in enumerate(problems):
            problem_id = f"g_{i:06d}"
            f.write(f"{problem_id}\n")
            f.write(f"{problem}\n")

if __name__ == "__main__":
    main()
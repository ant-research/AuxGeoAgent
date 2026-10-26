
constructions_dict = {
    "BASIC": {
        "segment": {"format": "a b = segment a b", "description": "Let $AB$ be a line segment"},
        "triangle": {"format": "a b c = triangle a b c", "description": "Let $ABC$ be a triangle"},
        "rectangle": {"format": "a b c d = rectangle a b c d", "description": "Let $ABCD$ be a rectangle"},
        "pentagon": {"format": "a b c d e = pentagon a b c d e", "description": "Let $ABCDE$ be a pentagon"},
        "quadrangle": {"format": "a b c d = quadrangle a b c d", "description": "Let $ABCD$ be a quadrilateral"},
        "eq_quadrangle": {"format": "a b c d = eq_quadrangle a b c d", "description": "Let $ABCD$ be a quadrilateral with $DA = BC$"},
        "eq_trapezoid": {"format": "a b c d = eq_trapezoid a b c d", "description": "Let $ABCD$ be an isosceles trapezoid with $DC \\parallel AB$ and $DA = BC$"},
        "eqdia_quadrangle": {"format": "a b c d = eqdia_quadrangle a b c d", "description": "Let $ABCD$ be a quadrilateral with $DB = AC$"},
        "iso_triangle": {"format": "a b c = iso_triangle a b c", "description": "Let $ABC$ be an isosceles triangle with $AB = AC$"},
        "r_trapezoid": {"format": "a b c d = r_trapezoid a b c d", "description": "Let $ABCD$ be a right trapezoid with $AB \\parallel CD$ and $AB \\perp AD$"},
        "r_triangle": {"format": "a b c = r_triangle a b c", "description": "Let $ABC$ be a right triangle with $AB \\perp AC$"},
        "risos": {"format": "a b c = risos a b c", "description": "Let $ABC$ be a right isosceles triangle with $AB \\perp AC$ and $AB = AC$"},
        "ieq_triangle": {"format": "a b c = ieq_triangle a b c", "description": "Let $ABC$ be an equilateral triangle with $AB = BC = CA$"}
    },
    
    "BASIC_FREE": {
        "free": {"format": "a = free a", "description": "Let $A$ be an arbitrary point"}
    },

    "TRAJECTORY": {
        "angle_bisector": {"format": "x = angle_bisector x a b c", "description": "Let $X$ be a point on the angle bisector of $\\angle ABC$"},
        "eqangle2": {"format": "x = eqangle2 x a b c", "description": "Let $X$ be a point such that $\\angle ABX = \\angle CXB$"},
        "eqdistance": {"format": "x = eqdistance x a b c", "description": "Let $X$ be a point such that $XA = BC$"},
        "on_aline": {"format": "x = on_aline x a b c d e", "description": "Let $X$ be a point such that $\\angle XAB = \\angle CDE$"},
        "on_aline2": {"format": "x = on_aline2 x a b c d e", "description": "Let $X$ be a point such that $\\angle AXB = \\angle CDE$"},
        "on_bline": {"format": "x = on_bline x a b", "description": "Let $X$ be a point on the perpendicular bisector of $AB$"},
        "on_circle": {"format": "x = on_circle x o a", "description": "Let $X$ be a point on the circle with center $O$ and radius $OA$"},
        "on_line": {"format": "x = on_line x a b", "description": "Let $X$ be a point on line $AB$"},
        "on_pline": {"format": "x = on_pline x a b c", "description": "Let $X$ be a point on line through $A$ parallel to $BC$"},
        "on_tline": {"format": "x = on_tline x a b c", "description": "Let $X$ be a point on line through $A$ perpendicular to $BC$"},
        "on_dia": {"format": "x = on_dia x a b", "description": "Let $X$ be a point on the circle with diameter $AB$"},
        "on_opline": {"format": "x = on_opline x a b", "description": "Let $X$ be a point on line $AB$"},
        "eqangle3": {"format": "x = eqangle3 x a b d e f", "description": "Let $X$ be a point such that $\\angle AXB = \\angle EDF$"},
        "on_circum": {"format": "x = on_circum x a b c", "description": "Let $X$ be a point on the circumcircle of $\\triangle ABC$"}
    },
 
    "UNIQUE": {
        "angle_mirror": {"format": "x = angle_mirror x a b c", "description": "Point $X$ satisfies $\\angle ABC = \\angle XBC$"},
        "circle": {"format": "x = circle x a b c", "description": "Point $X$ is the center of the circle through $A$, $B$, $C$"},
        "circumcenter": {"format": "x = circumcenter x a b c", "description": "Point $X$ is the circumcenter of $\\triangle ABC$"},
        "foot": {"format": "x = foot x a b c", "description": "Point $X$ is the foot of the perpendicular from $A$ to line $BC$"},
        "incenter": {"format": "x = incenter x a b c", "description": "Point $X$ is the incenter of $\\triangle ABC$"},
        "excenter": {"format": "x = excenter x a b c", "description": "Point $X$ is an excenter of $\\triangle ABC$"},
        "intersection_ll": {"format": "x = intersection_ll x a b c d", "description": "Point $X$ is the intersection of lines $AB$ and $CD$"},
        "intersection_lp": {"format": "x = intersection_lp x a b c m n", "description": "Point $X$ is the intersection of line $AB$ and the line through $C$ parallel to $MN$"},
        "intersection_lt": {"format": "x = intersection_lt x a b c d e", "description": "Point $X$ is the intersection of line $AB$ and the line through $C$ perpendicular to $DE$"},
        "intersection_tt": {"format": "x = intersection_tt x a b c d e f", "description": "Point $X$ is the intersection of the line through $A$ perpendicular to $BC$ and the line through $D$ perpendicular to $EF$"},
        "intersection_cc": {"format": "x = intersection_cc x o w a", "description": "Point $X$ is an intersection point of circles with centers $O$ and $W$ both passing through point $A$"},
        "intersection_lc": {"format": "x = intersection_lc x a o b", "description": "Point $X$ is the intersection of line $AB$ and circle with center $O$ passing through $B$"},
        "intersection_pp": {"format": "x = intersection_pp x a b c d e f", "description": "Point $X$ is the intersection of the line through $A$ parallel to $BC$ and the line through $D$ parallel to $EF$"},
        "midpoint": {"format": "x = midpoint x a b", "description": "Point $X$ is the midpoint of segment $AB$"},
        "mirror": {"format": "x = mirror x a b", "description": "Point $X$ is the reflection of $A$ across $B$"},
        "nsquare": {"format": "x = nsquare x a b", "description": "Points $A$, $B$, $X$ are three vertices of a square with $\\angle ABX = 90^\\circ$ and $AB = BX$"},
        "orthocenter": {"format": "x = orthocenter x a b c", "description": "Point $X$ is the orthocenter of $\\triangle ABC$"},
        "parallelogram": {"format": "parallelogram a b c x", "description": "Points $A$, $B$, $C$, $X$ form a parallelogram"},
        "psquare": {"format": "x = psquare x a b", "description": "Points $A$, $B$, $X$ are three vertices of a square with $XA \\perp AB$ and $XA = AB$"},
        "reflect": {"format": "x = reflect x a b c", "description": "Point $X$ is the reflection of $A$ across line $BC$"},
        "shift": {"format": "x = shift x b c d", "description": "Point $X$ satisfies $XB = CD$ and $XC = BD$"},
        "ninepoints": {"format": "x y z i = ninepoints x y z i a b c", "description": "$X$, $Y$, $Z$ are midpoints of sides $BC$, $CA$, $AB$ respectively, and $I$ is the center of the nine-point circle of $\\triangle ABC$"},
        "trisect": {"format": "x y = trisect x y a b c", "description": "Points $X$ and $Y$ on $AC$ trisect $\\angle ABC$"},
        "trisegment": {"format": "x y = trisegment x y a b", "description": "Points $X$ and $Y$ on $AB$ trisect segment $AB$"},
        "cc_tangent0": {"format": "x y = cc_tangent0 x y o a w b", "description": "Points $X$ and $Y$ are tangency points of a common tangent line to circles $(O, OA)$ and $(W, WB)$"},
        "cc_tangent": {"format": "x y z i = cc_tangent x y z i o a w b", "description": "Points $X$, $Y$, $Z$, $I$ are tangency points of two common tangent lines to circles $(O, OA)$ and $(W, WB)$"},
        "tangent": {"format": "x y = tangent x y a o b", "description": "Points $X$ and $Y$ are tangency points of two tangent lines from $A$ to circle with center $O$ through $B$"},
        "2l1c": {"format": "x y z i = 2l1c x y z i a b c o", "description": "Points $X$ on $AC$, $Y$ on $BC$, $Z$ with $OA = OZ$, and $I$ on line $OZ$ such that $IX = IY = IZ$, $IX \\perp AC$, $IY \\perp BC$"},
        "e5128": {"format": "x y = e5128 x y a b c d", "description": "Point $X$ with $CB = CX$, and $Y$ is the intersection of $AB$ and $XD$, such that $\\angle ABD = \\angle XAY$"},
        "3peq": {"format": "x y z = 3peq x y z a b c", "description": "Points $Z$ on $BC$, $X$ on $AB$, $Y$ on $AC$ such that $X$, $Y$, $Z$ are collinear and $ZX = ZY$"},
        "incenter2": {"format": "x y z i = incenter2 x y z i a b c", "description": "Points $X$, $Y$, $Z$ are feet of perpendiculars from incenter $I$ to sides $BC$, $CA$, $AB$ of $\\triangle ABC$"},
        "excenter2": {"format": "x y z i = excenter2 x y z i a b c", "description": "Points $X$, $Y$, $Z$ are feet of perpendiculars from excenter $I$ to extended sides $BC$, $CA$, $AB$ of $\\triangle ABC$"},
        "centroid": {"format": "x y z i = centroid x y z i a b c", "description": "Points $X$, $Y$, $Z$ are midpoints of sides $BC$, $CA$, $AB$ respectively, and $I$ is the centroid of $\\triangle ABC$"}
    }
}

conclusion_commands = {
    "cong": {"format": "cong a b c d", "description": "segment $AB$ equals segment $CD$"},
    "coll": {"format": "coll a b c", "description": "points $A$, $B$, $C$ are collinear"},
    "perp": {"format": "perp a b c d", "description": "line $AB$ is perpendicular to line $CD$"},
    "para": {"format": "para a b c d", "description": "line $AB$ is parallel to line $CD$"},
    "eqangle": {"format": "eqangle a b a d x a x y", "description": "angle $\\angle BAD$ equals angle $\\angle XAY$"},
    "cyclic": {"format": "cyclic a b c d", "description": "points $A$, $B$, $C$, $D$ are concyclic"},
    "eqratio": {"format": "eqratio a b c d e f g h", "description": "ratio $AB/CD$ equals ratio $EF/GH$"},
    "contri": {"format": "contri a b c d e f", "description": "triangle $\\triangle ABC$ is congruent to triangle $\\triangle DEF$"},
    "simtri": {"format": "simtri a b c d e f", "description": "triangle $\\triangle ABC$ is similar to triangle $\\triangle DEF$"}
}
import json
import re

def get_command_from_dict(command, constructions_dict):
    if command in constructions_dict:
        return constructions_dict[command]
    
    if isinstance(constructions_dict, dict):
        for category in constructions_dict.values():
            if isinstance(category, dict) and command in category:
                return category[command]
    
    return None

def replace_points_with_caps_independent(statement, description, command_data):
    if not command_data or "format" not in command_data:
        return description
    
    statement_parts = statement.split('=')
    if len(statement_parts) != 2:
        return description
    
    left_var = statement_parts[0].strip()
    right_side = statement_parts[1].strip()
    
    right_parts_list = right_side.split()
    if not right_parts_list:
        return description
    
    actual_parameters = right_parts_list[1:]
    
    format_string = command_data["format"]
    format_parts_list = format_string.split('=')
    if len(format_parts_list) != 2:
        return description
    
    format_left_var = format_parts_list[0].strip()
    format_right_side = format_parts_list[1].strip()
    
    format_right_parts_list = format_right_side.split()
    if len(format_right_parts_list) < 2:
        return description
    
    format_parameters = format_right_parts_list[1:]
    
    mapping_dict = {}
    mapping_dict[format_left_var] = left_var
    
    for idx, format_var in enumerate(format_parameters):
        if idx < len(actual_parameters):
            mapping_dict[format_var] = actual_parameters[idx]
    
    result_text = description
    
    for match_obj in re.finditer(r'\$([^$]+)\$', result_text):
        content_inside = match_obj.group(1)
        
        new_chars_list = []
        char_index = 0
        
        while char_index < len(content_inside):
            current_char = content_inside[char_index]
            
            if current_char == '\\':
                start_idx = char_index
                while char_index < len(content_inside) and (content_inside[char_index].isalpha() or content_inside[char_index] == '\\'):
                    char_index += 1
                new_chars_list.append(content_inside[start_idx:char_index])
            elif 'A' <= current_char <= 'Z':
                lower_case = current_char.lower()
                if lower_case in mapping_dict:
                    new_chars_list.append(mapping_dict[lower_case].upper())
                else:
                    new_chars_list.append(current_char)
                char_index += 1
            else:
                new_chars_list.append(current_char)
                char_index += 1
        
        new_content = ''.join(new_chars_list)
        result_text = result_text.replace(f'${content_inside}$', f'${new_content}$', 1)
    
    return result_text

def symbolic_to_english_question_independent(symbolic_text):
    def process_single_construction(full_statement, command_word, command_info):
        if not command_info or "description" not in command_info:
            return full_statement
        
        return replace_points_with_caps_independent(full_statement, command_info["description"], command_info)
    
    statement_list = [s.strip() for s in symbolic_text.split(';') if s.strip()]
    english_parts_list = []
    
    for stmt in statement_list:
        if '=' not in stmt:
            english_parts_list.append(stmt)
            continue
        
        left_part, right_part = stmt.split('=', 1)
        left_var = left_part.strip()
        right_part = right_part.strip()
        
        construction_list = [c.strip() for c in right_part.split(',')]
        
        description_list = []
        for constr in construction_list:
            constr_parts = constr.split()
            if not constr_parts:
                continue
            
            cmd = constr_parts[0]
            full_stmt = f"{left_var} = {constr}"
            
            cmd_data = get_command_from_dict(cmd, constructions_dict)
            if cmd_data and "description" in cmd_data:
                desc = process_single_construction(full_stmt, cmd, cmd_data)
                description_list.append(desc)
            else:
                description_list.append(full_stmt)
        
        if not description_list:
            english_parts_list.append(stmt)
        elif len(description_list) == 1:
            english_parts_list.append(description_list[0])
        elif len(description_list) == 2:
            desc1 = description_list[0].rstrip('.')
            desc2 = description_list[1].rstrip('.')
            english_parts_list.append(f"{desc1} and {desc2}.")
        else:
            desc_strings = [d.rstrip('.') for d in description_list]
            combined_desc = ', '.join(desc_strings[:-1]) + ', and ' + desc_strings[-1] + '.'
            english_parts_list.append(combined_desc)
    
    if not english_parts_list:
        return ""
    
    final_parts = []
    for part in english_parts_list:
        part = part.strip()
        if not part.endswith('.'):
            part += '.'
        final_parts.append(part)
    
    return ' '.join(final_parts)

def conclusion_to_english_independent(conclusion_text):
    if not conclusion_text:
        return ""
    
    conclusion_text = conclusion_text.strip().strip(';')
    words = conclusion_text.split()
    if not words:
        return ""
    
    cmd_word = words[0]
    param_list = words[1:]
    
    if cmd_word not in conclusion_commands:
        return conclusion_text
    
    cmd_info = conclusion_commands[cmd_word]
    fmt_str = cmd_info["format"]
    desc_text = cmd_info["description"]
    
    fmt_parts = fmt_str.split()
    if len(fmt_parts) < 2:
        return f"Proof that {desc_text}"
    
    fmt_params = fmt_parts[1:]
    
    param_mapping = {}
    for idx, fmt_param in enumerate(fmt_params):
        if idx < len(param_list):
            param_mapping[fmt_param] = param_list[idx]
    
    result_text = desc_text
    
    def replace_single_match(match):
        inner_content = match.group(1)
        new_chars = []
        
        for ch in inner_content:
            if 'A' <= ch <= 'Z':
                lower_ch = ch.lower()
                if lower_ch in param_mapping:
                    new_chars.append(param_mapping[lower_ch].upper())
                else:
                    new_chars.append(ch)
            else:
                new_chars.append(ch)
        
        return '$' + ''.join(new_chars) + '$'
    
    result_text = re.sub(r'\$([^$]+)\$', replace_single_match, result_text)
    result_text = result_text.strip('.')
    
    return f"Proof that {result_text}."

def auxiliary_to_english_independent(auxiliary_text):
    if not auxiliary_text:
        return ""
    
    statement_list = [s.strip() for s in auxiliary_text.split(';') if s.strip()]
    english_parts_list = []
    
    for stmt in statement_list:
        if ',' in stmt and '=' in stmt:
            left_var, right_part = stmt.split('=', 1)
            left_var = left_var.strip()
            right_part = right_part.strip()
            
            construction_list = [c.strip() for c in right_part.split(',')]
            
            desc_list = []
            for constr in construction_list:
                full_stmt = f"{left_var} = {constr}"
                
                constr_parts = constr.split()
                if not constr_parts:
                    continue
                
                cmd_word = constr_parts[0]
                cmd_data = get_command_from_dict(cmd_word, constructions_dict)
                
                if cmd_data and "description" in cmd_data:
                    formatted_desc = replace_points_with_caps_independent(full_stmt, cmd_data["description"], cmd_data)
                    
                    if not desc_list:
                        desc_list.append(formatted_desc.rstrip('.'))
                    else:
                        prefix_pattern = r'^(Let \$[A-Z]+\$ be|Point \$[A-Z]+\$ (?:is|are)|Points [A-Z, ]+ (?:is|are))\s*'
                        core_desc = re.sub(prefix_pattern, '', formatted_desc)
                        desc_list.append(core_desc.rstrip('.'))
            
            if desc_list:
                if len(desc_list) == 1:
                    english_parts_list.append(desc_list[0] + '.')
                elif len(desc_list) == 2:
                    english_parts_list.append(f"{desc_list[0]} and {desc_list[1]}.")
                else:
                    combined = desc_list[0]
                    for idx in range(1, len(desc_list)):
                        if idx == len(desc_list) - 1:
                            combined += f", and {desc_list[idx]}."
                        else:
                            combined += f", {desc_list[idx]}"
                    english_parts_list.append(combined)
        else:
            stmt_parts = stmt.split('=')
            if len(stmt_parts) != 2:
                english_parts_list.append(stmt)
                continue
            
            left_var = stmt_parts[0].strip()
            right_part = stmt_parts[1].strip()
            
            right_words = right_part.split()
            if not right_words:
                english_parts_list.append(stmt)
                continue
            
            cmd_word = right_words[0]
            cmd_data = get_command_from_dict(cmd_word, constructions_dict)
            
            if cmd_data and "description" in cmd_data:
                formatted_desc = replace_points_with_caps_independent(stmt, cmd_data["description"], cmd_data)
                
                if not formatted_desc.endswith('.'):
                    formatted_desc += '.'
                
                english_parts_list.append(formatted_desc)
            else:
                english_parts_list.append(stmt)
    
    if not english_parts_list:
        return ""
    
    if len(english_parts_list) == 1:
        return english_parts_list[0]
    elif len(english_parts_list) == 2:
        return english_parts_list[0] + ' ' + english_parts_list[1]
    else:
        return ', '.join(english_parts_list[:-1]) + ', and ' + english_parts_list[-1]

def process_jsonl_file_all_fields_independent(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue        
            try:
                data = json.loads(line)
                
                if 'question' in data:
                    original_question = data['question']
                    question_en = symbolic_to_english_question_independent(original_question)
                    data['question_en'] = question_en
                else:
                    data['question_en'] = ""
                
                if 'conclusion' in data:
                    original_conclusion = data['conclusion']
                    conclusion_en = conclusion_to_english_independent(original_conclusion)
                    data['conclusion_en'] = conclusion_en
                else:
                    data['conclusion_en'] = ""
                
                if 'auxiliary' in data:
                    original_auxiliary = data['auxiliary']
                    auxiliary_en = auxiliary_to_english_independent(original_auxiliary)
                    data['auxiliary_en'] = auxiliary_en
                else:
                    data['auxiliary_en'] = ""
                
                outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                
            except json.JSONDecodeError as e:
                outfile.write(line + '\n')
            except Exception as e:
                outfile.write(line + '\n')

if __name__ == "__main__":
    input_file = "merged_all.jsonl"
    output_file = "output_en.jsonl"
    
    try:
        process_jsonl_file_all_fields_independent(input_file, output_file)
    except FileNotFoundError:
        pass
    except Exception as e:
        pass
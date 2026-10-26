
"""Implements the combination DD+AR."""
import time

from absl import logging
import dd
import graph as gh
import problem as pr
from problem import Dependency  # pylint: disable=g-importing-member
import trace_back


def saturate_or_goal(
    g: gh.Graph,
    theorems: list[pr.Theorem],
    level_times: list[float],
    p: pr.Problem,
    max_level: int = 100,
    timeout: int = 600,
) -> tuple[
    list[dict[str, list[tuple[gh.Point, ...]]]],
    list[dict[str, list[tuple[gh.Point, ...]]]],
    list[int],
    list[pr.Dependency],
]:
  """Run DD until saturation or goal found."""
  derives = []
  eq4s = []
  branching = []
  all_added = []

  while len(level_times) < max_level:
    level = len(level_times) + 1

    t = time.time()
    added, derv, eq4, n_branching = dd.bfs_one_level(
        g, theorems, level, p, verbose=False, nm_check=True, timeout=timeout
    )
    all_added += added
    branching.append(n_branching)

    derives.append(derv)
    eq4s.append(eq4)
    level_time = time.time() - t

    logging.info(f'Depth {level}/{max_level} time = {level_time}')  # pylint: disable=logging-fstring-interpolation
    level_times.append(level_time)

    if p.goal is not None:
      goal_args = list(map(lambda x: g.get(x, lambda: int(x)), p.goal.args))
      if g.check(p.goal.name, goal_args):  # found goal
        break

    if not added:  # saturated
      break

    if level_time > timeout:
      break

  return derives, eq4s, branching, all_added


def solve(
    g: gh.Graph,
    theorems: list[pr.Problem],
    controller: pr.Problem,
    max_level: int = 1000,
    timeout: int = 600,
) -> tuple[gh.Graph, list[float], str, list[int], list[pr.Dependency]]:
  """Alternate between DD and AR until goal is found."""
  status = 'saturated'
  level_times = []

  dervs, eq4 = g.derive_algebra(level=0, verbose=False)
  derives = [dervs]
  eq4s = [eq4]
  branches = []
  all_added = []

  gh.nm.draw(
    g.type2nodes[gh.Point],
    g.type2nodes[gh.Line],
    g.type2nodes[gh.Circle],
    g.type2nodes[gh.Segment])



  while len(level_times) < max_level:
    dervs, eq4, next_branches, added = saturate_or_goal(
        g, theorems, level_times, controller, max_level, timeout=timeout
    )
    all_added += added

    derives += dervs
    eq4s += eq4
    branches += next_branches
    
    # print(derives)
    # print(eq4s)
    # print(branches)



    # Now, it is either goal or saturated
    if controller.goal is not None:
      goal_args = g.names2points(controller.goal.args)

      if g.check(controller.goal.name, goal_args):  # found goal
        status = 'solved'
        break
    

    if not derives:  # officially saturated.
      break

    # Now we resort to algebra derivations.
    added = []
    while derives and not added:
      added += dd.apply_derivations(g, derives.pop(0))

    if added:
      continue

    # Final help from AR.
    while eq4s and not added:
      added += dd.apply_derivations(g, eq4s.pop(0))

    all_added += added
    # print("all_added")
    # print(all_added[0].name)
    # print(all_added[0].args)
    # print(all_added[0].rule_name)
    # print(all_added[0].level)
    
    if not added:  # Nothing left. saturated.
      break
    


  return g, level_times, status, branches, all_added

# from collections import defaultdict
# from typing import List, Dict, Tuple

# class GoalGraph:
#     """独立的反向推理图，正确处理Clause结构"""
#     def __init__(self, original_graph: gh.Graph):
#         self.goals = []  # 存储目标谓词元组 (name, args)
#         self.dependencies = defaultdict(list)
#         self.original = original_graph
        
#     def add_goal(self, clause: Union[pr.Construction, pr.Clause]):
#         """解析Clause/Construction对象，提取谓词"""
#         if isinstance(clause, pr.Construction):
#             # Construction类型目标（例如problem.goal）
#             self.goals.append((clause.name, clause.args))
#         elif isinstance(clause, pr.Clause):
#             # Clause类型目标（例如problem.goal_clause）
#             for pred in clause.predicates:
#                 self.goals.append((pred.name, pred.args))
        
#     def check_satisfied(self):
#         """检查所有谓词目标是否满足"""
#         return all(self.original.check(name, args) for name, args in self.goals)

# class BidirectionalSolver:
#     def __init__(self, graph: gh.Graph, theorems: List[pr.Problem]):
#         self.forward_graph = graph
#         self.goal_graph = GoalGraph(graph)
#         self.theorems = theorems
#         self.reverse_index = self._build_reverse_index(theorems)
        
#     def _build_reverse_index(self, theorems):
#         """构建谓词到定理的索引"""
#         index = defaultdict(list)
#         for thm in theorems:
#             if hasattr(thm, 'goal_clause'):
#                 goal_clause = thm.goal_clause
#                 # 处理列表或单个Clause的情况
#                 clauses = goal_clause if isinstance(goal_clause, list) else [goal_clause]
#                 for clause in clauses:
#                     for pred in clause.predicates:
#                         index[pred.name].append(thm)
#         return index

#     def _match_arguments(self, goal_args: list, theorem_args: list) -> Optional[dict]:
#         """变量匹配算法（简化版）"""
#         var_map = {}
#         for g_arg, t_arg in zip(goal_args, theorem_args):
#             if t_arg.isupper():  # 假设定理参数是大写字母变量
#                 if t_arg in var_map and var_map[t_arg] != g_arg:
#                     return None
#                 var_map[t_arg] = g_arg
#             else:  # 常量需精确匹配
#                 if t_arg != g_arg:
#                     return None
#         return var_map

#     def _apply_theorem_backward(self, theorem: pr.Problem, goal_name: str, goal_args: list) -> bool:
#         """尝试反向应用定理"""
#         # 获取定理结论谓词
#         theorem_goals = []
#         goal_clause = theorem.goal_clause
#         if isinstance(goal_clause, list):
#             for clause in goal_clause:
#                 theorem_goals.extend(clause.predicates)
#         else:
#             theorem_goals.extend(goal_clause.predicates)
            
#         # 寻找匹配的结论谓词
#         for t_pred in theorem_goals:
#             # 1. 名称匹配
#             if t_pred.name != goal_name:
#                 continue
                
#             # 2. 参数匹配
#             var_map = self._match_arguments(goal_args, t_pred.args)
#             if not var_map:
#                 continue
                
#             # 3. 验证前提条件
#             all_premises_met = True
#             for premise in theorem.clauses:
#                 # 应用变量替换
#                 prem_args = [var_map.get(arg, arg) for arg in premise.args]
#                 if not self.forward_graph.check(premise.name, prem_args):
#                     all_premises_met = False
#                     break
                    
#             if all_premises_met:
#                 # 4. 添加推理边
#                 prem_nodes = [
#                     self.forward_graph.get_node(premise.name, prem_args)
#                     for premise in theorem.clauses
#                 ]
#                 concl_node = self.forward_graph.get_node(goal_name, goal_args)
#                 self.forward_graph.add_edge(concl_node, prem_nodes, rule=theorem.url)
#                 return True
#         return False


    
# def solve(
#     g: gh.Graph,
#     theorems: List[pr.Problem],
#     controller: pr.Problem,
#     max_level: int = 1000,
#     timeout: int = 600,
# ) -> Tuple[gh.Graph, List[float], str, List[int], List[pr.Dependency]]:
#     """兼容原有架构的双向推理实现"""
    
#     # ===== 初始化阶段 =====
#     status = 'saturated'
#     level_times = []
    
#     # 创建双向求解器（不修改原图）
#     solver = BidirectionalSolver(g, theorems)
    
#     # 添加初始目标
#     if controller.goal_clause:
#         goal_clause = controller.goal_clause[0] if isinstance(controller.goal_clause, list) else controller.goal_clause
#         solver.goal_graph.add_goal(goal_clause)
    
#     # ===== 双向推理循环 =====
#     derives = []
#     eq4s = []
#     branches = []
#     all_added = []
    
#     for level in range(max_level):
#         # 正向推理步骤
#         dervs, eq4, next_branches, added = saturate_or_goal(
#             solver.forward_graph, theorems, level_times, controller, max_level, timeout
#         )
#         derives += dervs
#         eq4s += eq4
#         branches += next_branches
#         all_added += added
        
#         # 检查目标是否已满足
#         if solver.goal_graph.check_satisfied():
#             status = 'solved'
#             break
            
#         # 反向推理步骤（交替执行）
#         if level % 2 == 1:
#             for goal in solver.goal_graph.goals:
#                 candidate_theorems = solver.reverse_index.get(goal.name, [])
#                 for theorem in candidate_theorems:
#                     if self._apply_theorem_backward(theorem, goal):
#                         break
        
#         # 原有代数处理逻辑
#         added = []
#         while derives and not added:
#             added += dd.apply_derivations(solver.forward_graph, derives.pop(0))
#         if added:
#             continue
            
#         while eq4s and not added:
#             added += dd.apply_derivations(solver.forward_graph, eq4s.pop(0))
#         all_added += added
#         if not added:
#             break

#     return solver.forward_graph, level_times, status, branches, all_added

# def _apply_theorem_backward(self, theorem: pr.Problem, goal: pr.Clause) -> bool:
#     """尝试反向应用定理"""
#     # 1. 匹配目标与定理结论
#     if not self._match_goal_to_theorem(goal, theorem):
#         return False
        
#     # 2. 验证前提条件
#     premises = []
#     for premise in theorem.clauses:
#         if not self.forward_graph.check(premise.name, premise.args):
#             # 将未满足的前提作为新目标
#             self.goal_graph.add_goal(premise)
#             premises.append(premise)
    
#     if premises:
#         return False
        
#     # 3. 应用定理推导
#     self._add_theorem_edges(theorem)
#     return True

# def _match_goal_to_theorem(self, goal: pr.Clause, theorem: pr.Problem) -> bool:
#     """匹配目标与定理结论"""
#     theorem_goal = theorem.goal_clause[0] if isinstance(theorem.goal_clause, list) else theorem.goal_clause
#     if goal.name != theorem_goal.name:
#         return False
        
#     # 简单参数检查
#     if len(goal.args) != len(theorem_goal.args):
#         return False
        
#     # TODO: 实现更复杂的变量匹配逻辑
#     return True

# def _add_theorem_edges(self, theorem: pr.Problem):
#     """将定理转化为图边（兼容原有add_edge方法）"""
#     # 获取前提和结论节点
#     prem_nodes = []
#     for premise in theorem.clauses:
#         node = self.forward_graph.get_node(premise.name, premise.args)
#         prem_nodes.append(node)
        
#     concl_node = self.forward_graph.get_node(
#         theorem.goal_clause[0].name, 
#         theorem.goal_clause[0].args
#     )
    
#     # 添加推理边
#     self.forward_graph.add_edge(concl_node, prem_nodes, rule=theorem.url)

def get_proof_steps(
    g: gh.Graph, goal: pr.Clause, merge_trivials: bool = False
) -> tuple[
    list[pr.Dependency],
    list[pr.Dependency],
    list[tuple[list[pr.Dependency], list[pr.Dependency]]],
    dict[tuple[str, ...], int],
]:
  """Extract proof steps from the built DAG."""
  goal_args = g.names2nodes(goal.args)
  query = Dependency(goal.name, goal_args, None, None)

  setup, aux, log, setup_points = trace_back.get_logs(
      query, g, merge_trivials=merge_trivials
  )

  refs = {}
  setup = trace_back.point_log(setup, refs, set())
  aux = trace_back.point_log(aux, refs, setup_points)

  setup = [(prems, [tuple(p)]) for p, prems in setup]
  aux = [(prems, [tuple(p)]) for p, prems in aux]

  return setup, aux, log, refs

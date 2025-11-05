from langgraph.graph import StateGraph, END
from sample.PlanExecute_example.cast.state import PlanExecuteState
from sample.PlanExecute_example.cast.agents.planner import run_planner
from sample.PlanExecute_example.cast.agents.executor import run_executor


def plan_execute_workflow():
    """Plan → Execute 단계를 거치는 LangGraph 워크플로우"""
    graph = StateGraph(PlanExecuteState)

    graph.add_node("planner", lambda state: run_planner(state))
    graph.add_node("executor", lambda state: run_executor(state))

    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", END)

    return graph.compile()

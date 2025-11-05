from langgraph.graph import StateGraph
from multi_agent.modules import script_agent, shotlist_agent, tts_agent, image_agent, video_agent
from .types import WorkflowState

def build_graph():
    workflow = StateGraph(WorkflowState)

    workflow.add_node("script", script_agent.run)
    workflow.add_node("shotlist", shotlist_agent.run)
    workflow.add_node("tts", tts_agent.run)
    workflow.add_node("image", image_agent.run)
    workflow.add_node("video", video_agent.run)

    workflow.add_edge("__start__", "script")
    workflow.add_edge("script", "shotlist")
    workflow.add_edge("shotlist", "tts")
    workflow.add_edge("tts", "image")
    workflow.add_edge("image", "video")
    workflow.add_edge("video", "__end__")

    return workflow.compile()

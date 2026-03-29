from langgraph.graph import StateGraph
from models.schemas import WorkflowState

from agents.input_processor import InputProcessorAgent
from agents.requirement_extractor import RequirementExtractorAgent
from agents.semantic_duplicator import SemanticduplicatorAgent
from agents.conflict_detector import ConflictDetectorAgent
from agents.acceptance_criteria_generator import AcceptanceCriteriaAgent
from agents.human_approval_gate import HumanApprovalAgent
from agents.gherkin_test_generator import GherkinTestGeneratorAgent


def build_graph():
    graph = StateGraph(WorkflowState)

    graph.add_node("input", InputProcessorAgent().run)
    graph.add_node("extract", RequirementExtractorAgent().run)
    graph.add_node("dedup", SemanticduplicatorAgent().run)
    graph.add_node("conflict", ConflictDetectorAgent().run)
    graph.add_node("ac", AcceptanceCriteriaAgent().run)
    graph.add_node("approval", HumanApprovalAgent().run)
    graph.add_node("gherkin", GherkinTestGeneratorAgent().run)

    graph.set_entry_point("input")

    graph.add_edge("input", "extract")
    graph.add_edge("extract", "dedup")
    graph.add_edge("dedup", "conflict")
    graph.add_edge("conflict", "ac")
    graph.add_edge("ac", "approval")
    graph.add_edge("approval", "gherkin")

    return graph.compile()

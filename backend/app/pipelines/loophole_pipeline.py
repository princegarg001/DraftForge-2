from typing import List
from app.ai.evaluation.models import EvaluationFinding
from app.ai.graph.graph_reasoner import GraphReasoner
from app.ai.graph.models import LoopholeFinding
from app.core.constants import DocumentType


class LoopholePipeline:
    """Orchestrates graph-based loophole detection."""

    def __init__(self):
        self.reasoner = GraphReasoner()

    def run(
        self,
        doc_type: DocumentType,
        findings: List[EvaluationFinding]
    ) -> List[LoopholeFinding]:
        return self.reasoner.analyze_loopholes(doc_type=doc_type, findings=findings)
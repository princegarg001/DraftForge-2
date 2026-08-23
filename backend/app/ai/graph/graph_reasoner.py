import uuid
from typing import List, Set
from app.ai.evaluation.models import EvaluationFinding
from app.ai.graph.graph_retriever import GraphRetriever
from app.ai.graph.models import LoopholeFinding
from app.core.constants import DocumentType, FindingCategory, FindingStatus


class GraphReasoner:
    """
    Reasoning engine that performs graph-traversals over Neo4j Aura
    to identify clause dependency gaps, exposed legal risks, and skill targets.
    """

    def __init__(self):
        self.retriever = GraphRetriever()

    def analyze_loopholes(
        self,
        doc_type: DocumentType,
        findings: List[EvaluationFinding]
    ) -> List[LoopholeFinding]:
        loopholes: List[LoopholeFinding] = []

        # 1. Identify present vs missing/failed clauses from evaluation findings
        present_clause_ids: Set[str] = set()
        missing_clause_ids: Set[str] = set()

        for f in findings:
            cid = f.metadata.get("clause_id")
            if not cid:
                continue
            if f.status == FindingStatus.PASS:
                present_clause_ids.add(cid)
            elif f.status in (FindingStatus.FAIL, FindingStatus.PARTIAL):
                missing_clause_ids.add(cid)

        # 2. Dependency Checking via Graph: (A) exists, but prerequisite (B) is missing
        dependencies = self.retriever.clause_graph.get_dependencies_for_doctype(doc_type)
        for dep in dependencies:
            if dep.source_clause_id in present_clause_ids and dep.target_clause_id in missing_clause_ids:
                loopholes.append(
                    LoopholeFinding(
                        finding_id=f"gap_dep_{uuid.uuid4().hex[:8]}",
                        title=f"Unresolved Dependency: {dep.source_clause_name}",
                        severity="HIGH",
                        gap_type="MISSING_DEPENDENCY",
                        related_clause_id=dep.source_clause_id,
                        related_clause_name=dep.source_clause_name,
                        prerequisite_clause_id=dep.target_clause_id,
                        prerequisite_clause_name=dep.target_clause_name,
                        educational_observation=(
                            f"The draft includes '{dep.source_clause_name}', but is missing its prerequisite "
                            f"'{dep.target_clause_name}'. {dep.reason}."
                        ),
                        reference_recommendation=(
                            f"Incorporate the prerequisite '{dep.target_clause_name}' to ensure structural cohesion."
                        )
                    )
                )

        # 3. Unmitigated Legal Exposure Analysis
        if missing_clause_ids:
            risk_records = self.retriever.get_unmitigated_risks(list(missing_clause_ids))
            skill_records = {
                item["clause_id"]: item
                for item in self.retriever.get_skill_mappings(list(missing_clause_ids))
            }

            for rec in risk_records:
                cid = rec["clause_id"]
                cname = rec["clause_name"]
                rname = rec["risk_name"]
                sev = rec["severity"]
                rdesc = rec["risk_description"]

                skill_info = skill_records.get(cid, {})

                loopholes.append(
                    LoopholeFinding(
                        finding_id=f"gap_risk_{uuid.uuid4().hex[:8]}",
                        title=f"Potential Risk: {rname}",
                        severity=sev,
                        gap_type="UNMITIGATED_RISK",
                        related_clause_id=cid,
                        related_clause_name=cname,
                        risk_name=rname,
                        skill_id=skill_info.get("skill_id"),
                        skill_name=skill_info.get("skill_name"),
                        educational_observation=(
                            f"Omission of '{cname}' leaves a potential loophole. Reference risk: {rdesc}"
                        ),
                        reference_recommendation=(
                            f"Draft standard provisions for '{cname}' to mitigate '{rname}'."
                        )
                    )
                )

        return loopholes
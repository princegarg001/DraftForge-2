GET_RISKS_FOR_MISSING_CLAUSES = """
UNWIND $missing_clause_ids AS cid
MATCH (c:Clause {clause_id: cid})-[m:MITIGATES]->(r:Risk)
RETURN 
    c.clause_id AS clause_id,
    c.name AS clause_name,
    r.risk_id AS risk_id,
    r.name AS risk_name,
    r.severity AS severity,
    r.description AS risk_description
"""

GET_ALL_RISKS_FOR_DOCTYPE = """
MATCH (d:DocumentType {name: $document_type})-[:REQUIRES_CLAUSE]->(c:Clause)-[:MITIGATES]->(r:Risk)
RETURN DISTINCT 
    c.clause_id AS clause_id,
    c.name AS clause_name,
    r.risk_id AS risk_id,
    r.name AS risk_name,
    r.severity AS severity,
    r.description AS risk_description
"""
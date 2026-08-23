INIT_CONSTRAINTS = """
CREATE CONSTRAINT clause_id_unique IF NOT EXISTS
FOR (c:Clause) REQUIRE c.clause_id IS UNIQUE;

CREATE CONSTRAINT doc_type_unique IF NOT EXISTS
FOR (d:DocumentType) REQUIRE d.name IS UNIQUE;

CREATE CONSTRAINT risk_id_unique IF NOT EXISTS
FOR (r:Risk) REQUIRE r.risk_id IS UNIQUE;

CREATE CONSTRAINT skill_id_unique IF NOT EXISTS
FOR (s:Skill) REQUIRE s.skill_id IS UNIQUE;
"""

GET_CLAUSE_DEPENDENCIES_BY_DOCTYPE = """
MATCH (d:DocumentType {name: $document_type})-[:REQUIRES_CLAUSE]->(c1:Clause)
OPTIONAL MATCH (c1)-[dep:DEPENDS_ON]->(c2:Clause)
RETURN 
    c1.clause_id AS source_id,
    c1.name AS source_name,
    c2.clause_id AS target_id,
    c2.name AS target_name,
    dep.reason AS reason
"""

GET_PREREQUISITES_FOR_CLAUSE = """
MATCH (c:Clause {clause_id: $clause_id})-[dep:DEPENDS_ON]->(prereq:Clause)
RETURN 
    prereq.clause_id AS prereq_id,
    prereq.name AS prereq_name,
    dep.reason AS reason
"""
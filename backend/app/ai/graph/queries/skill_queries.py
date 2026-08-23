GET_SKILLS_FOR_CLAUSES = """
UNWIND $clause_ids AS cid
MATCH (c:Clause {clause_id: cid})-[:RELATES_TO_SKILL]->(s:Skill)
RETURN 
    c.clause_id AS clause_id,
    s.skill_id AS skill_id,
    s.name AS skill_name,
    s.category AS skill_category
"""

UPSERT_STUDENT_SKILL_HISTORY = """
MERGE (u:Student {id: $user_id})
MERGE (s:Skill {skill_id: $skill_id})
MERGE (u)-[r:PERFORMANCE_ON]->(s)
ON CREATE SET r.score = $score, r.attempts = 1, r.updated_at = timestamp()
ON MATCH SET r.score = (r.score + $score) / 2.0, r.attempts = r.attempts + 1, r.updated_at = timestamp()
RETURN r.score AS new_score
"""
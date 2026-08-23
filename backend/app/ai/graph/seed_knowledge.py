from app.core.logging import get_logger
from app.db.neo4j import execute_cypher_write

logger = get_logger("graph_seed")

SEED_CYPHER = """
// 1. Document Types
MERGE (d1:DocumentType {name: 'AFFIDAVIT_OF_CHARACTER'})
MERGE (d2:DocumentType {name: 'EMPLOYMENT_AGREEMENT'})
MERGE (d3:DocumentType {name: 'RENT_AGREEMENT'})
MERGE (d4:DocumentType {name: 'LEGAL_NOTICE'})

// 2. Skills
MERGE (s1:Skill {skill_id: 'SKILL_PARTIES', name: 'Party Identification & Capacity', category: 'DRAFTING_ESSENTIALS', description: 'Accurate legal description of signatories'})
MERGE (s2:Skill {skill_id: 'SKILL_VERIFICATION', name: 'Jurat & Verification Formats', category: 'EVIDENTIARY_COMPLIANCE', description: 'Statutory solemn affirmation and verification formula'})
MERGE (s3:Skill {skill_id: 'SKILL_TERMINATION', name: 'Termination & Severance Clauses', category: 'RISK_MANAGEMENT', description: 'Drafting clear notice periods and cause-based exits'})
MERGE (s4:Skill {skill_id: 'SKILL_IP_CONF', name: 'Confidentiality & Restrictive Covenants', category: 'PROTECTIVE_COVENANTS', description: 'Drafting enforceable non-disclosure provisions'})
MERGE (s5:Skill {skill_id: 'SKILL_FINANCIALS', name: 'Financial Terms & Security Deposits', category: 'COMMERCIAL_TERMS', description: 'Specifying rent, deduction formulas, and refund periods'})
MERGE (s6:Skill {skill_id: 'SKILL_CAUSE_ACTION', name: 'Cause of Action & Legal Demands', category: 'LITIGATION_PREP', description: 'Drafting statutory notices with structured default chronologies'})

// 3. Affidavit Clauses & Risks
MERGE (c_aff1:Clause {clause_id: 'AFF_DEPONENT_ID', name: 'Deponent Identity & Parentage', document_type: 'AFFIDAVIT_OF_CHARACTER'})
MERGE (c_aff2:Clause {clause_id: 'AFF_MORAL_CHAR', name: 'Good Moral Character Declaration', document_type: 'AFFIDAVIT_OF_CHARACTER'})
MERGE (c_aff3:Clause {clause_id: 'AFF_NO_CRIMINAL', name: 'No Criminal Antecedents', document_type: 'AFFIDAVIT_OF_CHARACTER'})
MERGE (c_aff4:Clause {clause_id: 'AFF_VERIFICATION', name: 'Verification Clause and Jurat', document_type: 'AFFIDAVIT_OF_CHARACTER'})

MERGE (r_aff1:Risk {risk_id: 'RISK_AFF_INADMISSIBLE', name: 'Defective Jurat & Inadmissibility', severity: 'HIGH', description: 'Affidavit liable to be rejected by authorities if verification lacks place, date, or knowledge-attribution formula.'})
MERGE (r_aff2:Risk {risk_id: 'RISK_AFF_PERJURY', name: 'Ambiguous Statement of Fact', severity: 'MEDIUM', description: 'Lack of clear separation between personal knowledge and derived belief.'})

MERGE (d1)-[:REQUIRES_CLAUSE]->(c_aff1)
MERGE (d1)-[:REQUIRES_CLAUSE]->(c_aff2)
MERGE (d1)-[:REQUIRES_CLAUSE]->(c_aff3)
MERGE (d1)-[:REQUIRES_CLAUSE]->(c_aff4)

MERGE (c_aff4)-[:DEPENDS_ON {reason: 'Verification clause requires prior factual statements and identified deponent'}]->(c_aff1)
MERGE (c_aff4)-[:MITIGATES]->(r_aff1)
MERGE (c_aff3)-[:MITIGATES]->(r_aff2)
MERGE (c_aff1)-[:RELATES_TO_SKILL]->(s1)
MERGE (c_aff4)-[:RELATES_TO_SKILL]->(s2)

// 4. Employment Agreement Clauses & Risks
MERGE (c_emp1:Clause {clause_id: 'EMP_PARTIES', name: 'Parties Identification', document_type: 'EMPLOYMENT_AGREEMENT'})
MERGE (c_emp2:Clause {clause_id: 'EMP_DUTIES', name: 'Job Designation and Duties', document_type: 'EMPLOYMENT_AGREEMENT'})
MERGE (c_emp3:Clause {clause_id: 'EMP_COMP', name: 'Remuneration and Salary', document_type: 'EMPLOYMENT_AGREEMENT'})
MERGE (c_emp4:Clause {clause_id: 'EMP_TERM', name: 'Termination Notice Period', document_type: 'EMPLOYMENT_AGREEMENT'})
MERGE (c_emp5:Clause {clause_id: 'EMP_CONF', name: 'Confidentiality and Proprietary Information', document_type: 'EMPLOYMENT_AGREEMENT'})
MERGE (c_emp6:Clause {clause_id: 'EMP_GOV_LAW', name: 'Governing Law & Jurisdiction', document_type: 'EMPLOYMENT_AGREEMENT'})

MERGE (r_emp1:Risk {risk_id: 'RISK_EMP_WRONGFUL_TERM', name: 'Indefinite Liability on Exit', severity: 'HIGH', description: 'Absence of mutual notice or severance formula exposes employer to wrongful termination claims.'})
MERGE (r_emp2:Risk {risk_id: 'RISK_EMP_DATA_LEAK', name: 'Loss of Proprietary Rights & Trade Secrets', severity: 'HIGH', description: 'Lack of explicit post-termination confidentiality clause risks trade secret leakage without contractual recourse.'})
MERGE (r_emp3:Risk {risk_id: 'RISK_EMP_FORUM_UNCERTAINTY', name: 'Jurisdictional Ambiguity', severity: 'MEDIUM', description: 'Absence of designated exclusive forum creates multi-jurisdiction litigation exposure.'})

MERGE (d2)-[:REQUIRES_CLAUSE]->(c_emp1)
MERGE (d2)-[:REQUIRES_CLAUSE]->(c_emp2)
MERGE (d2)-[:REQUIRES_CLAUSE]->(c_emp3)
MERGE (d2)-[:REQUIRES_CLAUSE]->(c_emp4)
MERGE (d2)-[:REQUIRES_CLAUSE]->(c_emp5)
MERGE (d2)-[:REQUIRES_CLAUSE]->(c_emp6)

MERGE (c_emp4)-[:DEPENDS_ON {reason: 'Termination mechanics must link to defined remuneration and notice formula'}]->(c_emp3)
MERGE (c_emp4)-[:MITIGATES]->(r_emp1)
MERGE (c_emp5)-[:MITIGATES]->(r_emp2)
MERGE (c_emp6)-[:MITIGATES]->(r_emp3)

MERGE (c_emp4)-[:RELATES_TO_SKILL]->(s3)
MERGE (c_emp5)-[:RELATES_TO_SKILL]->(s4)

// 5. Rent Agreement Clauses & Risks
MERGE (c_rent1:Clause {clause_id: 'RENT_PARTIES_PREMISES', name: 'Lessor/Lessee & Demised Property', document_type: 'RENT_AGREEMENT'})
MERGE (c_rent2:Clause {clause_id: 'RENT_MONTHLY_PAYMENT', name: 'Monthly Rent Amount & Due Date', document_type: 'RENT_AGREEMENT'})
MERGE (c_rent3:Clause {clause_id: 'RENT_SEC_DEPOSIT', name: 'Interest-Free Security Deposit', document_type: 'RENT_AGREEMENT'})
MERGE (c_rent4:Clause {clause_id: 'RENT_TENURE', name: 'Agreement Duration and Extension', document_type: 'RENT_AGREEMENT'})
MERGE (c_rent5:Clause {clause_id: 'RENT_TERMINATION', name: 'Notice for Eviction / Vacating', document_type: 'RENT_AGREEMENT'})

MERGE (r_rent1:Risk {risk_id: 'RISK_RENT_TENANCY_DISPUTE', name: 'Deemed Perpetual Tenancy Risk', severity: 'HIGH', description: 'Failure to specify fixed 11-month license term and renewal conditions can trigger statutory tenancy protections.'})
MERGE (r_rent2:Risk {risk_id: 'RISK_RENT_DEPOSIT_DISPUTE', name: 'Security Deposit Forfeiture Ambiguity', severity: 'MEDIUM', description: 'Unspecified timeline and deduction conditions for deposit refund create recovery disputes upon vacating.'})

MERGE (d3)-[:REQUIRES_CLAUSE]->(c_rent1)
MERGE (d3)-[:REQUIRES_CLAUSE]->(c_rent2)
MERGE (d3)-[:REQUIRES_CLAUSE]->(c_rent3)
MERGE (d3)-[:REQUIRES_CLAUSE]->(c_rent4)
MERGE (d3)-[:REQUIRES_CLAUSE]->(c_rent5)

MERGE (c_rent5)-[:DEPENDS_ON {reason: 'Vacating notice relies on defined tenure expiry and deposit refund terms'}]->(c_rent3)
MERGE (c_rent4)-[:MITIGATES]->(r_rent1)
MERGE (c_rent3)-[:MITIGATES]->(r_rent2)

MERGE (c_rent3)-[:RELATES_TO_SKILL]->(s5)
MERGE (c_rent5)-[:RELATES_TO_SKILL]->(s3)

// 6. Legal Notice Clauses & Risks
MERGE (c_not1:Clause {clause_id: 'NOT_AUTHORITY', name: 'Instructions from Client Authority', document_type: 'LEGAL_NOTICE'})
MERGE (c_not2:Clause {clause_id: 'NOT_FACTS', name: 'Factual Chronology of Default/Cause', document_type: 'LEGAL_NOTICE'})
MERGE (c_not3:Clause {clause_id: 'NOT_DEMAND', name: 'Clear Demand & Specific Grace Period', document_type: 'LEGAL_NOTICE'})
MERGE (c_not4:Clause {clause_id: 'NOT_CONSEQUENCE', name: 'Notice of Legal Action & Cost Consequences', document_type: 'LEGAL_NOTICE'})

MERGE (r_not1:Risk {risk_id: 'RISK_NOT_DEFECTIVE_NOTICE', name: 'Premature Action or Invalid Demand', severity: 'HIGH', description: 'Omission of explicit cure period or client authorization invalidates statutory notice prerequisites for litigation.'})

MERGE (d4)-[:REQUIRES_CLAUSE]->(c_not1)
MERGE (d4)-[:REQUIRES_CLAUSE]->(c_not2)
MERGE (d4)-[:REQUIRES_CLAUSE]->(c_not3)
MERGE (d4)-[:REQUIRES_CLAUSE]->(c_not4)

MERGE (c_not4)-[:DEPENDS_ON {reason: 'Threat of legal action requires preceding specific demand and default timeline'}]->(c_not3)
MERGE (c_not3)-[:MITIGATES]->(r_not1)
MERGE (c_not2)-[:RELATES_TO_SKILL]->(s6)
MERGE (c_not3)-[:RELATES_TO_SKILL]->(s6)
"""


def seed_knowledge_graph() -> None:
    """Seeds master legal document topologies, clauses, risks, and skill relationships."""
    logger.info("Seeding Neo4j Aura Knowledge Graph...")
    execute_cypher_write(SEED_CYPHER)
    logger.info("Knowledge Graph seeded successfully.")
import uuid
from app.db.supabase import get_supabase_admin_client

supabase = get_supabase_admin_client()

SKILLS = [
    {
        "name": "Parties & Recitals Demarcation",
        "category": "STRUCTURE",
        "description": "Accurate identification of parties, juristic capacities, and recitals."
    },
    {
        "name": "Jurisdiction & Statutory References",
        "category": "STATUTORY",
        "description": "Incorporating precise statutory acts, court jurisdictions, and stamp duty recitals."
    },
    {
        "name": "Operative Consideration & Remuneration",
        "category": "SUBSTANTIVE",
        "description": "Drafting clear financial terms, security deposits, and compensation mechanics."
    },
    {
        "name": "Termination & Dispute Resolution",
        "category": "SUBSTANTIVE",
        "description": "Structuring valid notice periods, summary dismissal, and arbitration clauses."
    },
    {
        "name": "Verification Clauses & Jurats",
        "category": "FORMATTING",
        "description": "Executing valid oaths, perjury liability statements, and deponent verifications."
    }
]

QUIZZES = [
    {
        "id": "11111111-1111-1111-1111-111111111101",
        "document_type": "AFFIDAVIT_OF_CHARACTER",
        "title": "Affidavit Verification & Perjury Essentials",
        "description": "Test your mastery over Indian affidavit statutory jurats and deponent statements.",
        "difficulty": "BEGINNER",
        "questions": [
            {
                "id": "22222222-2222-2222-2222-222222222201",
                "question_text": "Which essential element must be present in the Verification clause of an Indian affidavit?",
                "order_index": 1,
                "options": [
                    {"key": "A", "text": "Statement verifying truth and stating nothing material is concealed"},
                    {"key": "B", "text": "A clause waiving all criminal liability"},
                    {"key": "C", "text": "A monetary consideration clause"},
                    {"key": "D", "text": "Arbitration seat designation"}
                ],
                "correct_option": "A",
                "explanation": "An affidavit verification must state that the contents are true to deponent's knowledge/belief and nothing material has been concealed under penalty of perjury."
            },
            {
                "id": "22222222-2222-2222-2222-222222222202",
                "question_text": "Before whom can an Indian Affidavit of Character for bar enrolment be sworn?",
                "order_index": 2,
                "options": [
                    {"key": "A", "text": "Any university professor"},
                    {"key": "B", "text": "An Oath Commissioner, Notary Public, or Magistrate"},
                    {"key": "C", "text": "Opposing party's counsel"},
                    {"key": "D", "text": "A police sub-inspector"}
                ],
                "correct_option": "B",
                "explanation": "Under the Indian Oaths Act and Notaries Act, affidavits must be sworn before an authorized Notary Public, Oath Commissioner, or Magistrate."
            }
        ]
    },
    {
        "id": "11111111-1111-1111-1111-111111111102",
        "document_type": "EMPLOYMENT_AGREEMENT",
        "title": "Restrictive Covenants & Section 27 Enforceability",
        "description": "Assess non-compete vs non-solicitation legality under Indian Contract Act, 1872.",
        "difficulty": "INTERMEDIATE",
        "questions": [
            {
                "id": "22222222-2222-2222-2222-222222222203",
                "question_text": "Under Section 27 of the Indian Contract Act, 1872, what is the legal status of a post-employment non-compete clause?",
                "order_index": 1,
                "options": [
                    {"key": "A", "text": "Fully enforceable for up to 3 years"},
                    {"key": "B", "text": "Void and unenforceable as a restraint of trade"},
                    {"key": "C", "text": "Enforceable only if approved by a magistrate"},
                    {"key": "D", "text": "Enforceable if salary exceeds 10 LPA"}
                ],
                "correct_option": "B",
                "explanation": "Indian courts consistently hold post-termination non-compete covenants void under Section 27 of the Indian Contract Act, 1872."
            }
        ]
    },
    {
        "id": "11111111-1111-1111-1111-111111111103",
        "document_type": "RENT_AGREEMENT",
        "title": "Rent Agreement Security Deposits & Notice Periods",
        "description": "Test clauses concerning notice periods, repair obligations, and utility apportionment.",
        "difficulty": "BEGINNER",
        "questions": [
            {
                "id": "22222222-2222-2222-2222-222222222204",
                "question_text": "What is the standard notice period for early termination in a residential rental deed in India?",
                "order_index": 1,
                "options": [
                    {"key": "A", "text": "24 hours notice"},
                    {"key": "B", "text": "One month (30 days) prior written notice"},
                    {"key": "C", "text": "1 year mandatory notice"},
                    {"key": "D", "text": "Oral notice is sufficient"}
                ],
                "correct_option": "B",
                "explanation": "Standard Indian residential tenancy agreements require 30 days / one month prior written notice by either party."
            }
        ]
    }
]


def seed():
    print("Seeding Skills (matching by name)...")
    for s in SKILLS:
        supabase.table("skills").upsert(s, on_conflict="name").execute()

    print("Seeding Quizzes & Questions...")
    for q in QUIZZES:
        quiz_data = dict(q)
        questions = quiz_data.pop("questions")
        supabase.table("quizzes").upsert(quiz_data, on_conflict="id").execute()
        for qu in questions:
            qu["quiz_id"] = quiz_data["id"]
            supabase.table("quiz_questions").upsert(qu, on_conflict="id").execute()

    print("✅ Seed completed successfully!")


if __name__ == "__main__":
    seed()
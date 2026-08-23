import sys
import os
import uuid
from fastapi.testclient import TestClient

# Ensure app is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.constants import UserRole
from app.models.database.models import UserProfileDB
from app.dependencies import get_current_user
from app.db.supabase import get_supabase_admin_client

# Real verified database student and teacher
student_id = "fede7239-bf5f-45ea-8c11-47ff90c01b1d"
teacher_id = "b48caabf-d065-49c9-bfc0-dadcedd7a367"

test_student = UserProfileDB(
    id=student_id,
    email="ashisingla85@gmail.com",
    role=UserRole.STUDENT,
    full_name="Himanshi Singla",
)

test_teacher = UserProfileDB(
    id=teacher_id,
    email="24csu078@ncuindia.edu",
    role=UserRole.TEACHER,
    full_name="Arjun Sharma",
)

client = TestClient(app)

results_summary = []

def test_endpoint(name, method, url, override_user=None, expected_status=None, **kwargs):
    if override_user:
        app.dependency_overrides[get_current_user] = lambda: override_user
    else:
        app.dependency_overrides.pop(get_current_user, None)
    
    status_text = "FAILED"
    res = None
    try:
        if method == "GET":
            res = client.get(url, **kwargs)
        elif method == "POST":
            res = client.post(url, **kwargs)
        elif method == "PATCH":
            res = client.patch(url, **kwargs)
        elif method == "DELETE":
            res = client.delete(url, **kwargs)
        elif method == "OPTIONS":
            res = client.options(url, **kwargs)
        
        is_ok = res.status_code in (200, 201) if not expected_status else res.status_code == expected_status
        status_text = "WORKING" if is_ok else f"STATUS_{res.status_code}"
        print(f"[{method:5}] {url:45} -> Status: {res.status_code} ({status_text})")
        if res.status_code >= 500:
            print(f"       ERROR DETAIL: {res.text[:200]}")
    except Exception as exc:
        print(f"[{method:5}] {url:45} -> CRASHED: {exc}")
        status_text = "CRASHED"

    results_summary.append({
        "name": name,
        "method": method,
        "url": url,
        "status": status_text,
        "code": res.status_code if res else 500
    })
    return res

def run_all_tests():
    print("=" * 80)
    print("COMPREHENSIVE BACKEND ENDPOINT AUDIT & VERIFICATION")
    print("=" * 80)

    # 1. Health & Root Endpoints
    test_endpoint("Root Overview", "GET", "/")
    test_endpoint("System Health (Root)", "GET", "/health")
    test_endpoint("System Telemetry (API)", "GET", "/api/v1/health")

    # 2. Documents & Classifier
    test_endpoint("Classify Legal Text", "POST", "/api/v1/documents/classify", data={"text": "NOW THEREFORE THIS EMPLOYMENT AGREEMENT WITNESSETH THAT in consideration of mutual covenants..."})
    test_endpoint("List Reference Documents", "GET", "/api/v1/documents/reference", override_user=test_student)

    # 3. Drafts Creation & Management
    draft_res = test_endpoint("Create Draft (Text)", "POST", "/api/v1/drafts", override_user=test_student, json={"title": "Affidavit of Residence", "document_type": "AFFIDAVIT_OF_CHARACTER", "raw_content": "I, Himanshi Singla, do solemnly swear and affirm that I reside at Delhi and have never been convicted of any offense."})
    draft_id = draft_res.json().get("id") if draft_res and draft_res.status_code == 201 else None

    test_endpoint("List Student Drafts", "GET", "/api/v1/drafts", override_user=test_student)
    if draft_id:
        test_endpoint("Get Draft Details", "GET", f"/api/v1/drafts/{draft_id}", override_user=test_student)
        test_endpoint("Add Draft Version", "POST", f"/api/v1/drafts/{draft_id}/versions", override_user=test_student, data={"content": "I, Himanshi Singla, do solemnly swear and state on oath that I am a law-abiding citizen and deponent herein."})
        test_endpoint("Compare Draft Versions", "GET", f"/api/v1/drafts/{draft_id}/compare?v1=1&v2=2", override_user=test_student)

    # 4. Evaluations & Loopholes
    eval_id = None
    if draft_id:
        eval_res = test_endpoint("Evaluate Draft", "POST", "/api/v1/evaluations", override_user=test_student, json={"draft_id": draft_id, "version_number": 1})
        eval_id = eval_res.json().get("id") if eval_res and eval_res.status_code == 201 else None

    if eval_id:
        test_endpoint("Get Evaluation Report", "GET", f"/api/v1/evaluations/{eval_id}", override_user=test_student)
        test_endpoint("Explain Evaluation AI", "POST", "/api/v1/ai/explain-evaluation", override_user=test_student, json={"evaluation_id": eval_id, "clause_category": "STRUCTURE", "student_query": "How do I improve my jurat clause?"})
        test_endpoint("GraphRAG Loophole Analysis", "GET", f"/api/v1/loopholes/{eval_id}", override_user=test_student)

    # 5. AI Drafting Assist & RAG Retrieve
    test_endpoint("AI Assist Drafting", "POST", "/api/v1/ai/assist-drafting", override_user=test_student, json={"document_type": "EMPLOYMENT_AGREEMENT", "target_clause": "NON_SOLICITATION", "user_instructions": "Limit duration to 12 months."})
    test_endpoint("RAG Retrieve Reference Evidence", "POST", "/api/v1/rag/retrieve", override_user=test_student, json={"query": "non solicitation post employment period", "document_type": "EMPLOYMENT_AGREEMENT", "top_k": 2})

    # 6. Conversations & Multi-tier Chat
    conv_res = test_endpoint("Create Conversation", "POST", "/api/v1/conversations", override_user=test_student, json={"title": "Drafting Guidance Session"})
    conv_id = conv_res.json().get("id") if conv_res and conv_res.status_code == 201 else None

    test_endpoint("List Conversations", "GET", "/api/v1/conversations", override_user=test_student)
    if conv_id:
        test_endpoint("Get Conversation Messages", "GET", f"/api/v1/conversations/{conv_id}/messages", override_user=test_student)
        test_endpoint("Send Chat Message (AI Tutor)", "POST", "/api/v1/chat/send", override_user=test_student, json={"conversation_id": conv_id, "message": "What are the essential elements of an affidavit of character?", "document_type": "AFFIDAVIT_OF_CHARACTER"})

    # 7. Skills & Roadmaps
    test_endpoint("Get Student Skills", "GET", "/api/v1/skills/my-skills", override_user=test_student)
    test_endpoint("Get Active Roadmap", "GET", "/api/v1/roadmap", override_user=test_student)
    road_res = test_endpoint("Generate New Roadmap", "POST", "/api/v1/roadmap/generate", override_user=test_student)
    if road_res and road_res.status_code == 201:
        items = road_res.json().get("roadmap_items", [])
        if items:
            item_id = items[0].get("id")
            test_endpoint("Complete Roadmap Milestone", "PATCH", f"/api/v1/roadmap/items/{item_id}/complete", override_user=test_student)

    # 8. Quizzes
    test_endpoint("List Quizzes", "GET", "/api/v1/quizzes", override_user=test_student)

    # 9. Progress & Leaderboard
    test_endpoint("Student Progress Analytics", "GET", "/api/v1/progress", override_user=test_student)
    test_endpoint("Global Leaderboard", "GET", "/api/v1/leaderboard", override_user=test_student)

    # 10. Teacher Management & Assignments
    assign_res = test_endpoint("Teacher Create Assignment", "POST", "/api/v1/assignments", override_user=test_teacher, json={"title": "Legal Notice Drafting Exercise", "document_type": "LEGAL_NOTICE", "instructions": "Draft a formal section 138 NI Act notice for cheque dishonour."})
    assign_id = assign_res.json().get("id") if assign_res and assign_res.status_code == 201 else None

    test_endpoint("Teacher List Assignments", "GET", "/api/v1/teachers/assignments", override_user=test_teacher)
    test_endpoint("Student List Assignments", "GET", "/api/v1/assignments", override_user=test_student)

    if assign_id and draft_id:
        test_endpoint("Get Assignment Details", "GET", f"/api/v1/assignments/{assign_id}", override_user=test_student)
        draft_full = client.get(f"/api/v1/drafts/{draft_id}").json()
        version_id = draft_full["versions"][0]["id"]
        sub_res = test_endpoint("Submit Assignment", "POST", "/api/v1/submissions", override_user=test_student, json={"assignment_id": assign_id, "draft_id": draft_id, "draft_version_id": version_id})
        sub_id = sub_res.json().get("id") if sub_res and sub_res.status_code == 201 else None

        if sub_id:
            test_endpoint("Teacher Submissions Audit", "GET", f"/api/v1/submissions/assignment/{assign_id}", override_user=test_teacher)
            test_endpoint("Teacher Score Override", "POST", f"/api/v1/submissions/{sub_id}/override", override_user=test_teacher, json={"overridden_score": 92.5, "override_reason": "Excellent statutory compliance and recital clarity.", "teacher_notes": "Well done on deponent verification."})

    test_endpoint("Teacher Cohort Analytics (Teachers router)", "GET", "/api/v1/teachers/cohort-analytics", override_user=test_teacher)
    test_endpoint("Cohort Analytics (Analytics router)", "GET", "/api/v1/analytics/cohort", override_user=test_teacher)

    print("=" * 80)
    print("ALL TESTS COMPLETED. SUMMARY:")
    working_count = sum(1 for r in results_summary if r["status"] == "WORKING")
    print(f"Total Tested: {len(results_summary)} | Working: {working_count} | Non-200: {len(results_summary) - working_count}")
    print("=" * 80)

if __name__ == "__main__":
    run_all_tests()

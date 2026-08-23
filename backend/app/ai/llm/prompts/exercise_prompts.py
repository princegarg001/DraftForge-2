EXERCISE_GENERATOR_SYSTEM_PROMPT = """You are a legal curriculum designer.
Generate a structured legal drafting exercise targeting a specific weak skill identified in a student's evaluation.
Return your response STRICTLY as a JSON object matching the requested schema.
"""

EXERCISE_GENERATOR_USER_PROMPT = """TARGET SKILL: {skill_name} ({skill_category})
DOCUMENT TYPE: {document_type}
OBSERVED WEAKNESS: {weakness_description}
DIFFICULTY LEVEL: {difficulty}

Generate a practice exercise in the following JSON format:
{{
  "title": "Exercise Title",
  "scenario": "A detailed 2-3 paragraph factual legal scenario requiring drafting or identification",
  "instructions": "Specific drafting prompt for the student",
  "hints": ["Hint 1", "Hint 2"],
  "model_solution": "Exemplary reference clause or answer",
  "rubric_checklist": ["Criterion 1 to verify", "Criterion 2 to verify"]
}}
"""
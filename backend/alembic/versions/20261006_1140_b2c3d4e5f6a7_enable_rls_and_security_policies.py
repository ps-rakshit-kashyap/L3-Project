"""enable_rls_and_security_policies

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-10-06 11:40:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = [
    'alembic_version',
    'companies',
    'jobs',
    'users',
    'candidates',
    'resumes',
    'applications',
    'screening_results',
    'interview_results',
    'final_evaluations',
    'knowledge_documents',
    'document_chunks',
]


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # 1. Enable Row Level Security on all public tables and grant service_role full control
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"DROP POLICY IF EXISTS service_role_manage_{table} ON {table};")
        op.execute(f"CREATE POLICY service_role_manage_{table} ON {table} FOR ALL TO service_role USING (true) WITH CHECK (true);")

    # 2. Add authenticated role policies for client/PostgREST access
    # Jobs: authenticated users can read jobs
    op.execute("DROP POLICY IF EXISTS authenticated_select_jobs ON jobs;")
    op.execute("CREATE POLICY authenticated_select_jobs ON jobs FOR SELECT TO authenticated USING (true);")

    # Companies: authenticated users can read companies
    op.execute("DROP POLICY IF EXISTS authenticated_select_companies ON companies;")
    op.execute("CREATE POLICY authenticated_select_companies ON companies FOR SELECT TO authenticated USING (true);")

    # Users: authenticated users can read their own profile
    op.execute("DROP POLICY IF EXISTS authenticated_select_users ON users;")
    op.execute("CREATE POLICY authenticated_select_users ON users FOR SELECT TO authenticated USING (auth_user_id = auth.uid());")

    # Candidates: candidate can view their own profile
    op.execute("DROP POLICY IF EXISTS authenticated_select_candidates ON candidates;")
    op.execute("CREATE POLICY authenticated_select_candidates ON candidates FOR SELECT TO authenticated USING (user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()));")

    # Resumes: candidate can view their own resumes
    op.execute("DROP POLICY IF EXISTS authenticated_select_resumes ON resumes;")
    op.execute("CREATE POLICY authenticated_select_resumes ON resumes FOR SELECT TO authenticated USING (candidate_id IN (SELECT id FROM candidates WHERE user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())));")

    # Applications: candidate can view their own applications
    op.execute("DROP POLICY IF EXISTS authenticated_select_applications ON applications;")
    op.execute("CREATE POLICY authenticated_select_applications ON applications FOR SELECT TO authenticated USING (candidate_id IN (SELECT id FROM candidates WHERE user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid())));")

    # Screening results: candidate can view results for their own applications
    op.execute("DROP POLICY IF EXISTS authenticated_select_screening_results ON screening_results;")
    op.execute("CREATE POLICY authenticated_select_screening_results ON screening_results FOR SELECT TO authenticated USING (application_id IN (SELECT id FROM applications WHERE candidate_id IN (SELECT id FROM candidates WHERE user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()))));")

    # Interview results: candidate can view results for their own applications
    op.execute("DROP POLICY IF EXISTS authenticated_select_interview_results ON interview_results;")
    op.execute("CREATE POLICY authenticated_select_interview_results ON interview_results FOR SELECT TO authenticated USING (application_id IN (SELECT id FROM applications WHERE candidate_id IN (SELECT id FROM candidates WHERE user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()))));")

    # Final evaluations: candidate can view results for their own applications
    op.execute("DROP POLICY IF EXISTS authenticated_select_final_evaluations ON final_evaluations;")
    op.execute("CREATE POLICY authenticated_select_final_evaluations ON final_evaluations FOR SELECT TO authenticated USING (application_id IN (SELECT id FROM applications WHERE candidate_id IN (SELECT id FROM candidates WHERE user_id IN (SELECT id FROM users WHERE auth_user_id = auth.uid()))));")

    # Knowledge documents & chunks: authenticated can view
    op.execute("DROP POLICY IF EXISTS authenticated_select_knowledge_documents ON knowledge_documents;")
    op.execute("CREATE POLICY authenticated_select_knowledge_documents ON knowledge_documents FOR SELECT TO authenticated USING (true);")

    op.execute("DROP POLICY IF EXISTS authenticated_select_document_chunks ON document_chunks;")
    op.execute("CREATE POLICY authenticated_select_document_chunks ON document_chunks FOR SELECT TO authenticated USING (true);")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # Drop authenticated policies
    for pol, tbl in [
        ("authenticated_select_jobs", "jobs"),
        ("authenticated_select_companies", "companies"),
        ("authenticated_select_users", "users"),
        ("authenticated_select_candidates", "candidates"),
        ("authenticated_select_resumes", "resumes"),
        ("authenticated_select_applications", "applications"),
        ("authenticated_select_screening_results", "screening_results"),
        ("authenticated_select_interview_results", "interview_results"),
        ("authenticated_select_final_evaluations", "final_evaluations"),
        ("authenticated_select_knowledge_documents", "knowledge_documents"),
        ("authenticated_select_document_chunks", "document_chunks"),
    ]:
        op.execute(f"DROP POLICY IF EXISTS {pol} ON {tbl};")

    for table in TABLES:
        op.execute(f"DROP POLICY IF EXISTS service_role_manage_{table} ON {table};")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

"""add_phase4_screening_and_job_fields

Revision ID: a1b2c3d4e5f6
Revises: 543005c045f1
Create Date: 2026-10-06 11:20:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '543005c045f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Job model fields
    op.add_column('jobs', sa.Column('required_skills', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('preferred_skills', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('required_experience', sa.String(length=255), nullable=True))
    op.add_column('jobs', sa.Column('education_requirements', sa.String(length=255), nullable=True))

    # 2. Resume extracted text cache
    op.add_column('resumes', sa.Column('extracted_text', sa.Text(), nullable=True))

    # 3. Screening result structured output fields
    op.add_column('screening_results', sa.Column('recommendation', sa.String(length=50), nullable=True))
    op.add_column('screening_results', sa.Column('details', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('screening_results', 'details')
    op.drop_column('screening_results', 'recommendation')
    op.drop_column('resumes', 'extracted_text')
    op.drop_column('jobs', 'education_requirements')
    op.drop_column('jobs', 'required_experience')
    op.drop_column('jobs', 'preferred_skills')
    op.drop_column('jobs', 'required_skills')

"""add_auth_user_id_and_rbac

Revision ID: 543005c045f1
Revises: cd852c1bb160
Create Date: 2026-10-05 09:29:10.445925+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '543005c045f1'
down_revision: Union[str, None] = 'cd852c1bb160'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('candidates', sa.Column('user_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_candidates_user_id'), 'candidates', ['user_id'], unique=False)
    op.create_foreign_key('fk_candidates_user_id_users', 'candidates', 'users', ['user_id'], ['id'], ondelete='SET NULL')
    op.add_column('users', sa.Column('auth_user_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_users_auth_user_id'), 'users', ['auth_user_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_auth_user_id'), table_name='users')
    op.drop_column('users', 'auth_user_id')
    op.drop_constraint('fk_candidates_user_id_users', 'candidates', type_='foreignkey')
    op.drop_index(op.f('ix_candidates_user_id'), table_name='candidates')
    op.drop_column('candidates', 'user_id')

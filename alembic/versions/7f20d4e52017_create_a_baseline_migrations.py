"""Create a baseline migrations

Revision ID: 7f20d4e52017
Revises: 
Create Date: 2024-01-28 21:54:33.805372

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f20d4e52017'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('sentence',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.Date(), nullable=True),
    sa.Column('foreign_language', sa.String(), nullable=True),
    sa.Column('mother_tongue', sa.String(), nullable=True),
    sa.Column('foreign_idiom', sa.String(), nullable=True),
    sa.Column('mother_idiom', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.Date(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('age', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('repeat_password', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('notebook',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('created_at', sa.Date(), nullable=True),
    sa.Column('updated_at', sa.Date(), nullable=True),
    sa.Column('list_size', sa.Integer(), nullable=True),
    sa.Column('days_period', sa.Integer(), nullable=True),
    sa.Column('foreign_idiom', sa.String(length=100), nullable=True),
    sa.Column('mother_idiom', sa.String(length=100), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('page_section',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('section_number', sa.Integer(), nullable=True),
    sa.Column('page_number', sa.Integer(), nullable=True),
    sa.Column('group', sa.String(length=2), nullable=True),
    sa.Column('created_at', sa.Date(), nullable=True),
    sa.Column('distillation_at', sa.Date(), nullable=True),
    sa.Column('distillated', sa.Boolean(), nullable=True),
    sa.Column('distillation_actual', sa.Date(), nullable=True),
    sa.Column('translated_sentences', sa.String(), nullable=True),
    sa.Column('memorializeds', sa.String(), nullable=True),
    sa.Column('notebook_id', sa.Integer(), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['created_by_id'], ['page_section.id'], ),
    sa.ForeignKeyConstraint(['notebook_id'], ['notebook.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pagesection_sentence_assoc',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.Date(), nullable=True),
    sa.Column('pagesection_id', sa.Integer(), nullable=True),
    sa.Column('sentence_id', sa.Integer(), nullable=True),
    sa.Column('page', sa.Integer(), nullable=True),
    sa.Column('group', sa.String(length=2), nullable=True),
    sa.Column('memorialized', sa.Boolean(), nullable=True),
    sa.Column('distillated', sa.Boolean(), nullable=True),
    sa.Column('notebook_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['pagesection_id'], ['page_section.id'], ),
    sa.ForeignKeyConstraint(['sentence_id'], ['sentence.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pagesection_sentence_assoc')
    op.drop_table('page_section')
    op.drop_table('notebook')
    op.drop_table('user')
    op.drop_table('sentence')
    # ### end Alembic commands ###
"""Initial migrations

Revision ID: c146ef11fc29
Revises: 
Create Date: 2023-11-06 14:41:05.561697

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c146ef11fc29'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('domains',
    sa.Column('cloudflare_domain_id', sa.String(length=64), nullable=True),
    sa.Column('domain_name', sa.String(length=128), nullable=True),
    sa.Column('has_zone', sa.SmallInteger(), nullable=True),
    sa.Column('checked_at', sa.Integer(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('domain_name')
    )
    op.create_index(op.f('ix_domains_cloudflare_domain_id'), 'domains', ['cloudflare_domain_id'], unique=False)
    op.create_index(op.f('ix_domains_created_at'), 'domains', ['created_at'], unique=False)
    op.create_index(op.f('ix_domains_id'), 'domains', ['id'], unique=False)
    op.create_index(op.f('ix_domains_updated_at'), 'domains', ['updated_at'], unique=False)
    op.create_table('domain_dns_queue',
    sa.Column('domain_id', sa.BigInteger(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('task', sa.Integer(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.Integer(), nullable=False),
    sa.Column('updated_at', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_domain_dns_queue_created_at'), 'domain_dns_queue', ['created_at'], unique=False)
    op.create_index(op.f('ix_domain_dns_queue_id'), 'domain_dns_queue', ['id'], unique=False)
    op.create_index(op.f('ix_domain_dns_queue_updated_at'), 'domain_dns_queue', ['updated_at'], unique=False)
    op.create_table('domain_records',
    sa.Column('cloudflare_dns_record_id', sa.String(length=64), nullable=True),
    sa.Column('domain_id', sa.BigInteger(), nullable=True),
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('record_type', sa.String(length=300), nullable=True),
    sa.Column('record_content', sa.String(length=1000), nullable=True),
    sa.Column('record_proxied', sa.SmallInteger(), nullable=True),
    sa.Column('record_ttl', sa.Integer(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.ForeignKeyConstraint(['domain_id'], ['domains.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_domain_records_cloudflare_dns_record_id'), 'domain_records', ['cloudflare_dns_record_id'], unique=False)
    op.create_index(op.f('ix_domain_records_id'), 'domain_records', ['id'], unique=False)
    op.create_table('domain_dns_log',
    sa.Column('queue_id', sa.BigInteger(), nullable=True),
    sa.Column('task', sa.Integer(), nullable=True),
    sa.Column('response', sa.Text(), nullable=True),
    sa.Column('response_http_code', sa.Integer(), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.ForeignKeyConstraint(['queue_id'], ['domain_dns_queue.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_domain_dns_log_id'), 'domain_dns_log', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_domain_dns_log_id'), table_name='domain_dns_log')
    op.drop_table('domain_dns_log')
    op.drop_index(op.f('ix_domain_records_id'), table_name='domain_records')
    op.drop_index(op.f('ix_domain_records_cloudflare_dns_record_id'), table_name='domain_records')
    op.drop_table('domain_records')
    op.drop_index(op.f('ix_domain_dns_queue_updated_at'), table_name='domain_dns_queue')
    op.drop_index(op.f('ix_domain_dns_queue_id'), table_name='domain_dns_queue')
    op.drop_index(op.f('ix_domain_dns_queue_created_at'), table_name='domain_dns_queue')
    op.drop_table('domain_dns_queue')
    op.drop_index(op.f('ix_domains_updated_at'), table_name='domains')
    op.drop_index(op.f('ix_domains_id'), table_name='domains')
    op.drop_index(op.f('ix_domains_created_at'), table_name='domains')
    op.drop_index(op.f('ix_domains_cloudflare_domain_id'), table_name='domains')
    op.drop_table('domains')
    # ### end Alembic commands ###
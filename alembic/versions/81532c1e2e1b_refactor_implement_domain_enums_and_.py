"""refactor: implement domain enums and modularize schema

Revision ID: 81532c1e2e1b
Revises: 
Create Date: 2026-04-14 14:23:30.468808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '81532c1e2e1b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # Manually create Enum types in DB (if not exists)
    # Using 'execute' because 'create' fails if types were partially created
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'luretype') THEN CREATE TYPE luretype AS ENUM ('essence', 'spirit', 'pure'); END IF; END $$;")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'essencetype') THEN CREATE TYPE essencetype AS ENUM ('Earth', 'Wind', 'Fire', 'Arcane', 'Water'); END IF; END $$;")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'encountertype') THEN CREATE TYPE encountertype AS ENUM ('essence', 'spirit'); END IF; END $$;")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'rarity') THEN CREATE TYPE rarity AS ENUM ('common', 'uncommon', 'rare', 'legendary'); END IF; END $$;")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'spirittype') THEN CREATE TYPE spirittype AS ENUM ('Feline', 'Canine', 'Winged', 'Goblin', 'Restless'); END IF; END $$;")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'resonancemode') THEN CREATE TYPE resonancemode AS ENUM ('echo', 'pulse', 'attract'); END IF; END $$;")

    lure_type = postgresql.ENUM('essence', 'spirit', 'pure', name='luretype')
    essence_type = postgresql.ENUM('Earth', 'Wind', 'Fire', 'Arcane', 'Water', name='essencetype')
    encounter_type = postgresql.ENUM('essence', 'spirit', name='encountertype')
    rarity_type = postgresql.ENUM('common', 'uncommon', 'rare', 'legendary', name='rarity')
    spirit_type = postgresql.ENUM('Feline', 'Canine', 'Winged', 'Goblin', 'Restless', name='spirittype')
    resonance_mode_type = postgresql.ENUM('echo', 'pulse', 'attract', name='resonancemode')

    # Drop defaults that might block type changes
    op.execute("ALTER TABLE familiars ALTER COLUMN resonance_mode DROP DEFAULT")
    op.execute("ALTER TABLE channel_configs ALTER COLUMN activity_score DROP DEFAULT")
    op.execute("ALTER TABLE channel_configs ALTER COLUMN pity_count DROP DEFAULT")
    op.execute("ALTER TABLE familiars ALTER COLUMN growth_bonus DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN stored_essence_lure_mins DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN stored_spirit_lure_mins DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN stored_pure_lure_mins DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN daily_resonance_count DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN has_seen_essence_tip DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN has_seen_spirit_tip DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN has_seen_familiar_tip DROP DEFAULT")

    # Now alter columns with USING
    op.alter_column('channel_configs', 'activity_score',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('channel_configs', 'pity_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    
    op.alter_column('channel_configs', 'active_lure_type',
               existing_type=sa.VARCHAR(length=20),
               type_=lure_type,
               existing_nullable=True,
               postgresql_using='active_lure_type::luretype')
    
    op.alter_column('channel_configs', 'active_lure_subtype',
               existing_type=sa.VARCHAR(length=20),
               type_=essence_type,
               existing_nullable=True,
               postgresql_using='active_lure_subtype::essencetype')
    
    op.alter_column('encounters', 'type',
               existing_type=sa.VARCHAR(length=20),
               type_=encounter_type,
               existing_nullable=False,
               postgresql_using='type::encountertype')
    
    op.alter_column('encounters', 'rarity',
               existing_type=sa.VARCHAR(length=20),
               type_=rarity_type,
               existing_nullable=True,
               postgresql_using='rarity::rarity')
    
    op.alter_column('essences', 'type',
               existing_type=sa.VARCHAR(length=20),
               type_=essence_type,
               existing_nullable=False,
               postgresql_using='type::essencetype')
    
    op.alter_column('familiars', 'spirit_type',
               existing_type=sa.VARCHAR(length=20),
               type_=spirit_type,
               existing_nullable=False,
               postgresql_using='spirit_type::spirittype')
    
    op.alter_column('familiars', 'essence_type',
               existing_type=sa.VARCHAR(length=20),
               type_=essence_type,
               existing_nullable=False,
               postgresql_using='essence_type::essencetype')
    
    op.alter_column('familiars', 'rarity',
               existing_type=sa.VARCHAR(length=20),
               type_=rarity_type,
               existing_nullable=False,
               postgresql_using='rarity::rarity')
    
    op.alter_column('familiars', 'growth_bonus',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
    
    op.alter_column('familiars', 'resonance_mode',
               existing_type=sa.VARCHAR(length=20),
               type_=resonance_mode_type,
               nullable=False,
               postgresql_using='resonance_mode::resonancemode')
    
    op.alter_column('familiars', 'attract_element',
               existing_type=sa.VARCHAR(length=20),
               type_=essence_type,
               existing_nullable=True,
               postgresql_using='attract_element::essencetype')
    
    op.alter_column('spirits', 'type',
               existing_type=sa.VARCHAR(length=20),
               type_=spirit_type,
               existing_nullable=False,
               postgresql_using='type::spirittype')
    
    op.alter_column('spirits', 'rarity',
               existing_type=sa.VARCHAR(length=20),
               type_=rarity_type,
               existing_nullable=False,
               postgresql_using='rarity::rarity')
    
    op.alter_column('users', 'stored_essence_lure_mins', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('users', 'stored_spirit_lure_mins', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('users', 'stored_pure_lure_mins', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('users', 'daily_resonance_count', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('users', 'has_seen_essence_tip', existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column('users', 'has_seen_spirit_tip', existing_type=sa.BOOLEAN(), nullable=False)
    op.alter_column('users', 'has_seen_familiar_tip', existing_type=sa.BOOLEAN(), nullable=False)

    # Re-apply defaults with correct types
    op.execute("ALTER TABLE channel_configs ALTER COLUMN activity_score SET DEFAULT 0")
    op.execute("ALTER TABLE channel_configs ALTER COLUMN pity_count SET DEFAULT 0")
    op.execute("ALTER TABLE familiars ALTER COLUMN growth_bonus SET DEFAULT 0.0")
    op.execute("ALTER TABLE familiars ALTER COLUMN resonance_mode SET DEFAULT 'echo'")
    op.execute("ALTER TABLE users ALTER COLUMN stored_essence_lure_mins SET DEFAULT 0")
    op.execute("ALTER TABLE users ALTER COLUMN stored_spirit_lure_mins SET DEFAULT 0")
    op.execute("ALTER TABLE users ALTER COLUMN stored_pure_lure_mins SET DEFAULT 0")
    op.execute("ALTER TABLE users ALTER COLUMN daily_resonance_count SET DEFAULT 0")
    op.execute("ALTER TABLE users ALTER COLUMN has_seen_essence_tip SET DEFAULT FALSE")
    op.execute("ALTER TABLE users ALTER COLUMN has_seen_spirit_tip SET DEFAULT FALSE")
    op.execute("ALTER TABLE users ALTER COLUMN has_seen_familiar_tip SET DEFAULT FALSE")


def downgrade() -> None:
    """Downgrade schema."""
    # This is a complex refactor, downgrade is not strictly necessary for MVP but good practice
    # For now, let's keep it simple or empty as the focus is hardening the move forward.
    pass

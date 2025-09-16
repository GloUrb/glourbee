"""create table image

Revision ID: 1226738ec11d
Revises: 159b81fb0bfc
Create Date: 2025-09-16 10:59:48.589635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1226738ec11d'
down_revision: Union[str, None] = '159b81fb0bfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql = """
CREATE TABLE IF NOT EXISTS public.image
(
    fid integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    name text COLLATE pg_catalog."default" NOT NULL,
    date date NOT NULL,
    "user" text COLLATE pg_catalog."default" NOT NULL DEFAULT 'all'::text,
    path text COLLATE pg_catalog."default",
    satellite text COLLATE pg_catalog."default",
    geometry geometry(Polygon,3857) NOT NULL,
    CONSTRAINT image_pkey PRIMARY KEY (fid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.image
    OWNER to glourbee_user;
"""
    op.execute(sql)

def downgrade() -> None:
    sql = "DROP TABLE IF EXISTS public.image;"
    op.execute(sql)

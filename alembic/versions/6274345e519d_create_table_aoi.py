"""create table aoi

Revision ID: 6274345e519d
Revises: 
Create Date: 2025-09-15 18:32:06.350291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6274345e519d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql = """
CREATE TABLE IF NOT EXISTS public.aoi
(
    fid integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    type text COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default" NOT NULL,
    author text COLLATE pg_catalog."default" NOT NULL,
    last_access timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geometry geometry(MultiPolygon,3857) NOT NULL,
    CONSTRAINT aoi_pkey PRIMARY KEY (fid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.aoi
    OWNER to glourbee_user;
"""
    op.execute(sql)

def downgrade() -> None:
    sql = "DROP TABLE IF EXISTS public.aoi;"
    op.execute(sql)

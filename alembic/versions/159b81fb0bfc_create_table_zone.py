"""create table zone

Revision ID: 159b81fb0bfc
Revises: 6274345e519d
Create Date: 2025-09-16 10:59:39.287639

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '159b81fb0bfc'
down_revision: Union[str, None] = '6274345e519d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sql = """
CREATE TABLE IF NOT EXISTS public.zone
(
    fid integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    aoi_fid integer NOT NULL,
    zone_fid integer NOT NULL,
    geometry geometry(MultiPolygon,3857) NOT NULL,
    CONSTRAINT zone_pkey PRIMARY KEY (fid),
    CONSTRAINT aoi_fid FOREIGN KEY (aoi_fid)
        REFERENCES public.aoi (fid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.zone
    OWNER to glourbee_user;
"""
    op.execute(sql)


def downgrade() -> None:
    sql = 'DROP TABLE IF EXISTS public.zone;'
    op.execute(sql)

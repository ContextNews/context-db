from eralchemy2 import render_er
from rds_postgres.models import Base

render_er(Base, "erd.png")
print("ERD written to erd.png")

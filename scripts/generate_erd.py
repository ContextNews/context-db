from eralchemy2 import render_er
from context_db.models import Base

render_er(Base, "erd.png")
print("ERD written to erd.png")

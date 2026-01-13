from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PersonMigration(Base):
    """
    This is perons migration table where we keep track of which perons is migrated
    """
    __tablename__ = "person_migration"
    id: Mapped[int] = mapped_column(primary_key=True)
    old_person_id = Column(String)
    old_person_bdrc_id = Column(String)
    new_person_id = Column(String)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "old_person_id": self.old_person_id,
            "old_person_bdrc_id": self.old_person_bdrc_id,
            "new_person_id": self.new_person_id,
        }

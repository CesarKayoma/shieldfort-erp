from datetime import datetime, timezone
from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    criado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now
    )

    atualizado_em = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now
    )



    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
"""
Schema od DB.

autogen command: alembic revision --autogenerate -m "msg"

"""
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User table schema."""

    __tablename__ = 'user'
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String, nullable=False, unique=True)
    password_hash = sa.Column(sa.String)


class Letter(Base):
    """Letter table schema."""

    __tablename__ = 'letter'
    id = sa.Column(sa.Integer, primary_key=True)
    id_external = sa.Column(sa.Integer)  # id from mail server
    sender = sa.Column(sa.String, nullable=False)  # from
    to = sa.Column(sa.String, nullable=False, default=' ')
    subject = sa.Column(sa.String, nullable=True)
    body = sa.Column(sa.String, nullable=False, default=' ')
    user = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    size = sa.Column(sa.Integer, nullable=False)
    star = sa.Column(sa.Integer, sa.ForeignKey('star.id'), nullable=True)
    ts = sa.Column(sa.DateTime, nullable=False)  #  e.g. `Tue, 18 Jan 2022 09:37:29 +0300`
    mailbox = sa.Column(sa.Integer, sa.ForeignKey('mailbox.id'), nullable=False)
    is_important = sa.Column(sa.Boolean, default=False)
    is_read = sa.Column(sa.Boolean, nullable=False)


class Star(Base):
    """Letter flag table schema."""

    __tablename__ = 'star'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False, unique=True)


class MailBox(Base):
    """MailBox table schema."""

    __tablename__ = 'mailbox'
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False, unique=False)
    is_custom = sa.Column(sa.Boolean, default=True)
    user = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=True)

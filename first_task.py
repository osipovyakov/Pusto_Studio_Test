from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Interval, text
from sqlalchemy.orm import relationship, declarative_base, sessionmaker, Mapped, mapped_column
from datetime import datetime
from typing import Optional, Annotated


Base = declarative_base()
intpk = Annotated[int, mapped_column(primary_key=True)]

class Player(Base):
    __tablename__ = 'players'

    id: Mapped[intpk]
    first_login: Mapped[Optional[DateTime]] = mapped_column(
        nullable=True,
        server_default=text("TIMEZONE('utc', now())")
        )
    last_login: Mapped[Optional[DateTime]] = mapped_column(
        nullable=True,
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.utcnow,
        )
    daily_points: Mapped[int] = mapped_column(default=0)
    total_points: Mapped[int] = mapped_column(default=0)

    boosts = relationship("PlayerBoost", back_populates="player")


    def __repr__(self):
        return f"<Player(id={self.id}, total_points={self.total_points})>"


class Boost(Base):
    __tablename__ = 'boosts'

    id: Mapped[intpk]
    type: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(String(256))
    duration: Mapped[int] = mapped_column(server_default=3600)


    def __repr__(self):
        return f"<Boost(type={self.type})>"


class PlayerBoost(Base):
    __tablename__ = 'player_boosts'

    id: Mapped[intpk]
    player_id: Mapped[int] = mapped_column(ForeignKey('players.id', ondelete='CASCADE'))
    boost_id: Mapped[int] = mapped_column(ForeignKey('boosts.id', ondelete='CASCADE'))
    assigned_at: Mapped[DateTime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))

    player = relationship("Player", back_populates="boosts")
    boost = relationship("Boost")


    def __repr__(self):
        return f"<PlayerBoost(player_id={self.player_id}, boost_id={self.boost_id})>"


engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

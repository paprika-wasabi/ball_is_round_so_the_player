from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+mysqlconnector://root:my-secret-pw@localhost/footballplayers_analysis",
    echo=True  # Set to False to disable SQL query logging
)

Base = declarative_base()

from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    person_id = Column(String(50), unique=True)
    shirt_number = Column(String(10))
    team = Column(String(100))

    match_participations = relationship("PlayerMatch", back_populates="player", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Player(person_id='{self.person_id}', name='{self.first_name} {self.last_name}', shirt_number={self.shirt_number}, team='{self.team}')>"

class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    match_id = Column(String(50), unique=True)

    player_participations = relationship("PlayerMatch", back_populates="match", cascade="all, delete-orphan")

class PlayerMatch(Base):
    """
    Association object between Player and Match.
    Holds multiple Position records.
    """
    __tablename__ = 'player_matches'

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'))
    match_id = Column(Integer, ForeignKey('matches.id'))

    player = relationship("Player", back_populates="match_participations")
    match = relationship("Match", back_populates="player_participations")
    positions = relationship("Position", back_populates="player_match", cascade="all, delete-orphan")

class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    player_match_id = Column(Integer, ForeignKey('player_matches.id'))

    x = Column(Float)        # x coordinate on the field
    y = Column(Float)        # y coordinate on the field
    frame_number = Column(Integer)  # Frame number in the video
    timestamp = Column(DateTime)  # in seconds (or milliseconds)

    player_match = relationship("PlayerMatch", back_populates="positions")


# Create the tables
Base.metadata.create_all(engine)
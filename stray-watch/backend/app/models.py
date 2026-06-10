from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

# This is the base class that all our table classes will inherit from.
# Think of it as the foundation — SQLAlchemy needs this to track all tables.
Base = declarative_base()


class Locality(Base):
    """
    Represents a geographic zone/area in the city.
    Example: T. Nagar, Adyar, Anna Nagar
    Created first because Dog and Alert tables refer to it.
    """
    __tablename__ = "localities"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False, unique=True)  # e.g. "T. Nagar"
    lat         = Column(Float, nullable=False)   # latitude  e.g. 13.0418
    lng         = Column(Float, nullable=False)   # longitude e.g. 80.2341
    risk_score  = Column(Integer, default=0)      # 0–100, calculated by your algorithm
    last_survey = Column(DateTime, nullable=True) # when was this locality last checked

    # These let you do locality.dogs to get all dogs in this area
    dogs     = relationship("Dog",      back_populates="locality")
    sightings = relationship("Sighting", back_populates="locality")
    alerts   = relationship("Alert",    back_populates="locality")

    def __repr__(self):
        return f"<Locality {self.name} | risk={self.risk_score}>"


class Dog(Base):
    """
    Represents one individual stray dog in the registry.
    Each dog gets a unique dog_code like DOG-0041.
    """
    __tablename__ = "dogs"

    id               = Column(Integer, primary_key=True, index=True)
    dog_code         = Column(String(20),  nullable=False, unique=True) # e.g. "DOG-0041"
    locality_id      = Column(Integer, ForeignKey("localities.id"), nullable=False)
    sex              = Column(String(10),  nullable=True)   # "male" / "female" / "unknown"
    color            = Column(String(50),  nullable=True)   # e.g. "brown", "black and white"
    photo_path       = Column(String(255), nullable=True)   # path or URL to the dog's photo
    embedding_vector = Column(JSON,        nullable=True)   # MobileNet 1280-dim vector stored as list
    vaccinated       = Column(Boolean,     default=False)
    vax_date         = Column(DateTime,    nullable=True)   # date vaccination was given
    vax_expiry       = Column(DateTime,    nullable=True)   # date vaccination expires
    sterilized       = Column(Boolean,     default=False)   # ABC program status
    notes            = Column(Text,        nullable=True)   # any extra observations
    created_at       = Column(DateTime,    default=datetime.utcnow)

    # Relationships
    locality  = relationship("Locality",  back_populates="dogs")
    sightings = relationship("Sighting",  back_populates="dog")

    def __repr__(self):
        return f"<Dog {self.dog_code} | {self.color} | vaccinated={self.vaccinated}>"


class Sighting(Base):
    """
    Every time a volunteer spots and reports a dog, a sighting is logged.
    One dog can have many sightings over time — this tracks movement.
    """
    __tablename__ = "sightings"

    id          = Column(Integer, primary_key=True, index=True)
    dog_id      = Column(Integer, ForeignKey("dogs.id"),       nullable=False)
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=False)
    spotted_at  = Column(DateTime, default=datetime.utcnow)   # when it was seen
    lat         = Column(Float, nullable=True)  # exact GPS lat where spotted
    lng         = Column(Float, nullable=True)  # exact GPS lng where spotted

    # Relationships
    dog      = relationship("Dog",      back_populates="sightings")
    locality = relationship("Locality", back_populates="sightings")

    def __repr__(self):
        return f"<Sighting dog={self.dog_id} at {self.spotted_at}>"


class Alert(Base):
    """
    System-generated warnings about a locality's dog situation.
    Examples: low vaccination coverage, expired vaccines, unregistered dogs spotted.
    """
    __tablename__ = "alerts"

    id          = Column(Integer, primary_key=True, index=True)
    type        = Column(String(50),  nullable=False)  # "low_coverage" / "vax_expiring" / "unregistered"
    locality_id = Column(Integer, ForeignKey("localities.id"), nullable=True)
    message     = Column(Text,        nullable=False)  # human-readable description
    severity    = Column(String(10),  nullable=False)  # "high" / "medium" / "info"
    is_resolved = Column(Boolean,     default=False)   # mark True once acted upon
    created_at  = Column(DateTime,    default=datetime.utcnow)

    # Relationship
    locality = relationship("Locality", back_populates="alerts")

    def __repr__(self):
        return f"<Alert [{self.severity}] {self.type} | resolved={self.is_resolved}>"
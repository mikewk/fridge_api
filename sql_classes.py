from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Table, func
from sqlalchemy.orm import relationship
from db import get_db

db = get_db()
Base = db.Model

users_households_association = Table('users_households', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE')),
    Column('household_id', Integer, ForeignKey('households.id', ondelete='CASCADE'))
)


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255))
    passwordHash = Column(String(256))
    fullName = Column(String(100))
    lastLogin = Column(DateTime(timezone=True))
    favoriteStorageId = Column(Integer, ForeignKey("storages.id"), nullable=True)
    
    favoriteStorage = relationship("Storage", uselist=False)
    households = relationship("Household", secondary=users_households_association)
    ownedHouseholds = relationship("Household", foreign_keys="Household.ownerId", passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.fullName
        }


class Household(Base):
    __tablename__ = "households"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    location = Column(String(255))
    ownerId = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    folder = Column(String(37))
    
    owner = relationship("User", back_populates="ownedHouseholds", foreign_keys=[ownerId])
    users = relationship("User", secondary=users_households_association, back_populates="households")
    storages = relationship("Storage", back_populates="household", passive_deletes=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "folder": self.folder,
            "owner": self.owner.to_dict(),
            "storages": map(lambda x: x.to_dict(), self.storages)
        }


class Storage(Base):
    __tablename__ = "storages"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(String(50))
    householdId = Column(Integer, ForeignKey("households.id", ondelete='CASCADE'))
    
    household = relationship("Household", back_populates="storages", foreign_keys=[householdId])
    foodItems = relationship("FoodItem", back_populates="storage", passive_deletes=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "foodItems": map(lambda x: x.to_dict(), self.foodItems)
        }


class FoodItem(Base):
    __tablename__ = "food_items"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    storageId = Column(Integer, ForeignKey("storages.id", ondelete='CASCADE'))
    dateEntered = Column(DateTime(timezone=True), server_default=func.now())
    enteredById = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    expiration = Column(DateTime(timezone=True))
    filename = Column(String(255))

    storage = relationship("Storage", back_populates="foodItems")
    enteredBy = relationship("User")
    tags = relationship("Tag", back_populates="foodItem", passive_deletes=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "storageName": self.storage.name,
            "enteredBy": self.enteredBy.to_dict(),
            "entered": str(self.dateEntered),
            "expiration": self.expiration,
            "filename": self.filename,
            "tags": map(lambda x: x.tag, self.tags)
        }


class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    foodItemId = Column(Integer, ForeignKey("food_items.id", ondelete='CASCADE'))
    tag = Column(String(100))
    foodItem = relationship("FoodItem", back_populates="tags")

    def to_dict(self):
        return {
            "id": self.id,
            "tag": self.tag,
        }


class Invite(Base):
    __tablename__ = "invites"

    id = Column(Integer, primary_key=True)
    householdId = Column(Integer, ForeignKey("households.id", ondelete='CASCADE'))
    invitee = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    message = Column(String(255))
    status = Column(Integer)

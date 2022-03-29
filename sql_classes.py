from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Table, func, event
from sqlalchemy.orm import relationship

from api import access_key, secret_key
from db import get_db
import boto3

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
    defaultHouseholdId = Column(Integer, ForeignKey("households.id"), nullable=True)
    
    favoriteStorage = relationship("Storage", uselist=False)
    households = relationship("Household", secondary=users_households_association)
    ownedHouseholds = relationship("Household", foreign_keys="Household.ownerId", passive_deletes=True)
    defaultHousehold = relationship("Household", uselist=False, foreign_keys="User.defaultHouseholdId")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.fullName,
            "defaultHousehold": self.defaultHousehold.to_dict() if self.defaultHousehold else None,
            "memberHouseholds": map(lambda x: x.to_dict(), self.households),
            "ownedHouseholds": map(lambda x: x.to_dict(), self.ownedHouseholds)
        }

    def to_dict_no_recursion(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.fullName,
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
    invites = relationship("Invite", back_populates="household", passive_deletes=True)

    def delete(self):
        # Remove item from S3
        print("Deleting "+self.folder+" from S3\n")
        s3 = boto3.client("s3",
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
        s3.delete_object(Bucket="fridge-app-photos-dev", Key=self.folder)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "folder": self.folder,
            "owner": self.owner.to_dict_no_recursion(),
            "storages": map(lambda x: x.to_dict(), self.storages)
        }

    def to_dict_no_recursion(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "folder": self.folder,
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

    def delete(self):
        print("Deleting all food items in "+self.name)
        # Remove food items from S3
        for foodItem in self.foodItems:
            foodItem.delete()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "foodItems": map(lambda x: x.to_dict(), self.foodItems)
        }

    def to_dict_no_recursion(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "foodItems": []
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

    def delete(self):
        # Remove item from S3
        print("Deleting "+self.filename+" from S3\n")
        s3 = boto3.client("s3",
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
        s3.delete_object(Bucket="fridge-app-photos-dev", Key=self.filename)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "storage": self.storage.to_dict_no_recursion(),
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

    id = Column(String(38), primary_key=True)
    householdId = Column(Integer, ForeignKey("households.id", ondelete='CASCADE'))
    inviteeId = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    message = Column(String(255))
    status = Column(Integer)

    household = relationship("Household", uselist=False, back_populates="invites")
    invitee = relationship("User", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "householdName": self.household.name,
            "message": self.message,
            "status": self.status,
            "inviteeName": self.invitee.fullName if self.invitee else "",
            "inviterName": self.household.owner.fullName
        }


@event.listens_for(FoodItem, 'after_delete')
def receive_after_delete(mapper, connection, target):
    target.delete()


@event.listens_for(Storage, 'after_delete')
def receive_after_delete(mapper, connection, target):
    target.delete()


@event.listens_for(Household, 'after_delete')
def receive_after_delete(mapper, connection, target):
    target.delete()

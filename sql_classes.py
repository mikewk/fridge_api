import configparser
import boto3
import os

from datetime import timedelta, datetime, timezone

from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Table, func, event
from sqlalchemy.orm import relationship

from db import get_db

config = configparser.ConfigParser()
config.read(os.getenv("SECRET_PATH"))
access_key = config["auth"]["awsid"]
secret_key = config["auth"]["awssecret"]

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
    salt = Column(String(37))
    
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
            "memberHouseholds": [x.to_dict() for x in self.households],
            "ownedHouseholds": [x.to_dict() for x in self.ownedHouseholds]
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
    
    owner = relationship("User", back_populates="ownedHouseholds", foreign_keys=[ownerId], lazy="joined")
    users = relationship("User", secondary=users_households_association, back_populates="households")
    storages = relationship("Storage", back_populates="household", passive_deletes="all", lazy="joined")
    invites = relationship("Invite", back_populates="household", passive_deletes=True)

    def delete(self):
        # Remove item from S3
        print("Deleting storages")
        for storage in self.storages:
            print("Deleting "+storage.name)
            storage.delete()

        print("Deleting "+self.folder+" from S3\n")
        s3 = boto3.client("s3",
                          aws_access_key_id=access_key,
                          aws_secret_access_key=secret_key)
        s3.delete_object(Bucket="fridge-app-photos-dev", Key=self.folder+"/")

    def to_dict(self):
        return {
            "_type": "Household",
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "folder": self.folder,
            "owner": self.owner.to_dict_no_recursion(),
            "users": [x.to_dict_no_recursion() for x in self.users],
            "storages": [x.to_dict() for x in self.storages]
        }

    def to_dict_no_recursion(self):
        return {
            "_type": "Household",
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "folder": self.folder,
            "storages": [x.to_dict() for x in self.storages]
        }


class Storage(Base):
    __tablename__ = "storages"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    type = Column(String(50))
    householdId = Column(Integer, ForeignKey("households.id", ondelete='CASCADE'))
    
    household = relationship("Household", back_populates="storages", foreign_keys=[householdId])
    foodItems = relationship("FoodItem", back_populates="storage", passive_deletes="all", lazy="joined")

    def delete(self):
        print("Deleting all food items in "+self.name)
        # Remove food items from S3
        for foodItem in self.foodItems:
            foodItem.delete()

    def to_dict(self):
        return {
            "_type": "Storage",
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "householdId": self.householdId,
            "foodItems": [x.to_dict() for x in self.foodItems]
        }

    def to_dict_no_recursion(self):
        return {
            "_type": "Storage",
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "foodItems": []
        }


def default_expiration():
    expiration = datetime.now(timezone.utc) + timedelta(days=7)
    return expiration


class FoodItem(Base):
    __tablename__ = "food_items"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    storageId = Column(Integer, ForeignKey("storages.id", ondelete='CASCADE'))
    dateEntered = Column(DateTime(timezone=False), server_default=func.now())
    enteredById = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    expiration = Column(DateTime(timezone=False), default=default_expiration)
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
            "_type": "FoodItem",
            "id": self.id,
            "name": self.name,
            "storage": self.storage.to_dict_no_recursion(),
            "enteredBy": self.enteredBy.to_dict_no_recursion(),
            "entered": str(self.dateEntered),
            "expiration": str(self.expiration),
            "filename": self.filename,
            "tags": [x.tag for x in self.tags]
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


class PasswordResets(Base):
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete='SET NULL'))
    token = Column(String(400))
    created = Column(DateTime, server_default=func.now())
    attempted = Column(DateTime)
    status = Column(Integer)
    request_ip = Column(String(255))
    attempt_ip = Column(String(255))

    user = relationship("User", uselist=False)


@event.listens_for(FoodItem, 'after_delete')
def receive_after_delete(mapper, connection, target):
    target.delete()


@event.listens_for(Storage, 'after_delete')
def receive_after_delete(mapper, connection, target):
    target.delete()


@event.listens_for(Household, 'after_delete')
def receive_after_delete(mapper, connection, target):
    target.delete()

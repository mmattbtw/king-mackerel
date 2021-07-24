import datetime
import logging
import database
from peewee import *

log = logging.getLogger()

class BaseModel(Model):
    class Meta:
        database = database.db

def create_tables():
    database.connect()
    database.db.create_tables([User, Fish, FishingRod, FishingBaitInventory])

class User(BaseModel):
    id = AutoField()
    user_id = BigIntegerField(unique=True)
    coins = IntegerField(default=0)
    fish_caught = IntegerField(default=0)
    exp = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.datetime.utcnow())
    last_fished = DateTimeField(null=True)

# One-to-many relationship. One user has 0..n fish that belong to them.
class Fish(BaseModel):
    id = AutoField()
    user = ForeignKeyField(User, backref='fish')
    name = TextField()
    base_value = IntegerField()
    catch_value = IntegerField()
    # Rarities go from worst to best. 0 -> N where N is the best rarity in the game
    rarity = IntegerField()
    weight_kg = DoubleField()
    quality = IntegerField()
    time_caught = DateTimeField()
    minimum_line_thickness_required = DoubleField()

class FishingRod(BaseModel):
    user = ForeignKeyField(User, backref='fishing_rod')
    name = TextField()
    durability = IntegerField()
    line_thickness_support_mm = DoubleField()
    weight_support_kg = DoubleField()
    minimum_level_required = IntegerField()
    max_rarity_possible = IntegerField()
    cast_time = DoubleField()

class FishingBaitInventory(BaseModel):
    user = ForeignKeyField(User, backref='fishing_bait_inventory')
    # A user can't have more than one entry for the same bait type
    bait_type = IntegerField(unique=True)
    amount = IntegerField()
    # Only one bait type can be active at a time for fishing
    active = BooleanField()


from model.household import create_household, update_household
from model.user import get_user
from ariadne import ObjectType, convert_kwargs_to_snake_case
import traceback

mutation = ObjectType("Mutation")

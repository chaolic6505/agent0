"""
Main GraphQL schema for the auction system.
"""

import strawberry
from strawberry.extensions import AddValidationRules
from graphql import ValidationRule
from typing import List
import logging

from .queries import Query
from .mutations import Mutation

# Set up logging
logger = logging.getLogger(__name__)

# Custom validation rule for better error handling
class CustomValidationRule(ValidationRule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info("GraphQL validation rule initialized")

# Create schema with extensions
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        AddValidationRules([CustomValidationRule])
    ]
)
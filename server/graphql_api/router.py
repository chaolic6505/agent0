"""
FastAPI router for GraphQL integration.
"""

from strawberry.fastapi import GraphQLRouter
from .schema import schema

# Export the GraphQL router with GraphiQL playground enabled
router = GraphQLRouter(
    schema,
    graphiql=True,  # Enable GraphQL Playground
    allow_queries_via_get=True  # Allow queries via GET requests
)
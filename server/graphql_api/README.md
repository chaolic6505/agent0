# GraphQL API Documentation

This directory contains the GraphQL implementation for the auction system using Strawberry GraphQL.

## Overview

The GraphQL API provides a type-safe, self-documenting interface for interacting with the auction system. It includes:

- **Queries**: Read operations for users, stories, jobs, auctions, bids, and categories
- **Mutations**: Write operations for creating and updating entities
- **Types**: Strongly-typed GraphQL schema definitions
- **Error Handling**: Comprehensive error handling with logging

## Architecture

```
graphql/
├── router.py      # FastAPI router integration
├── schema.py      # Main GraphQL schema
├── queries.py     # Query resolvers
├── mutations.py   # Mutation resolvers
├── types.py       # GraphQL type definitions
└── README.md      # This documentation
```

## Features

### ✅ Implemented Features

1. **Complete CRUD Operations**
   - User management (create, read)
   - Story management (create, read)
   - Story job management (create, update, read)
   - Auction management (create, update, read)
   - Bid management (create, read)
   - Category management (create, read)
   - Auction item management (create, read)

2. **Error Handling**
   - Database error handling with rollback
   - Input validation
   - Integrity constraint handling
   - Comprehensive logging

3. **Type Safety**
   - Strongly-typed GraphQL schema
   - Input validation
   - Enum support for status fields

4. **Performance**
   - Efficient database queries
   - Proper relationship loading
   - Connection pooling support

## API Endpoints

### GraphQL Endpoint
- **URL**: `/graphql`
- **Method**: POST
- **Content-Type**: `application/json`

### GraphiQL Interface
- **URL**: `/graphql`
- **Method**: GET
- **Description**: Interactive GraphQL playground for development

### Health Check
- **URL**: `/graphql/health`
- **Method**: GET
- **Description**: Health check endpoint

## Example Queries

### Get All Users
```graphql
query {
  users {
    id
    username
  }
}
```

### Get Auction with Bids
```graphql
query {
  auction(id: 1) {
    id
    title
    description
    currentPrice
    status
    bids {
      id
      bidderId
      amount
      status
      createdAt
    }
    auctionItems {
      id
      name
      description
      quantity
    }
  }
}
```

### Create a New Auction
```graphql
mutation {
  createAuction(input: {
    title: "Vintage Watch"
    description: "A beautiful vintage timepiece"
    startingPrice: 100.00
    reservePrice: 150.00
    minBidIncrement: 5.00
    startTime: "2024-01-01T10:00:00"
    endTime: "2024-01-07T18:00:00"
    autoExtendMinutes: 5
    sellerId: 1
    categoryId: 1
  }) {
    id
    title
    status
    currentPrice
    createdAt
  }
}
```

### Place a Bid
```graphql
mutation {
  createBid(input: {
    auctionId: 1
    bidderId: 2
    amount: 120.00
  }) {
    id
    auctionId
    bidderId
    amount
    status
    createdAt
  }
}
```

## Error Handling

The GraphQL API includes comprehensive error handling:

### Database Errors
- Automatic rollback on database errors
- Detailed error logging
- User-friendly error messages

### Validation Errors
- Input validation for all mutations
- Business rule validation (e.g., bid amounts, auction status)
- Clear error messages for validation failures

### Example Error Response
```json
{
  "errors": [
    {
      "message": "Bid amount must be positive",
      "locations": [{"line": 2, "column": 3}],
      "path": ["createBid"]
    }
  ],
  "data": null
}
```

## Type Definitions

### Core Types
- `User`: User information
- `Story`: Story content and metadata
- `StoryNode`: Individual story nodes
- `StoryJob`: Background job for story generation
- `Auction`: Auction details and status
- `Bid`: Bid information
- `Category`: Auction categories
- `AuctionItem`: Items within auctions

### Enums
- `AuctionStatus`: DRAFT, PENDING, ACTIVE, PAUSED, ENDED, CANCELLED, SOLD
- `BidStatus`: PENDING, ACCEPTED, REJECTED, CANCELLED

## Development

### Adding New Queries

1. Add the query method to `queries.py`:
```python
@strawberry.field
def my_query(self, id: int) -> Optional[MyType]:
    """Get my entity by ID."""
    try:
        db = next(get_db())
        entity = db.query(MyModel).filter(MyModel.id == id).first()
        if entity:
            return MyType.from_model(entity)
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error in my_query: {e}")
        raise Exception("Database error occurred")
```

2. Add the corresponding type to `types.py` if needed.

### Adding New Mutations

1. Create input type in `mutations.py`:
```python
@strawberry.input
class CreateMyEntityInput:
    name: str
    description: Optional[str] = None
```

2. Add the mutation method:
```python
@strawberry.mutation
def create_my_entity(self, input: CreateMyEntityInput) -> MyEntity:
    """Create a new my entity."""
    try:
        db = next(get_db())
        entity = MyEntityModel(name=input.name, description=input.description)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        logger.info(f"Created my entity with ID: {entity.id}")
        return MyEntity.from_model(entity)
    except SQLAlchemyError as e:
        logger.error(f"Database error creating my entity: {e}")
        db.rollback()
        raise Exception("Database error occurred")
```

## Testing

### Manual Testing with GraphiQL

1. Start the server: `uvicorn main:app --reload`
2. Navigate to `http://localhost:8000/graphql`
3. Use the GraphiQL interface to test queries and mutations

### Example Test Queries

```graphql
# Test user creation
mutation {
  createUser(input: {username: "testuser"}) {
    id
    username
  }
}

# Test auction creation
mutation {
  createAuction(input: {
    title: "Test Auction"
    description: "Test description"
    startingPrice: 50.00
    startTime: "2024-01-01T10:00:00"
    endTime: "2024-01-07T18:00:00"
    sellerId: 1
    categoryId: 1
  }) {
    id
    title
    status
  }
}
```

## Performance Considerations

1. **Database Queries**: All queries use efficient SQLAlchemy queries with proper indexing
2. **N+1 Problem**: Related data is loaded efficiently using SQLAlchemy relationships
3. **Connection Pooling**: Database connections are managed through SQLAlchemy's connection pool
4. **Error Handling**: Comprehensive error handling prevents resource leaks

## Security

1. **Input Validation**: All inputs are validated before processing
2. **SQL Injection Protection**: Using SQLAlchemy ORM prevents SQL injection
3. **Error Information**: Error messages don't expose sensitive information
4. **Logging**: Comprehensive logging for debugging and monitoring

## Monitoring

The GraphQL API includes comprehensive logging:

- **Info Level**: Successful operations (creates, updates)
- **Warning Level**: Non-critical issues (not found entities)
- **Error Level**: Database errors, validation failures

### Log Format
```
2024-01-01 10:00:00,000 - INFO - Created auction with ID: 1
2024-01-01 10:00:01,000 - ERROR - Database error creating bid: ...
```

## Future Enhancements

1. **Authentication**: Add JWT-based authentication
2. **Authorization**: Implement role-based access control
3. **Subscriptions**: Add real-time updates for auction events
4. **Caching**: Implement Redis-based caching for frequently accessed data
5. **Rate Limiting**: Add rate limiting for mutations
6. **File Uploads**: Support for auction item images
7. **Search**: Add full-text search capabilities
8. **Pagination**: Implement cursor-based pagination for large datasets
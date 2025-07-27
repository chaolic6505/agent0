"""
GraphQL types for the auction system using Strawberry.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Any
from enum import Enum
import strawberry

@strawberry.type
class User:
    id: int
    username: str


@strawberry.type
class StoryNode:
    id: int
    story_id: int
    content: str
    is_ending: bool
    is_root: bool
    is_winning_ending: bool
    options: List[str]


@strawberry.type
class Story:
    id: int
    title: str
    session_id: str = strawberry.field(name="session_id")
    created_at: datetime = strawberry.field(name="created_at")
    updated_at: datetime = strawberry.field(name="updated_at")
    nodes: List[StoryNode]


@strawberry.type
class StoryJob:
    id: int
    job_id: str
    session_id: str
    theme: str
    status: str
    story_id: Optional[int]
    error: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]


@strawberry.enum
class AuctionStatus(Enum):
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    CANCELLED = "cancelled"
    SOLD = "sold"


@strawberry.enum
class BidStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@strawberry.type
class Category:
    id: int
    name: str
    description: Optional[str]
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


@strawberry.type
class Bid:
    id: int
    auction_id: int
    bidder_id: int
    amount: Decimal
    status: BidStatus
    created_at: datetime
    updated_at: datetime


@strawberry.type
class AuctionItem:
    id: int
    auction_id: int
    name: str
    description: str
    condition: Optional[str]
    quantity: int
    created_at: datetime
    updated_at: datetime


@strawberry.type
class Auction:
    id: int
    title: str
    description: str
    starting_price: Decimal
    reserve_price: Optional[Decimal]
    current_price: Decimal
    min_bid_increment: Decimal
    start_time: datetime
    end_time: datetime
    auto_extend_minutes: int
    status: AuctionStatus
    seller_id: int
    category_id: int
    winner_user_id: Optional[int]
    current_highest_bid_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    current_highest_bid: Optional[Bid]
    bids: List[Bid]
    auction_items: List[AuctionItem]
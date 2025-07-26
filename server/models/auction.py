"""
Database models for the auction system.
Defines SQLAlchemy models for auctions, auction items, bids, and related entities.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer,
    String, Text, Numeric, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class AuctionStatus(str, Enum):
    """Auction status enumeration."""
    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    CANCELLED = "cancelled"
    SOLD = "sold"


class BidStatus(str, Enum):
    """Bid status enumeration."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class Auction(Base):
    """Auction model representing an auction event that can contain multiple items."""
    __tablename__ = "auctions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Pricing
    starting_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    reserve_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    current_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    min_bid_increment: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=1.00)

    # Timing
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    auto_extend_minutes: Mapped[int] = mapped_column(Integer, default=5)

    # Status and metadata
    status: Mapped[AuctionStatus] = mapped_column(SQLEnum(AuctionStatus), default=AuctionStatus.DRAFT)
    seller_id: Mapped[int] = mapped_column(Integer, nullable=False)  # Fake user ID
    category_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Winner tracking
    winner_user_id: Mapped[Optional[int]] = mapped_column(Integer)  # Fake user ID
    current_highest_bid_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("bids.id"))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    current_highest_bid: Mapped[Optional["Bid"]] = relationship("Bid", foreign_keys=[current_highest_bid_id])
    bids: Mapped[List["Bid"]] = relationship("Bid", back_populates="auction", cascade="all, delete-orphan")
    auction_items: Mapped[List["AuctionItem"]] = relationship("AuctionItem", back_populates="auction", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("starting_price >= 0", name="check_starting_price_positive"),
        CheckConstraint("current_price >= 0", name="check_current_price_positive"),
        CheckConstraint("min_bid_increment > 0", name="check_min_bid_increment_positive"),
        CheckConstraint("end_time > start_time", name="check_end_time_after_start_time"),
        Index("idx_auction_status_time", "status", "end_time"),
        Index("idx_auction_seller", "seller_id"),
        Index("idx_auction_category", "category_id"),
        Index("idx_auction_winner", "winner_user_id"),
        Index("idx_auction_current_bid", "current_highest_bid_id"),
    )

    def __repr__(self):
        return f"<Auction(id={self.id}, title='{self.title}', status='{self.status}')>"

    @property
    def is_active(self) -> bool:
        """Check if auction is currently active."""
        now = datetime.utcnow()
        return (
            self.status == AuctionStatus.ACTIVE and
            self.start_time <= now <= self.end_time
        )

    @property
    def time_remaining(self) -> Optional[timedelta]:
        """Get time remaining until auction ends."""
        if not self.is_active:
            return None
        return self.end_time - datetime.utcnow()

    def get_minimum_bid(self) -> Decimal:
        """Calculate minimum bid amount."""
        if not self.bids:
            return self.starting_price
        return max(self.current_price + self.min_bid_increment, self.current_price)


class AuctionItem(Base):
    """Auction item model representing individual items within an auction."""
    __tablename__ = "auction_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    auction_id: Mapped[int] = mapped_column(Integer, ForeignKey("auctions.id"), nullable=False)

    # Item details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    condition: Mapped[Optional[str]] = mapped_column(String(100))

    # Item metadata
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    auction: Mapped["Auction"] = relationship("Auction", back_populates="auction_items")

    # Constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_positive"),
        Index("idx_auction_item_auction", "auction_id"),
    )

    def __repr__(self):
        return f"<AuctionItem(id={self.id}, name='{self.name}', auction_id={self.auction_id})>"


class Bid(Base):
    """Bid model representing user bids on auctions."""
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    auction_id: Mapped[int] = mapped_column(Integer, ForeignKey("auctions.id"), nullable=False)
    bidder_id: Mapped[int] = mapped_column(Integer, nullable=False)  # Fake user ID
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[BidStatus] = mapped_column(SQLEnum(BidStatus), default=BidStatus.PENDING)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    auction: Mapped["Auction"] = relationship("Auction", back_populates="bids")

    # Constraints
    __table_args__ = (
        CheckConstraint("amount > 0", name="check_bid_amount_positive"),
        Index("idx_bid_auction_time", "auction_id", "created_at"),
        Index("idx_bid_bidder", "bidder_id"),
        Index("idx_bid_status", "status"),
        Index("idx_bid_amount", "auction_id", "amount"),
    )

    def __repr__(self):
        return f"<Bid(id={self.id}, auction_id={self.auction_id}, bidder_id={self.bidder_id}, amount={self.amount})>"


class Category(Base):
    """Category model for organizing auctions."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"
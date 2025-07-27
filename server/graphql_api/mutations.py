"""
GraphQL mutations for the auction system.
"""

from typing import Optional, List, Any
import strawberry
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db.database import get_db
from models.user import User as UserModel
from models.story import Story as StoryModel, StoryNode as StoryNodeModel
from models.job import StoryJob as StoryJobModel
from models.auction import Auction as AuctionModel, Bid as BidModel, Category as CategoryModel, AuctionItem as AuctionItemModel, AuctionStatus, BidStatus
from .types import User, Story, StoryNode, StoryJob, Auction, Bid, Category, AuctionItem
import logging
from datetime import datetime
from decimal import Decimal

# Set up logging
logger = logging.getLogger(__name__)


@strawberry.input
class CreateUserInput:
    username: str


@strawberry.input
class CreateStoryInput:
    title: str
    session_id: str


@strawberry.input
class CreateStoryNodeInput:
    story_id: int
    content: str
    is_ending: bool = False
    is_root: bool = False
    is_winning_ending: bool = False
    options: List[str] = strawberry.field(default_factory=list)


@strawberry.input
class CreateStoryJobInput:
    job_id: str
    session_id: str
    theme: str
    status: str = "pending"


@strawberry.input
class CreateCategoryInput:
    name: str
    description: Optional[str] = None
    slug: str
    is_active: bool = True


@strawberry.input
class CreateAuctionInput:
    title: str
    description: str
    starting_price: float
    reserve_price: Optional[float] = None
    min_bid_increment: float = 1.0
    start_time: str  # ISO datetime string
    end_time: str  # ISO datetime string
    auto_extend_minutes: int = 5
    seller_id: int
    category_id: int


@strawberry.input
class CreateAuctionItemInput:
    auction_id: int
    name: str
    description: str
    condition: Optional[str] = None
    quantity: int = 1


@strawberry.input
class CreateBidInput:
    auction_id: int
    bidder_id: int
    amount: float


@strawberry.input
class UpdateStoryJobInput:
    id: int
    status: Optional[str] = None
    story_id: Optional[int] = None
    error: Optional[str] = None
    completed_at: Optional[str] = None  # ISO datetime string


@strawberry.input
class UpdateAuctionInput:
    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    current_price: Optional[float] = None
    status: Optional[str] = None
    winner_user_id: Optional[int] = None
    current_highest_bid_id: Optional[int] = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, input: CreateUserInput) -> User:
        """Create a new user."""
        try:
            db = next(get_db())
            user = UserModel(username=input.username)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created user with ID: {user.id}")
            return User(id=user.id, username=user.username)
        except IntegrityError as e:
            logger.error(f"Integrity error creating user: {e}")
            db.rollback()
            raise Exception("Username already exists")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating user: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error creating user: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")

    @strawberry.mutation
    def create_story(self, input: CreateStoryInput) -> Story:
        """Create a new story."""
        try:
            db = next(get_db())
            story = StoryModel(title=input.title, session_id=input.session_id)
            db.add(story)
            db.commit()
            db.refresh(story)
            logger.info(f"Created story with ID: {story.id}")
            return Story(
                id=story.id,
                title=story.title,
                session_id=story.session_id,
                created_at=story.created_at,
                updated_at=story.updated_at,
                nodes=[]
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error creating story: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error creating story: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")

    @strawberry.mutation
    def create_story_node(self, input: CreateStoryNodeInput) -> StoryNode:
        """Create a new story node."""
        try:
            db = next(get_db())
            node = StoryNodeModel(
                story_id=input.story_id,
                content=input.content,
                is_ending=input.is_ending,
                is_root=input.is_root,
                is_winning_ending=input.is_winning_ending,
                options=input.options
            )
            db.add(node)
            db.commit()
            db.refresh(node)
            logger.info(f"Created story node with ID: {node.id}")
            return StoryNode(
                id=node.id,
                story_id=node.story_id,
                content=node.content,
                is_ending=node.is_ending,
                is_root=node.is_root,
                is_winning_ending=node.is_winning_ending,
                options=node.options
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error creating story node: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error creating story node: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")

    @strawberry.mutation
    def create_story_job(self, input: CreateStoryJobInput) -> StoryJob:
        """Create a new story job."""
        try:
            db = next(get_db())
            job = StoryJobModel(
                job_id=input.job_id,
                session_id=input.session_id,
                theme=input.theme,
                status=input.status
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            logger.info(f"Created story job with ID: {job.id}")
            return StoryJob(
                id=job.id,
                job_id=job.job_id,
                session_id=job.session_id,
                theme=job.theme,
                status=job.status,
                story_id=job.story_id,
                error=job.error,
                created_at=job.created_at,
                completed_at=job.completed_at
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error creating story job: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error creating story job: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")

    @strawberry.mutation
    def update_story_job(self, input: UpdateStoryJobInput) -> Optional[StoryJob]:
        """Update a story job."""
        try:
            db = next(get_db())
            job = db.query(StoryJobModel).filter(StoryJobModel.id == input.id).first()
            if not job:
                logger.warning(f"Story job with ID {input.id} not found")
                return None

            if input.status is not None:
                job.status = input.status
            if input.story_id is not None:
                job.story_id = input.story_id
            if input.error is not None:
                job.error = input.error
            if input.completed_at is not None:
                job.completed_at = datetime.fromisoformat(input.completed_at)

            db.commit()
            db.refresh(job)
            logger.info(f"Updated story job with ID: {job.id}")
            return StoryJob(
                id=job.id,
                job_id=job.job_id,
                session_id=job.session_id,
                theme=job.theme,
                status=job.status,
                story_id=job.story_id,
                error=job.error,
                created_at=job.created_at,
                completed_at=job.completed_at
            )
        except SQLAlchemyError as e:
            logger.error(f"Database error updating story job: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error updating story job: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")

    @strawberry.mutation
    def create_category(self, input: CreateCategoryInput) -> Category:
        """Create a new category."""
        try:
            db = next(get_db())
            category = CategoryModel(
                name=input.name,
                description=input.description,
                slug=input.slug,
                is_active=input.is_active
            )
            db.add(category)
            db.commit()
            db.refresh(category)
            logger.info(f"Created category with ID: {category.id}")
            return Category(
                id=category.id,
                name=category.name,
                description=category.description,
                slug=category.slug,
                is_active=category.is_active,
                created_at=category.created_at,
                updated_at=category.updated_at
            )
        except IntegrityError as e:
            logger.error(f"Integrity error creating category: {e}")
            db.rollback()
            raise Exception("Category name or slug already exists")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating category: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error creating category: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")

    @strawberry.mutation
    def create_auction(self, input: CreateAuctionInput) -> Auction:
        """Create a new auction."""
        try:
            db = next(get_db())

            # Validate input
            if input.starting_price < 0:
                raise Exception("Starting price must be non-negative")
            if input.min_bid_increment <= 0:
                raise Exception("Minimum bid increment must be positive")

            start_time = datetime.fromisoformat(input.start_time)
            end_time = datetime.fromisoformat(input.end_time)

            if end_time <= start_time:
                raise Exception("End time must be after start time")

            auction = AuctionModel(
                title=input.title,
                description=input.description,
                starting_price=Decimal(str(input.starting_price)),
                reserve_price=Decimal(str(input.reserve_price)) if input.reserve_price else None,
                current_price=Decimal(str(input.starting_price)),
                min_bid_increment=Decimal(str(input.min_bid_increment)),
                start_time=start_time,
                end_time=end_time,
                auto_extend_minutes=input.auto_extend_minutes,
                status=AuctionStatus.DRAFT,
                seller_id=input.seller_id,
                category_id=input.category_id
            )
            db.add(auction)
            db.commit()
            db.refresh(auction)
            logger.info(f"Created auction with ID: {auction.id}")
            return Auction(
                id=auction.id,
                title=auction.title,
                description=auction.description,
                starting_price=auction.starting_price,
                reserve_price=auction.reserve_price,
                current_price=auction.current_price,
                min_bid_increment=auction.min_bid_increment,
                start_time=auction.start_time,
                end_time=auction.end_time,
                auto_extend_minutes=auction.auto_extend_minutes,
                status=auction.status,
                seller_id=auction.seller_id,
                category_id=auction.category_id,
                winner_user_id=auction.winner_user_id,
                current_highest_bid_id=auction.current_highest_bid_id,
                created_at=auction.created_at,
                updated_at=auction.updated_at,
                current_highest_bid=None,
                bids=[],
                auction_items=[]
            )
        except ValueError as e:
            logger.error(f"Validation error creating auction: {e}")
            raise Exception(f"Invalid input: {str(e)}")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating auction: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error creating auction: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")

    @strawberry.mutation
    def update_auction(self, input: UpdateAuctionInput) -> Optional[Auction]:
        """Update an auction."""
        try:
            db = next(get_db())
            auction = db.query(AuctionModel).filter(AuctionModel.id == input.id).first()
            if not auction:
                logger.warning(f"Auction with ID {input.id} not found")
                return None

            if input.title is not None:
                auction.title = input.title
            if input.description is not None:
                auction.description = input.description
            if input.current_price is not None:
                if input.current_price < 0:
                    raise Exception("Current price must be non-negative")
                auction.current_price = Decimal(str(input.current_price))
            if input.status is not None:
                auction.status = AuctionStatus(input.status)
            if input.winner_user_id is not None:
                auction.winner_user_id = input.winner_user_id
            if input.current_highest_bid_id is not None:
                auction.current_highest_bid_id = input.current_highest_bid_id

            db.commit()
            db.refresh(auction)

            # Get related data
            bids = db.query(BidModel).filter(BidModel.auction_id == auction.id).all()
            auction_items = db.query(AuctionItemModel).filter(AuctionItemModel.auction_id == auction.id).all()

            bid_list = [
                Bid(
                    id=bid.id,
                    auction_id=bid.auction_id,
                    bidder_id=bid.bidder_id,
                    amount=bid.amount,
                    status=bid.status,
                    created_at=bid.created_at,
                    updated_at=bid.updated_at
                ) for bid in bids
            ]

            item_list = [
                AuctionItem(
                    id=item.id,
                    auction_id=item.auction_id,
                    name=item.name,
                    description=item.description,
                    condition=item.condition,
                    quantity=item.quantity,
                    created_at=item.created_at,
                    updated_at=item.updated_at
                ) for item in auction_items
            ]

            current_highest_bid = None
            if auction.current_highest_bid:
                current_highest_bid = Bid(
                    id=auction.current_highest_bid.id,
                    auction_id=auction.current_highest_bid.auction_id,
                    bidder_id=auction.current_highest_bid.bidder_id,
                    amount=auction.current_highest_bid.amount,
                    status=auction.current_highest_bid.status,
                    created_at=auction.current_highest_bid.created_at,
                    updated_at=auction.current_highest_bid.updated_at
                )

            logger.info(f"Updated auction with ID: {auction.id}")
            return Auction(
                id=auction.id,
                title=auction.title,
                description=auction.description,
                starting_price=auction.starting_price,
                reserve_price=auction.reserve_price,
                current_price=auction.current_price,
                min_bid_increment=auction.min_bid_increment,
                start_time=auction.start_time,
                end_time=auction.end_time,
                auto_extend_minutes=auction.auto_extend_minutes,
                status=auction.status,
                seller_id=auction.seller_id,
                category_id=auction.category_id,
                winner_user_id=auction.winner_user_id,
                current_highest_bid_id=auction.current_highest_bid_id,
                created_at=auction.created_at,
                updated_at=auction.updated_at,
                current_highest_bid=current_highest_bid,
                bids=bid_list,
                auction_items=item_list
            )
        except ValueError as e:
            logger.error(f"Validation error updating auction: {e}")
            raise Exception(f"Invalid input: {str(e)}")
        except SQLAlchemyError as e:
            logger.error(f"Database error updating auction: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error updating auction: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")

    @strawberry.mutation
    def create_auction_item(self, input: CreateAuctionItemInput) -> AuctionItem:
        """Create a new auction item."""
        try:
            db = next(get_db())

            # Validate input
            if input.quantity <= 0:
                raise Exception("Quantity must be positive")

            item = AuctionItemModel(
                auction_id=input.auction_id,
                name=input.name,
                description=input.description,
                condition=input.condition,
                quantity=input.quantity
            )
            db.add(item)
            db.commit()
            db.refresh(item)
            logger.info(f"Created auction item with ID: {item.id}")
            return AuctionItem(
                id=item.id,
                auction_id=item.auction_id,
                name=item.name,
                description=item.description,
                condition=item.condition,
                quantity=item.quantity,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
        except ValueError as e:
            logger.error(f"Validation error creating auction item: {e}")
            raise Exception(f"Invalid input: {str(e)}")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating auction item: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error creating auction item: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")

    @strawberry.mutation
    def create_bid(self, input: CreateBidInput) -> Bid:
        """Create a new bid."""
        try:
            db = next(get_db())

            # Validate input
            if input.amount <= 0:
                raise Exception("Bid amount must be positive")

            # Check if auction exists and is active
            auction = db.query(AuctionModel).filter(AuctionModel.id == input.auction_id).first()
            if not auction:
                raise Exception("Auction not found")

            if auction.status != AuctionStatus.ACTIVE:
                raise Exception("Auction is not active")

            # Check if bid meets minimum requirements
            min_bid = auction.get_minimum_bid()
            if input.amount < min_bid:
                raise Exception(f"Bid must be at least {min_bid}")

            bid = BidModel(
                auction_id=input.auction_id,
                bidder_id=input.bidder_id,
                amount=Decimal(str(input.amount)),
                status=BidStatus.PENDING
            )
            db.add(bid)
            db.commit()
            db.refresh(bid)
            logger.info(f"Created bid with ID: {bid.id}")
            return Bid(
                id=bid.id,
                auction_id=bid.auction_id,
                bidder_id=bid.bidder_id,
                amount=bid.amount,
                status=bid.status,
                created_at=bid.created_at,
                updated_at=bid.updated_at
            )
        except ValueError as e:
            logger.error(f"Validation error creating bid: {e}")
            raise Exception(f"Invalid input: {str(e)}")
        except SQLAlchemyError as e:
            logger.error(f"Database error creating bid: {e}")
            db.rollback()
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error creating bid: {e}")
            db.rollback()
            raise Exception("An unexpected error occurred")
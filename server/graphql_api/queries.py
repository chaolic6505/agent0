"""
GraphQL queries for the auction system.
"""

from typing import List, Optional
import strawberry
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import get_db
from models.user import User as UserModel
from models.story import Story as StoryModel, StoryNode as StoryNodeModel
from models.job import StoryJob as StoryJobModel
from models.auction import Auction as AuctionModel, Bid as BidModel, Category as CategoryModel, AuctionItem as AuctionItemModel
from .types import User, Story, StoryNode, StoryJob, Auction, Bid, Category, AuctionItem
import logging

# Set up logging
logger = logging.getLogger(__name__)


@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        """Get a user by ID."""
        try:
            db = next(get_db())
            user = db.query(UserModel).filter(UserModel.id == id).first()
            if user:
                return User(id=user.id, username=user.username)
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error in user query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in user query: {e}")
            raise Exception("An unexpected error occurred")

    @strawberry.field
    def users(self) -> List[User]:
        """Get all users."""
        try:
            db = next(get_db())
            users = db.query(UserModel).all()
            return [User(id=user.id, username=user.username) for user in users]
        except SQLAlchemyError as e:
            logger.error(f"Database error in users query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in users query: {e}")
            raise Exception("An unexpected error occurred")

    @strawberry.field
    def story(self, id: int) -> Optional[Story]:
        """Get a story by ID."""
        try:
            db = next(get_db())
            story = db.query(StoryModel).filter(StoryModel.id == id).first()
            if story:
                nodes = db.query(StoryNodeModel).filter(StoryNodeModel.story_id == story.id).all()
                story_nodes = [
                    StoryNode(
                        id=node.id,
                        story_id=node.story_id,
                        content=node.content,
                        is_ending=node.is_ending,
                        is_root=node.is_root,
                        is_winning_ending=node.is_winning_ending,
                        options=node.options
                    ) for node in nodes
                ]
                return Story(
                    id=story.id,
                    title=story.title,
                    session_id=story.session_id,
                    created_at=story.created_at,
                    updated_at=story.updated_at,
                    nodes=story_nodes
                )
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error in story query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in story query: {e}")
            raise Exception("An unexpected error occurred")

    @strawberry.field
    def stories(self) -> List[Story]:
        """Get all stories."""
        try:
            db = next(get_db())
            stories = db.query(StoryModel).all()
            result = []
            for story in stories:
                nodes = db.query(StoryNodeModel).filter(StoryNodeModel.story_id == story.id).all()
                story_nodes = [
                    StoryNode(
                        id=node.id,
                        story_id=node.story_id,
                        content=node.content,
                        is_ending=node.is_ending,
                        is_root=node.is_root,
                        is_winning_ending=node.is_winning_ending,
                        options=node.options
                    ) for node in nodes
                ]
                result.append(Story(
                    id=story.id,
                    title=story.title,
                    session_id=story.session_id,
                    created_at=story.created_at,
                    updated_at=story.updated_at,
                    nodes=story_nodes
                ))
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error in stories query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in stories query: {e}")
            raise Exception("An unexpected error occurred")

    @strawberry.field
    def story_job(self, id: int) -> Optional[StoryJob]:
        """Get a story job by ID."""
        try:
            db = next(get_db())
            job = db.query(StoryJobModel).filter(StoryJobModel.id == id).first()
            if job:
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
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error in story_job query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in story_job query: {e}")
            raise Exception("An unexpected error occurred")

    @strawberry.field
    def story_jobs(self) -> List[StoryJob]:
        """Get all story jobs."""
        try:
            db = next(get_db())
            jobs = db.query(StoryJobModel).all()
            return [
                StoryJob(
                    id=job.id,
                    job_id=job.job_id,
                    session_id=job.session_id,
                    theme=job.theme,
                    status=job.status,
                    story_id=job.story_id,
                    error=job.error,
                    created_at=job.created_at,
                    completed_at=job.completed_at
                ) for job in jobs
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error in story_jobs query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in story_jobs query: {e}")
            raise Exception("An unexpected error occurred")

    @strawberry.field
    def auction(self, id: int) -> Optional[Auction]:
        """Get an auction by ID."""
        try:
            db = next(get_db())
            auction = db.query(AuctionModel).filter(AuctionModel.id == id).first()
            if auction:
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
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error in auction query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in auction query: {e}")
            raise Exception("An unexpected error occurred")

    @strawberry.field
    def auctions(self) -> List[Auction]:
        """Get all auctions."""
        try:
            db = next(get_db())
            auctions = db.query(AuctionModel).all()
            result = []
            for auction in auctions:
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

                result.append(Auction(
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
                ))
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error in auctions query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in auctions query: {e}")
            raise Exception("An unexpected error occurred")

    @strawberry.field
    def category(self, id: int) -> Optional[Category]:
        """Get a category by ID."""
        try:
            db = next(get_db())
            category = db.query(CategoryModel).filter(CategoryModel.id == id).first()
            if category:
                return Category(
                    id=category.id,
                    name=category.name,
                    description=category.description,
                    slug=category.slug,
                    is_active=category.is_active,
                    created_at=category.created_at,
                    updated_at=category.updated_at
                )
            return None
        except SQLAlchemyError as e:
            logger.error(f"Database error in category query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in category query: {e}")
            raise Exception("An unexpected error occurred")

    @strawberry.field
    def categories(self) -> List[Category]:
        """Get all categories."""
        try:
            db = next(get_db())
            categories = db.query(CategoryModel).all()
            return [
                Category(
                    id=category.id,
                    name=category.name,
                    description=category.description,
                    slug=category.slug,
                    is_active=category.is_active,
                    created_at=category.created_at,
                    updated_at=category.updated_at
                ) for category in categories
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error in categories query: {e}")
            raise Exception("Database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error in categories query: {e}")
            raise Exception("An unexpected error occurred")
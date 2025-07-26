# Auction System

A simple auction system with PostgreSQL and Redis.

## Quick Start with Docker

1. **Clone and navigate to the server directory:**
   ```bash
   cd server
   ```

2. **Create a .env file:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Health Check: http://localhost:8000/health
   - API Docs: http://localhost:8000/docs

## Local Development

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Set up environment variables:**
   ```bash
   # Create .env file with:
   DATABASE_URL=postgresql://auction_user:auction_pass@localhost:5432/auction_db
   REDIS_URL=redis://localhost:6379/0
   DEBUG=true
   ```

3. **Start PostgreSQL and Redis:**
   ```bash
   docker-compose up postgres redis -d
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

## Database Models

- **Auction**: Main auction entity with pricing and timing
- **AuctionItem**: Items within an auction (supports multiple items per auction)
- **Bid**: User bids on auctions
- **Category**: Auction categories

## Features

- ✅ Multiple auction items per auction
- ✅ Winner tracking
- ✅ Current highest bid tracking
- ✅ Race condition prevention (via database constraints)
- ✅ Docker setup with PostgreSQL and Redis
- ✅ Simple FastAPI endpoints

## Next Steps

- Add bidding endpoints
- Implement Redis caching
- Add WebSocket support for real-time updates
- Add authentication system

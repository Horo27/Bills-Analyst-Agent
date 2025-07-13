# Smart Home Expense & Maintenance Analyst Agent

An intelligent backend system for managing household expenses and maintenance tasks using LangGraph, PostgreSQL, and FastAPI.

## Features

### 🤖 Intelligent Agent
- **Natural Language Processing**: Chat with the agent using natural language
- **Intent Recognition**: Automatically understands user intentions (add bills, query expenses, get summaries)
- **Stateful Conversations**: Maintains context across conversation turns
- **Multi-turn Interactions**: Handles complex queries requiring clarification

### 💰 Expense Management
- **Bill Tracking**: Add, update, and manage household bills
- **Categorization**: Organize expenses by categories (utilities, subscriptions, maintenance, etc.)
- **Due Date Management**: Track upcoming and overdue bills
- **Recurring Bills**: Support for recurring expenses with different frequencies

### 📊 Analytics & Insights
- **Monthly Summaries**: Get comprehensive monthly expense reports
- **Trend Analysis**: Track spending patterns over time
- **Category Breakdown**: Analyze spending by category
- **Statistics**: Get detailed financial statistics and insights

### 🔧 Maintenance Tracking
- **Task Management**: Schedule and track home maintenance tasks
- **Cost Tracking**: Monitor estimated vs actual maintenance costs
- **Contractor Information**: Store contractor details and contact information
- **Recurring Maintenance**: Set up recurring maintenance schedules

## Technology Stack

- **Agent Framework**: LangGraph for workflow orchestration
- **Backend**: FastAPI for REST API
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: OpenAI GPT for natural language understanding
- **Validation**: Pydantic for data validation
- **Logging**: Structured logging with Python logging

## Project Structure

```
smart_home_agent/
├── core/                   # Core application configuration
│   ├── config.py          # Settings and configuration
│   └── database.py        # Database setup and session management
├── models/                 # SQLAlchemy database models
│   ├── base.py            # Base model with common fields
│   ├── bills.py           # Bill and expense models
│   ├── categories.py      # Category model
│   └── maintenance.py     # Maintenance task model
├── agent/                  # LangGraph agent implementation
│   ├── state.py           # Agent state management
│   ├── nodes.py           # Graph nodes for different operations
│   ├── graph.py           # Main graph orchestration
│   └── intent_parser.py   # Natural language intent parsing
├── services/               # Business logic services
│   ├── expense_service.py # Expense management service
│   └── analytics_service.py # Analytics and reporting service
├── api/                    # FastAPI REST API
│   ├── routes.py          # API endpoints
│   ├── middleware.py      # Custom middleware
│   └── schemas.py         # Pydantic schemas
└── utils/                  # Utility functions
    ├── logger.py          # Logging configuration
    └── helpers.py         # Helper functions
```

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-home-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup PostgreSQL database**
   ```bash
   # Create database
   createdb smart_home_agent

   # Or using psql
   psql -U postgres
   CREATE DATABASE smart_home_agent;
   ```

5. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and OpenAI API key
   ```

6. **Initialize database & start the backend**
   ```bash
   uvicorn main:app --reload
   ```
   
6. **Install Front-end Dependencies and Run**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Usage

### API Documentation

The Frontend API will be available at `http://localhost:3000`
The Backend API will be available at `http://localhost:8000`

Once the server is running, you can access:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Agent Chat API

```bash
# Chat with the agent
curl -X POST "http://localhost:8000/api/v1/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a new bill: Electric bill for $120 due July 15th",
    "session_id": "user123"
  }'
```

### Bill Management API

```bash
# Create a new bill
curl -X POST "http://localhost:8000/api/v1/bills/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electric Bill",
    "amount": 120.50,
    "due_date": "2025-07-15",
    "category_name": "Utilities",
    "description": "Monthly electricity bill"
  }'

# Get all bills
curl "http://localhost:8000/api/v1/bills/"

# Get upcoming bills
curl "http://localhost:8000/api/v1/bills/upcoming/list?days=30"
```

### Analytics API

```bash
# Get monthly summary
curl "http://localhost:8000/api/v1/analytics/summary"

# Get comprehensive statistics
curl "http://localhost:8000/api/v1/analytics/stats"

# Get category analysis
curl "http://localhost:8000/api/v1/analytics/categories/analysis"
```

## Agent Capabilities

The agent can understand and respond to various types of queries:

### Adding Bills
- "Add a bill: Internet $89.99 due July 10th"
- "Create a new expense for Netflix subscription $15.99"
- "I need to add my electric bill of $120 due on the 15th"

### Querying Expenses
- "What are my bills this month?"
- "Show me all utilities expenses"
- "How much did I spend on subscriptions?"

### Getting Summaries
- "Give me a summary of my expenses"
- "What's my total spending this month?"
- "Show me my expense statistics"

### Upcoming Bills
- "What bills are due soon?"
- "List my upcoming payments"
- "Do I have any bills due next week?"

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/smart_home_agent
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_home_agent
DB_USER=postgres
DB_PASSWORD=password

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Application
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_here

# API
API_PREFIX=/api/v1
CORS_ORIGINS=["http://localhost:3000"]

# Agent
AGENT_MODEL=deepseek/deepseek-r1:free
AGENT_TEMPERATURE=0.1
MAX_CONVERSATION_HISTORY=50
```

### Database Schema

The application uses the following main tables:
- `categories`: Expense categories
- `bills`: Bills and expenses
- `maintenance_tasks`: Maintenance tasks


## API Reference

### Agent Endpoints

- `POST /api/v1/agent/chat` - Chat with the agent
- `GET /api/v1/agent/history/{session_id}` - Get conversation history
- `DELETE /api/v1/agent/session/{session_id}` - Clear session

### Bill Endpoints

- `POST /api/v1/bills/` - Create a new bill
- `GET /api/v1/bills/` - Get bills with filtering
- `GET /api/v1/bills/{bill_id}` - Get specific bill
- `PUT /api/v1/bills/{bill_id}` - Update bill
- `DELETE /api/v1/bills/{bill_id}` - Delete bill
- `GET /api/v1/bills/upcoming/list` - Get upcoming bills
- `GET /api/v1/bills/overdue/list` - Get overdue bills

### Analytics Endpoints

- `GET /api/v1/analytics/summary` - Monthly summary
- `GET /api/v1/analytics/stats` - Comprehensive statistics
- `GET /api/v1/analytics/categories/analysis` - Category analysis
- `GET /api/v1/analytics/trends` - Trend analysis

### Category Endpoints

- `GET /api/v1/categories/` - Get all categories

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

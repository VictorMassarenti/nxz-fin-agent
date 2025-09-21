# NXZ-FIN-AGENT Project Context

## Project Overview
This is a financial assistant agent for NEXUZ, a company that serves the Food Service sector. The agent is built using LangGraph and LangChain to help customers with financial operations such as:
- Checking debts/invoices
- Generating second copies of invoices
- Processing payments
- Handling payment receipts

The agent is designed to be a virtual financial assistant that follows specific guidelines for professional and clear communication with customers.

## Project Structure
```
nxz-fin-agent/
├── agent/
│   ├── graph.py      # Main agent logic and configuration
│   └── tools.py      # Custom tools for the agent
├── .env              # Environment configuration
├── .gitignore
├── langgraph.json    # LangGraph configuration
├── mock-data.json    # Mock data for testing
├── requirements.txt  # Python dependencies
└── QWEN.md           # This file
```

## Technologies Used
- **LangGraph/LangChain**: Core framework for building the agent
- **OpenAI GPT**: Language model (gpt-4o-mini)
- **PostgreSQL**: Database for client information
- **Python**: Primary programming language

## Key Components

### Agent (agent/graph.py)
The main agent implementation that:
- Uses OpenAI's GPT-4o-mini model
- Implements a ReAct agent pattern
- Follows specific system guidelines for customer interaction
- Integrates custom tools for client management

### Tools (agent/tools.py)
Custom tools available to the agent:
- `add_client`: Adds a new client to the database
- `find_client`: Searches for clients by name or company

### Configuration Files
- `langgraph.json`: Defines the agent graph and dependencies
- `.env`: Environment variables for API keys, database connection, etc.
- `requirements.txt`: Python package dependencies

### Data
- `mock-data.json`: Contains sample client data, test messages, standard responses, and system configurations

## Development Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database
- OpenAI API key

### Installation
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env` file

### Running the Agent
The agent is configured to run with LangGraph. Use the LangGraph CLI or deployment tools to start the agent.

### Key Environment Variables
- `OPENAI_API_KEY`: OpenAI API key for GPT model access
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`: PostgreSQL database connection details
- `LANGSMITH_API_KEY`: LangSmith tracing key for monitoring

## Development Conventions

### Code Style
- Python code follows standard Python conventions
- Clear function and variable naming
- Docstrings for all functions and modules

### Agent Behavior Guidelines
The agent follows specific guidelines:
- Always be courteous and professional
- Use clear, objective language
- Format monetary values as R$ X.XXX,XX
- Format dates as DD/MM/AAAA
- Confirm important actions before executing
- Offer options to clients when in doubt
- Preserve conversation context

### What the Agent Should NOT Do
- Provide information about other clients
- Change values or due dates without authorization
- Promise something it cannot fulfill
- Use unnecessary technical jargon

## Testing
The project includes mock data for testing various scenarios:
- Client authentication (valid/invalid CNPJs)
- Debt consultation with/without pending debts
- Second invoice generation with/without discounts
- Payment receipt handling
- Human agent handoff
- Blocked client handling

## Deployment
The project is configured for cloud deployment with:
- `DEPLOY_TARGET=cloud` in the .env file
- PostgreSQL database connection
- OpenAI API integration

## Dependencies
Key dependencies include:
- langchain & langchain-core: Core framework
- langgraph: Agent workflow management
- openai: OpenAI API integration
- psycopg: PostgreSQL database adapter
- python-dotenv: Environment variable management
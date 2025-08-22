# Payroll Agent System

A multi-agent system for automated timesheet processing and anomaly detection using the OpenAI Agents SDK.

## 🚀 Features

- **Multi-Agent Architecture**: Orchestrated agents for different responsibilities
- **Anomaly Detection**: Automatically identifies missing hours and timesheet irregularities
- **Email Notifications**: Sends automated emails to employees about timesheet issues
- **Flexible Data Source**: Currently uses CSV, easily extendable to databases
- **SOLID Principles**: Clean architecture with dependency injection and abstraction

## 📋 System Architecture

### Agents

1. **Orchestrator Agent**: Main entry point that understands user requests and delegates to specialized agents
2. **Timesheet Analyzer Agent**: Analyzes timesheets, detects anomalies, and sends notifications
3. **Employee Engagement Agent** (Future): Monitors email responses and follows up
4. **Compliance Agent** (Future): Validates against policies and approves/rejects timesheets

### Key Components

- **Repository Pattern**: Abstract data access layer (easily swap CSV for database)
- **Email Service**: Handles all email communications
- **Configuration Management**: Centralized settings management
- **Models**: Pydantic models for data validation

## 🛠️ Setup

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
cd payroll-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration (Gmail)
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

4. Generate sample data:
```bash
python data/generate_sample_data.py
```

## 🎮 Usage

### Interactive Mode

Run the system in interactive mode:
```bash
python run.py
```

Then interact with the system using natural language:
```
> Find anomalies in the timesheets and notify employees
> List all pending timesheets
> Analyze timesheets from last week
```

### Batch Mode

Execute a single command:
```bash
python run.py "analyze timesheets and send notifications"
```

### Available Commands

- **Analyze timesheets**: `"Find anomalies in timesheets"`
- **Send notifications**: `"Send emails to employees with missing hours"`
- **List pending**: `"Show all pending timesheets"`
- **Get summary**: `"Get timesheet summary for employee EMP001"`

## 📁 Project Structure

```
payroll-agent/
├── src/
│   ├── agents/          # Agent definitions and tools
│   ├── config/          # Configuration management
│   ├── models/          # Data models (Pydantic)
│   ├── repositories/    # Data access layer
│   └── services/        # Business services (email, etc.)
├── data/                # CSV data storage
├── main.py              # Main application
├── run.py               # Runner script
└── requirements.txt     # Dependencies
```

## 🔄 Extending the System

### Adding a New Data Source

1. Create a new repository implementation:
```python
# src/repositories/database_repository.py
class DatabaseTimesheetRepository(TimesheetRepository):
    async def get_timesheets_by_date_range(...):
        # Database implementation
        pass
```

2. Update the dependency injection:
```python
# src/agents/tools.py
repository = DatabaseTimesheetRepository()  # Instead of CSVTimesheetRepository
```

### Adding New Agents

1. Define the agent in `src/agents/`:
```python
def create_new_agent() -> Agent:
    return Agent(
        name="New Agent",
        instructions="...",
        tools=[...],
        handoffs=[...]
    )
```

2. Add handoffs in the orchestrator:
```python
handoffs = [
    Handoff(target=new_agent, name="...", description="...")
]
```

## 🧪 Testing

Generate sample data with anomalies:
```bash
python data/generate_sample_data.py
```

This creates test data with:
- Missing hours entries
- Excessive hours
- Missing timesheet days
- Incomplete submissions

## 📧 Email Configuration

### Gmail Setup

1. Enable 2-factor authentication
2. Generate an app-specific password
3. Use the app password in your `.env` file

### Other Email Providers

Update the SMTP settings in `.env`:
```env
SMTP_SERVER=your.smtp.server
SMTP_PORT=your_port
```

## 🚧 Future Enhancements

- [ ] Email reply monitoring
- [ ] Policy compliance checking
- [ ] Leave balance integration
- [ ] Database support (PostgreSQL/MySQL)
- [ ] Web interface
- [ ] Slack/Teams integration
- [ ] Advanced anomaly detection with ML
- [ ] Automatic timesheet approval workflow

## 📝 License

This project is proprietary.

## 🤝 Contributing

Please follow the SOLID principles and maintain the clean architecture when contributing.

## 📞 Support

For issues or questions, please contact the development team.

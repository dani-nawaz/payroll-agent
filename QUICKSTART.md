# Quick Start Guide - Payroll Agent System

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with your credentials:
```env
OPENAI_API_KEY=sk-your-api-key-here
EMAIL_USERNAME=abdulrehman@clickchain.com
EMAIL_PASSWORD=jayx tamp jmcj yrnf
```

### 3. Generate Test Data
```bash
python data/generate_sample_data.py
```

### 4. Run the System

#### Option A: Interactive Mode
```bash
python run.py
```

Then type commands like:
- `analyze timesheets`
- `find anomalies and send emails`
- `list pending timesheets`

#### Option B: Command Mode
```bash
python run.py "analyze timesheets and notify employees"
```

### 5. Test the System
Run the test suite to verify everything works:
```bash
python test_system.py
```

## 📊 Sample Scenarios

### Scenario 1: Find and Report Anomalies
```
> find anomalies in timesheets from last week
```
The system will:
1. Analyze all timesheets
2. Identify missing hours (<8 hours/day)
3. Find excessive hours (>12 hours/day)
4. Report findings

### Scenario 2: Send Notifications
```
> analyze timesheets and send email notifications
```
The system will:
1. Find all anomalies
2. Group by employee
3. Send personalized emails
4. Report send status

### Scenario 3: Get Employee Summary
```
> get timesheet summary for employee EMP001
```
The system will:
1. Retrieve employee timesheets
2. Calculate total hours
3. List anomalies
4. Show summary statistics

## 🔧 Troubleshooting

### OpenAI API Key Not Working
- Ensure your API key starts with `sk-`
- Check you have credits/valid subscription
- Verify the key in your `.env` file

### Email Not Sending
- For Gmail: Use an [App Password](https://support.google.com/accounts/answer/185833)
- Check firewall/antivirus settings
- Verify SMTP settings in `.env`

### No Data Found
- Run `python data/generate_sample_data.py`
- Check `data/timesheets.csv` exists
- Verify CSV_DATA_PATH in settings

## 📝 Next Steps

1. **Customize Anomaly Rules**: Edit `src/config/settings.py` to change thresholds
2. **Add Real Data**: Replace CSV with your actual data source
3. **Extend Agents**: Add new agents for additional workflows
4. **Integrate Systems**: Connect to your HR/Payroll systems

## 💡 Tips

- Start with test data to understand the system
- Use interactive mode for exploration
- Check logs for detailed execution info
- Email notifications work with real SMTP credentials

## 🆘 Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review test output from `test_system.py`
- Examine sample data in `data/timesheets.csv`

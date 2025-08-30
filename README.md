# CronJob Multi-Module Data Scraper

A modular data scraping project that supports automated monitoring and scraping of multiple data sources.

## 🏗️ Project Structure

```
cronjob-ziroom/
├── .github/workflows/           # GitHub Actions configuration
│   ├── ziroom-runner.yml        # Ziroom monitoring workflow
│   └── 99-runner.yml            # 99.com scraping workflow
├── modules/                      # Functional modules directory
│   ├── ziroom/                  # Ziroom monitoring module
│   │   ├── scraper.py           # Scraping script
│   │   ├── cronjob.sh           # Cron job script
│   │   ├── data.html            # Output file
│   │   └── README.md            # Module documentation
│   └── 99/                      # 99.com scraping module
│       ├── scraper.py           # Basic scraping script
│       ├── cronjob.sh           # Cron job script
│       ├── data.json            # JSON output
│       ├── data.html            # HTML output
│       └── README.md            # Module documentation
├── core/                         # Common core code
│   ├── requirements.txt          # Dependencies
│   └── utils.py                 # Common utility functions
├── README.md                     # Project overview
├── EMAIL_SETUP.md               # Email configuration guide
└── LICENSE
```

## 🚀 Functional Modules

### 1. Ziroom Monitoring Module (`modules/ziroom/`)
- **Function**: Monitor Ziroom rental listings for specific keywords
- **Frequency**: Daily at 12:00 PM
- **Output**: `data.html`
- **Email Subject**: "OpenKikCoc: cronjob-ziroom"

### 2. 99.com Data Scraping Module (`modules/99/`)
- **Function**: Scrape game leaderboard data (number, fwq, player, hkzs)
- **Frequency**: Every 30 minutes
- **Output**: `data.json` and `data.html`
- **Email Subject**: "99.com Data Update Notification"

## 🛠️ Quick Start

### Install Dependencies
```bash
pip3 install -r ./core/requirements.txt
```

### Run Ziroom Monitoring
```bash
bash ./modules/ziroom/cronjob.sh
```

### Run 99.com Scraping
```bash
bash ./modules/99/cronjob.sh
```

## 🔧 Configuration Requirements

### GitHub Secrets
- `QQEMAIL_USERNAME`: QQ email username
- `QQEMAIL_TOKEN`: QQ email authorization token
- `QQEMAIL_RECIPIENTS`: **Comma-separated list of recipient email addresses**

### Environment Variables (Ziroom)
- `URI`: Target website URL
- `KEYWORD`: Search keyword

## 📧 Email Notifications

### Multiple Recipients Support
The project supports sending notifications to multiple recipients using the `QQEMAIL_RECIPIENTS` secret.

**Setup**:
1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Create a new secret named `QQEMAIL_RECIPIENTS`
3. Value: `email1@example.com,email2@example.com,email3@example.com`

**Features**:
- All workflows send emails to the same recipient list
- Easy to add/remove recipients without code changes
- Secure storage using GitHub Secrets

For detailed email configuration, see [EMAIL_SETUP.md](EMAIL_SETUP.md).

## 📊 Automated Execution

GitHub Actions will automatically run:
- **Ziroom**: Daily at 12:00 PM
- **99.com**: Every 30 minutes

## 🎯 Modular Advantages

1. **Clear Separation**: Each functional module is independent and non-interfering
2. **Easy Maintenance**: Code is organized by functionality, making maintenance and updates easier
3. **Flexible Extension**: New data source modules can be easily added
4. **Independent Configuration**: Each module can have its own configuration and dependencies
5. **Multi-Recipient Notifications**: Support for email lists and team notifications

## 📝 Adding New Modules

To add a new data source module:

1. Create a new directory under `modules/`
2. Add scraping scripts and cron job scripts
3. Create corresponding workflow files
4. Update project documentation

## 🔄 Workflow Details

### Ziroom Workflow (`ziroom-runner.yml`)
- **Trigger**: Daily at 12:00 PM
- **Script**: `./modules/ziroom/cronjob.sh`
- **Output**: `modules/ziroom/data.html`
- **Email**: Sent to all recipients in `QQEMAIL_RECIPIENTS` when data changes detected

### 99.com Workflow (`99-runner.yml`)
- **Trigger**: Every 30 minutes
- **Script**: `./modules/99/cronjob.sh`
- **Output**: `modules/99/data.json` and `modules/99/data.html`
- **Email**: Sent to all recipients in `QQEMAIL_RECIPIENTS` when data changes detected

## 🚨 Troubleshooting

### Common Issues
1. **Network Connection**: Ensure stable internet connection
2. **GitHub Secrets**: Verify QQ email credentials and recipient list are properly configured
3. **Python Dependencies**: Check if all required packages are installed
4. **Target Website**: Confirm target websites are accessible

### Debug Steps
1. Check GitHub Actions logs for error details
2. Verify environment variables and secrets configuration
3. Test scripts locally before pushing to GitHub
4. Monitor email notifications for execution status

## 🤝 Contributing

We welcome Issue submissions and Pull Requests to improve the project!

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

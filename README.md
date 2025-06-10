# InstaDM Pro ✨

A powerful Instagram DM automation tool with **advanced anti-detection features** for safe and effective outreach campaigns.

## 🛡️ Advanced Anti-Detection Features

- **Stealth Browser Configuration**: Advanced Chrome options to hide automation traces
- **JavaScript Injection**: Hides `navigator.webdriver` and other automation indicators  
- **Human-Like Behavior**: Realistic scrolling, reading pauses, and interaction patterns
- **Smart Profile Visiting**: Alternates between direct URLs and search functionality
- **Natural Typing Simulation**: Variable typing speeds with occasional corrections
- **Randomized Delays**: Human-like timing variations with extended breaks
- **User Agent Rotation**: Random realistic browser fingerprints
- **Window Size Randomization**: Prevents fingerprinting through consistent window sizes

## 🚀 Core Features

- **Multi-Account Support**: Manage multiple Instagram accounts simultaneously
- **Customizable Delays**: Set delays between messages to avoid account restrictions  
- **Name Personalization**: Use `{name}` variable to personalize messages
- **File Format Support**: Upload leads via .txt, .csv, or .xlsx files
- **Real-time Progress**: Monitor campaign progress with live updates
- **Safety Warnings**: Built-in safety checks and delay recommendations
- **Professional UI**: Modern, user-friendly interface

## 📋 Requirements

- Python 3.7 or higher
- Google Chrome browser (latest version recommended)
- Windows, macOS, or Linux

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd instagram-dm
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test anti-detection features** (recommended)
   ```bash
   python test_anti_detection.py
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://127.0.0.1:8080`

## 🔧 Anti-Detection Testing

Before using the tool, run the anti-detection test to ensure optimal stealth:

```bash
python test_stealth_only.py
```

This will verify:
- ✅ Chrome stealth configuration
- ✅ JavaScript injection working
- ✅ WebDriver traces hidden
- ✅ Human behavior simulation
- ✅ Instagram compatibility

## 📁 File Formats

### CSV/Excel Format
```csv
username,name
john_doe,John Smith
sarah_wilson,Sarah Wilson
```

### Text Format
```
john_doe John Smith
sarah_wilson Sarah Wilson
```

## ⚙️ Configuration

### Delay Settings
- **Conservative**: 60-120 seconds (safest)
- **Moderate**: 30-60 seconds (balanced)
- **Aggressive**: 15-30 seconds (higher risk)

### Message Template
Use `{name}` to personalize messages:
```
Hey {name}! Hope you're doing well. Would love to connect!
```

## 🛡️ Safety Features

- **Automatic delay variation** (±20% randomization)
- **Extended breaks** every 5-10 messages
- **Human-like typing patterns** with corrections
- **Profile visit randomization** (search vs direct URL)
- **Stealth script injection** on every page load

## 🚨 Troubleshooting

### Chrome Driver Issues
```bash
python fix_chrome_driver.py
```

### Detection Issues
1. Run `python test_stealth_only.py`
2. Increase delay settings
3. Use fewer messages per session
4. Take longer breaks between accounts

### Common Solutions
- Update Chrome browser to latest version
- Update undetected-chromedriver: `pip install --upgrade undetected-chromedriver`
- Clear browser cache and cookies
- Use different user agents

## ⚠️ Important Notes

- **Start with conservative settings** (60+ second delays)
- **Test with a small number of messages** first
- **Monitor for any detection warnings**
- **Use high-quality, aged Instagram accounts**
- **Avoid sending identical messages**
- **Respect Instagram's terms of service**

## 📊 Best Practices

1. **Warm up accounts** - Use them manually before automation
2. **Vary your messages** - Don't use identical templates
3. **Limit daily volume** - Max 50-100 messages per account per day
4. **Use realistic delays** - 30+ seconds between messages
5. **Monitor account health** - Watch for restrictions or warnings

## 🔄 Updates

The tool includes automatic anti-detection improvements:
- Regular user agent updates
- Enhanced stealth techniques
- Improved human behavior simulation
- Better delay randomization

## 📞 Support

If you encounter detection issues:
1. Run the anti-detection test: `python test_stealth_only.py`
2. Increase delay settings
3. Check Chrome/ChromeDriver versions
4. Review the troubleshooting section

---

**Disclaimer**: This tool is for educational purposes. Users are responsible for complying with Instagram's terms of service and applicable laws. 

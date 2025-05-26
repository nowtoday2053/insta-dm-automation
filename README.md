# Instagram Messenger Tool

A simple web-based tool to send messages to Instagram users.

## Setup

1. Install Python 3.7 or higher
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## How to Use

1. Run the web application:
   ```
   python app.py
   ```

2. Open your web browser and go to `http://127.0.0.1:3000`

3. On the web interface:
   - Enter your Instagram username and password
   - Enter your message template
   - Upload a text file containing Instagram usernames (one per line)
   - Click "Send Messages"

4. View the results page to see the status of each message sent

## Important Notes

- The tool waits 30 seconds between messages to avoid Instagram's rate limits
- Make sure your leads file contains valid Instagram usernames
- Keep your Instagram credentials secure
- Instagram may temporarily block automated messaging if too many messages are sent in a short time
- The tool will show you the status of each message sent, including any errors that occurred 

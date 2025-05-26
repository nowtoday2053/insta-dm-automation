import os
from instabot import Bot
from dotenv import load_dotenv
import time

def send_messages(username, password, leads_file, message_template):
    # Initialize the bot
    bot = Bot()
    bot.login(username=username, password=password)
    
    # Read leads from file
    with open(leads_file, 'r') as file:
        leads = [line.strip() for line in file if line.strip()]
    
    # Send messages to each lead
    for lead in leads:
        try:
            # Send the message
            bot.send_message(message_template, lead)
            print(f"Message sent to {lead}")
            # Wait 30 seconds between messages to avoid Instagram limits
            time.sleep(30)
        except Exception as e:
            print(f"Failed to send message to {lead}: {str(e)}")
    
    # Logout
    bot.logout()

def main():
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment variables
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in .env file")
        return
    
    # Get leads file path
    leads_file = input("Enter the path to your leads file (one username per line): ")
    if not os.path.exists(leads_file):
        print("Leads file not found!")
        return
    
    # Get message template
    message_template = input("Enter your message template: ")
    
    # Send messages
    send_messages(username, password, leads_file, message_template)

if __name__ == "__main__":
    main() 
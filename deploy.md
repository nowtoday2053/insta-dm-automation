# Deployment Guide for InstaDM Pro

## 🚨 Important Legal Notice
Before deploying, please note:
- Instagram automation may violate Instagram's Terms of Service
- This tool is for educational purposes only
- Users are responsible for compliance with all applicable laws and platform policies
- Consider using on private/test accounts first

## Deployment Options

### Option 1: Local Network Access (Easiest)

**Best for**: Sharing with friends/team members on the same WiFi network

1. **Find your local IP address**:
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address" (usually starts with 192.168.x.x)
   
   # Mac/Linux
   ifconfig
   # Look for inet address under your network interface
   ```

2. **Start the application**:
   ```bash
   cd instagram-dm
   python app.py
   ```

3. **Access from other devices**:
   - Open browser and go to: `http://YOUR_LOCAL_IP:8080`
   - Example: `http://192.168.1.100:8080`

4. **Share with others**: Give them your local IP and port (8080)

---

### Option 2: Cloud VPS Deployment (Recommended)

**Best for**: Public access, multiple users, remote access

#### A. DigitalOcean/Linode/Vultr Deployment

1. **Create a VPS** (minimum 2GB RAM, 1 CPU)
2. **Connect via SSH** and install dependencies:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python, pip, git
   sudo apt install -y python3 python3-pip git
   
   # Clone your repository
   git clone YOUR_REPOSITORY_URL
   cd instagram-dm
   
   # Install Python dependencies
   pip3 install -r requirements.txt
   
   # Install Chrome dependencies
   sudo apt install -y wget gnupg xvfb
   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
   echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
   sudo apt update
   sudo apt install -y google-chrome-stable
   ```

3. **Run with virtual display**:
   ```bash
   # Start virtual display for Chrome
   export DISPLAY=:99
   Xvfb :99 -screen 0 1280x720x24 &
   
   # Run the application
   python3 app.py
   ```

4. **Access**: `http://YOUR_VPS_IP:8080`

#### B. Docker Deployment (Advanced)

1. **Install Docker** on your VPS:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Deploy with Docker Compose**:
   ```bash
   git clone YOUR_REPOSITORY_URL
   cd instagram-dm
   sudo docker-compose up -d
   ```

3. **Access**: `http://YOUR_VPS_IP:8080`

---

### Option 3: Heroku Deployment (Free Tier Available)

**Note**: Heroku has limitations with browser automation but can work with additional configuration.

1. **Install Heroku CLI** and login
2. **Create Procfile**:
   ```
   web: python app.py
   ```

3. **Add buildpacks**:
   ```bash
   heroku buildpacks:add --index 1 heroku/python
   heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-google-chrome
   heroku buildpacks:add --index 3 https://github.com/heroku/heroku-buildpack-chromedriver
   ```

4. **Deploy**:
   ```bash
   git init
   git add .
   git commit -m "Initial deploy"
   heroku create your-app-name
   git push heroku main
   ```

---

### Option 4: Railway/Render Deployment

**Railway** and **Render** offer similar Docker-based deployments with good free tiers.

1. **Connect your GitHub repository**
2. **Add environment variables**:
   - `DISPLAY=:99`
   - `FLASK_ENV=production`
3. **Use the provided Dockerfile**
4. **Deploy automatically from Git**

---

## Security Considerations

### For Production Deployment:

1. **Add environment variables for sensitive data**:
   ```python
   import os
   app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')
   ```

2. **Add authentication** (optional):
   ```python
   from functools import wraps
   
   def login_required(f):
       @wraps(f)
       def decorated_function(*args, **kwargs):
           if 'authenticated' not in session:
               return redirect(url_for('login'))
           return f(*args, **kwargs)
       return decorated_function
   ```

3. **Use HTTPS** with SSL certificates (Let's Encrypt)

4. **Add rate limiting**:
   ```bash
   pip install Flask-Limiter
   ```

5. **Use a reverse proxy** (Nginx) for production

---

## Monitoring and Maintenance

### Process Management with PM2:
```bash
# Install PM2
npm install -g pm2

# Start application
pm2 start app.py --name instagram-dm --interpreter python3

# Monitor
pm2 status
pm2 logs instagram-dm

# Auto-restart on reboot
pm2 startup
pm2 save
```

### Log Monitoring:
```bash
# View real-time logs
tail -f /var/log/instagram-dm.log
```

---

## Troubleshooting

### Common Issues:

1. **Chrome not found**:
   ```bash
   # Install Chrome manually
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo dpkg -i google-chrome-stable_current_amd64.deb
   sudo apt-get install -f
   ```

2. **Display issues**:
   ```bash
   # Start virtual display
   sudo apt install xvfb
   export DISPLAY=:99
   Xvfb :99 -screen 0 1280x720x24 &
   ```

3. **Memory issues**:
   - Use VPS with at least 2GB RAM
   - Add swap space if needed

4. **Port blocked**:
   ```bash
   # Check if port is open
   sudo ufw allow 8080
   ```

---

## Cost Estimates

### VPS Options:
- **DigitalOcean**: $5-12/month (1-2GB RAM)
- **Linode**: $5-10/month
- **Vultr**: $5-10/month

### Free Options:
- **Railway**: Free tier with limitations
- **Render**: Free tier with sleep mode
- **Heroku**: Free tier (limited hours)

---

## Next Steps

1. Choose your deployment method
2. Set up domain name (optional): Use Cloudflare or Namecheap
3. Configure SSL certificate
4. Set up monitoring and backups
5. Add authentication if needed for public access

**Need help with any specific deployment option? Let me know which method you'd prefer!** 
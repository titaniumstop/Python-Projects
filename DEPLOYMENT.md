# Deployment Guide - FPS Game Web Edition

## Quick Deploy to Free Hosting

Your game can be deployed to multiple free hosting platforms. Here are the easiest options:

## Option 1: Netlify (Recommended - Easiest)

1. **Zip your files**:
   ```bash
   zip -r fps-game-web.zip index.html game.js style.css
   ```

2. **Go to [netlify.com](https://netlify.com)**
   - Sign up for free
   - Click "Add new site" → "Deploy manually"
   - Drag and drop your `fps-game-web.zip` file
   - Your game will be live in seconds!

3. **Get your public URL**: You'll get something like `https://your-game-name.netlify.app`

## Option 2: GitHub Pages

1. **Create a GitHub repository**:
   ```bash
   git init
   git add index.html game.js style.css
   git commit -m "FPS Game Web Edition"
   git remote add origin https://github.com/YOUR_USERNAME/fps-game.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**:
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: Deploy from branch `main`
   - Your game will be at: `https://YOUR_USERNAME.github.io/fps-game`

## Option 3: Vercel

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   vercel
   ```

3. **Follow the prompts** - your game will be live instantly!

## Option 4: Surge.sh (Simple & Fast)

1. **Install Surge**:
   ```bash
   npm install -g surge
   ```

2. **Deploy**:
   ```bash
   surge
   ```

3. **Follow the prompts** - you'll get a URL like `your-game-name.surge.sh`

## Option 5: Firebase Hosting

1. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   ```

2. **Initialize and deploy**:
   ```bash
   firebase login
   firebase init
   # Select: Hosting
   # Public directory: . (current directory)
   # Single-page app: No
   # Set up automatic builds: No
   
   firebase deploy
   ```

3. **Your game will be live** at your Firebase hosting URL

## Testing Locally

Before deploying, test your game locally:

```bash
# Using Python's built-in server:
python3 -m http.server 8000

# Or using Node.js:
npx serve

# Then open: http://localhost:8000
```

## Recommended: Netlify Drop

The absolute easiest method:
1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag your entire project folder
3. Done! Your game is live

## Share Your Game!

Once deployed, you can share the URL with anyone in the world!

## Custom Domain (Optional)

All platforms support custom domains:
- Netlify: Settings → Domain management
- GitHub Pages: Settings → Pages → Custom domain
- Vercel: Project settings → Domains

Choose the method that works best for you. Netlify Drop is recommended for beginners!


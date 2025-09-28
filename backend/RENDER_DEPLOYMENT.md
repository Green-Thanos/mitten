# Render Deployment Guide for Mitten Backend

## 🚀 Quick Deploy to Render

### 1. Repository Setup

- Push your code to GitHub
- Connect your GitHub repository to Render

### 2. Render Service Configuration

#### Service Type

- **Type**: Web Service
- **Environment**: Python 3.11

#### Build Command

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH="$HOME/.local/bin:$PATH" && uv sync
```

#### Start Command

```bash
uv run python main.py
```

#### Alternative (if uv fails)

**Build Command:**

```bash
pip install -r requirements.txt
```

**Start Command:**

```bash
python main.py
```

### 3. Environment Variables

Set these in Render dashboard:

| Variable                  | Description               | Required |
| ------------------------- | ------------------------- | -------- |
| `GEMINI_API_KEY`          | Your Gemini API key       | Yes      |
| `GOOGLE_SEARCH_API_KEY`   | Google Search API key     | No       |
| `GOOGLE_SEARCH_ENGINE_ID` | Google Search Engine ID   | No       |
| `PORT`                    | Port (auto-set by Render) | No       |

### 4. Health Check

- **Path**: `/health`
- **Expected Response**: `{"status": "healthy"}`

### 5. Static Files

- **Directory**: `static/images/`
- **Purpose**: Generated visualizations and images

## 🔧 Local Testing

### Test the build process locally:

```bash
cd backend
chmod +x build.sh
./build.sh
```

### Test the start command:

```bash
uv run python main.py
```

### Test with environment variables:

```bash
export GEMINI_API_KEY="your-key-here"
export PORT=8000
uv run python main.py
```

## 📊 API Endpoints

Once deployed, your API will be available at:

- **Base URL**: `https://your-app-name.onrender.com`
- **Health Check**: `https://your-app-name.onrender.com/health`
- **API Docs**: `https://your-app-name.onrender.com/docs`
- **Main Query**: `POST https://your-app-name.onrender.com/api/v1/query`

## 🐛 Troubleshooting

### Common Issues:

1. **Build Fails - uv not found**

   - Use the alternative build command with pip
   - Ensure Python 3.11 is selected

2. **Start Fails - Module not found**

   - Check that all dependencies are in requirements.txt
   - Verify the Python path is correct

3. **Health Check Fails**

   - Check that the `/health` endpoint exists
   - Verify the app starts without errors

4. **CORS Issues**
   - The app is configured with permissive CORS for hackathon
   - Update CORS settings for production

### Debug Commands:

```bash
# Check if app starts locally
uv run python main.py

# Check dependencies
uv pip list

# Test health endpoint
curl http://localhost:8000/health
```

## 🔄 Deployment Process

1. **Push to GitHub**

   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Render Auto-Deploy**

   - Render will automatically detect changes
   - Build and deploy your application
   - Monitor logs for any issues

3. **Verify Deployment**
   - Check health endpoint
   - Test API endpoints
   - Review logs in Render dashboard

## 📈 Monitoring

- **Logs**: Available in Render dashboard
- **Metrics**: CPU, Memory, Response times
- **Health**: Automatic health checks every 30s

## 🎯 Production Considerations

1. **Environment Variables**: Store sensitive keys securely
2. **CORS**: Restrict origins for production
3. **Rate Limiting**: Add rate limiting for API endpoints
4. **Caching**: Implement caching for better performance
5. **Monitoring**: Set up proper logging and monitoring

## 🚀 Success!

Once deployed, your Mitten backend will be live and ready to serve environmental data queries for Michigan! 🌍✨

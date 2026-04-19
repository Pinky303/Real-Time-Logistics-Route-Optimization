# Setup Guide: Upload to GitHub

Step-by-step instructions to export this repository from Databricks and upload to GitHub.

## Step 1: Export the Notebook

### Option A: Using Databricks UI (Recommended)

1. Open your notebook: [Kinesis GPS Coordinates Streaming](#notebook-1155211729462411)
2. Click **File** → **Export** → **IPython Notebook (.ipynb)**
3. Save the file as `kinesis_streaming_pipeline.ipynb`
4. **Important**: Move this file to `/delivery-driver-streaming-pipeline/notebooks/` directory

### Option B: Using Databricks CLI

```bash
# Install Databricks CLI if not already installed
pip install databricks-cli

# Configure authentication
databricks configure --token
# Enter your workspace URL and personal access token

# Export the notebook
databricks workspace export \
  /Users/pinky.somwani.cs17@ggits.net/"Kinesis GPS Coordinates Streaming" \
  ./kinesis_streaming_pipeline.ipynb \
  --format JUPYTER

# Move to notebooks directory
mv kinesis_streaming_pipeline.ipynb delivery-driver-streaming-pipeline/notebooks/
```

## Step 2: Download the Repository from Databricks

### Option A: Using Databricks UI

1. Navigate to the [delivery-driver-streaming-pipeline](#folder-563989166440118) folder
2. Right-click on the folder
3. Select **Export** → **DBC Archive** or **Directory**
4. Download to your local machine
5. Extract if needed

### Option B: Using Databricks CLI (Recommended)

```bash
# Export entire directory
databricks workspace export_dir \
  /Users/pinky.somwani.cs17@ggits.net/delivery-driver-streaming-pipeline \
  ./delivery-driver-streaming-pipeline \
  --overwrite

# This creates a local copy of all files
```

## Step 3: Initialize Git Repository

```bash
# Navigate to the project directory
cd delivery-driver-streaming-pipeline

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Real-time delivery driver efficiency pipeline"
```

## Step 4: Create GitHub Repository

### Via GitHub Website:

1. Go to [https://github.com/new](https://github.com/new)
2. Repository name: `delivery-driver-streaming-pipeline`
3. Description: *Real-time delivery driver efficiency & route optimization pipeline using Databricks, AWS Kinesis, and Delta Lake*
4. Choose **Public** or **Private**
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **Create repository**

### Via GitHub CLI:

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Create repository
gh repo create delivery-driver-streaming-pipeline \
  --public \
  --description "Real-time delivery driver efficiency & route optimization pipeline" \
  --source=. \
  --push
```

## Step 5: Push to GitHub

```bash
# Add remote origin (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/delivery-driver-streaming-pipeline.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 6: Verify Upload

1. Visit your GitHub repository: `https://github.com/yourusername/delivery-driver-streaming-pipeline`
2. Verify all files are present:
   - ✅ README.md
   - ✅ requirements.txt
   - ✅ .gitignore
   - ✅ LICENSE.py
   - ✅ config/
   - ✅ notebooks/ (with your notebook)
   - ✅ docs/
   - ✅ data/

## Step 7: Add Repository Badges (Optional)

Add these badges to your README.md:

```markdown
[![GitHub Stars](https://img.shields.io/github/stars/yourusername/delivery-driver-streaming-pipeline?style=social)](https://github.com/yourusername/delivery-driver-streaming-pipeline)
[![GitHub Forks](https://img.shields.io/github/forks/yourusername/delivery-driver-streaming-pipeline?style=social)](https://github.com/yourusername/delivery-driver-streaming-pipeline)
[![GitHub Issues](https://img.shields.io/github/issues/yourusername/delivery-driver-streaming-pipeline)](https://github.com/yourusername/delivery-driver-streaming-pipeline/issues)
```

## Step 8: Add Topics/Tags

On GitHub, add relevant topics to your repository:
- `databricks`
- `pyspark`
- `aws-kinesis`
- `delta-lake`
- `streaming`
- `real-time-analytics`
- `medallion-architecture`
- `route-optimization`
- `data-engineering`
- `spark-streaming`

## Troubleshooting

### Issue: Notebook not exporting
**Solution**: Make sure the notebook is not running. Stop all cells before exporting.

### Issue: Git authentication failed
**Solution**: Use a Personal Access Token (PAT) instead of password:
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Use token as password when pushing

### Issue: Files too large
**Solution**: Add large files to .gitignore:
```bash
echo "*.csv" >> .gitignore
echo "*.parquet" >> .gitignore
git rm --cached <large-file>
git commit -m "Remove large files"
```

### Issue: Databricks CLI not found
**Solution**: 
```bash
pip install --upgrade databricks-cli
```

## Alternative: Clone from GitHub Back to Databricks

Once your code is on GitHub, others can import it to Databricks:

### Method 1: Databricks Repos (Git Integration)
1. In Databricks, go to **Repos**
2. Click **Add Repo**
3. Enter your GitHub URL: `https://github.com/yourusername/delivery-driver-streaming-pipeline`
4. Click **Create**

### Method 2: Databricks CLI
```bash
# Clone and import to Databricks
git clone https://github.com/yourusername/delivery-driver-streaming-pipeline.git
cd delivery-driver-streaming-pipeline

databricks workspace import_dir \
  . \
  /Users/your.email@domain.com/delivery-driver-streaming-pipeline \
  --overwrite
```

## Best Practices

1. **Never commit secrets**: AWS keys, tokens, passwords
2. **Use .gitignore**: Exclude checkpoints, logs, data files
3. **Write clear commits**: Use descriptive commit messages
4. **Tag releases**: Use semantic versioning (v1.0.0, v1.1.0, etc.)
5. **Document changes**: Update README.md and CHANGELOG.md

## Next Steps

1. ✅ Upload to GitHub (you are here)
2. 📝 Write a detailed README (already provided)
3. 🎯 Add GitHub Actions for CI/CD (optional)
4. 📊 Create project wiki or documentation site
5. 🌟 Share with the community
6. 🤝 Accept contributions via pull requests

## Quick Commands Reference

```bash
# Check git status
git status

# Add changes
git add .

# Commit changes
git commit -m "Your message"

# Push changes
git push origin main

# Pull latest changes
git pull origin main

# Create new branch
git checkout -b feature/new-feature

# View commit history
git log --oneline
```

## Support

If you encounter issues:
- 📖 Read [GitHub Docs](https://docs.github.com/)
- 📖 Read [Databricks CLI Docs](https://docs.databricks.com/dev-tools/cli/index.html)
- 💬 Ask in [GitHub Discussions](https://github.com/yourusername/delivery-driver-streaming-pipeline/discussions)

---

**Good luck with your GitHub repository! 🚀**
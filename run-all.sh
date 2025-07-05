# File: run_all.sh
#!/bin/bash
set -e

cd /home/ubuntu/news-scraper-and-embedder

# [1] Run Website Scraper
echo "Running for Web Scraper";
python3 scraper/aggregator.py -c scraper/config.yaml
echo "Web Scraper Pipeline run complete."

# [2] Run YouTube Scraper
echo "Running for Youtube Scraper";
python3 scraper/youtube_scraper.py
echo "Youtube Scrapper Pipeline run complete."

# [3] Run Vector Embedding Pipeline
echo "Running for Vector Embedding";
python3 vector_embedding/vector_embedding_pipeline.py
echo "Vector Embedding Pipeline run complete."

# Log Completion
echo "Data Scrapping, Data Processing and Data Storage in Vector DB Pipeline run complete."
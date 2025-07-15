#!/bin/bash
set -e

# Activate your venv (adjust path if needed)
source /home/ubuntu/venv/bin/activate

cd /home/ubuntu/news-scraper-and-embedder

# [1] Run Website Scraper
echo "Running for Web Scraper";
python scraper/aggregator.py -c scraper/config.yaml
echo "Web Scraper Pipeline run complete."

# [2] Run YouTube Scraper
echo "Running for Youtube Scraper";
python scraper/youtube_scraper.py
echo "Youtube Scrapper Pipeline run complete."

# [3] Upload scraped_articles to S3
echo "Uploading scraped_articles to S3";
python scraper/upload_data_to_s3.py
echo "Upload of scraped_articles complete."

# [3] Run Vector Embedding Pipeline
echo "Running for Vector Embedding";
python vector_embedding/vector_embedding_pipeline.py
echo "Vector Embedding Pipeline run complete."

# # Log Completion
echo "Data Scrapping, Data Processing and Data Storage in Vector DB Pipeline run complete."
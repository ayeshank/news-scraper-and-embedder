import os
import pandas as pd
import logging
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import nltk
import boto3
from botocore.exceptions import NoCredentialsError

# ========== LOGGING CONFIGURATION ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(module)s] %(message)s"
)

# ========== CONFIGURATION ==========
CSV_FOLDER_PATH = "/home/ubuntu/shared_data/scraped_articles/"
CHROMA_PERSIST_DIR = "/home/ubuntu/shared_data/vector_db/"
S3_BUCKET_NAME = "llm-instance-bucket"
S3_SCRAPED_FOLDER = "scraped_articles/"
S3_VECTOR_DB_FOLDER = "vector_db/"
CHROMA_COLLECTION_NAME = "news_articles"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
# ====================================

nltk.download("punkt")

def load_and_clean_csv(folder_path: str) -> pd.DataFrame:
    logging.info("CSV-1001: Loading And Cleaning CSV Begins.")
    try:
        all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
        if not all_files:
            logging.warning("CSV-1002: No CSV Files Found In The Folder.")
            return pd.DataFrame()

        dfs = []
        for file in all_files:
            file_path = os.path.join(folder_path, file)
            logging.info(f"CSV-1003: Reading File: {file}")

            try:
                df = pd.read_csv(file_path)
                if df.empty or "article_content" not in df.columns:
                    logging.warning(f"CSV-1005: Skipping empty or invalid file: {file}")
                    continue
                df["source_file"] = file
                dfs.append(df)
            except pd.errors.EmptyDataError:
                logging.warning(f"CSV-1006: Skipping corrupt or empty CSV: {file}")
                continue

        if not dfs:
            logging.warning("CSV-1007: No usable data found in any CSV.")
            return pd.DataFrame()

        combined = pd.concat(dfs, ignore_index=True)
        combined = combined[combined["article_content"].notnull()]
        logging.info(f"CSV-1004: Loaded And Cleaned {len(combined)} Articles.")
        return combined[["title", "date", "article_content", "article_url", "source_file"]]

    except Exception as e:
        logging.error(f"CSV-1099: Error In Loading And Cleaning Files: {e}")
        raise


def chunk_articles(df: pd.DataFrame) -> list:
    logging.info("CHUNK-1001: Chunking Articles Begins.")
    try:
        docs = [
            Document(
                page_content=row["article_content"],
                metadata={
                    "title": row["title"],
                    "date": row["date"],
                    "source": row["source_file"],
                    "url": row["article_url"]
                }
            )
            for _, row in df.iterrows()
        ]
        splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separator="\n")
        chunked_docs = splitter.split_documents(docs)
        logging.info(f"CHUNK-1002: Chunking Complete: {len(chunked_docs)} Chunks Created.")
        return chunked_docs
    except Exception as e:
        logging.error(f"CHUNK-1099: Error In Chunking Articles: {e}")
        raise

def embed_and_store_chunks(docs: list, persist_path: str) -> Chroma:
    logging.info("EMBED-1001: Embedding And Storing In Vector Db Begins.")
    try:
        embedding_model = HuggingFaceEmbeddings(model_name=EMBED_MODEL_NAME)
        vectordb = Chroma.from_documents(documents=docs, embedding=embedding_model, persist_directory=persist_path, collection_name=CHROMA_COLLECTION_NAME)
        logging.info("EMBED-1002: Embeddings Stored Successfully In ChromaDB.")
        return vectordb
    except Exception as e:
        logging.error(f"EMBED-1099: Error In Embedding Creation And Storing In Vector Db: {e}")
        raise


def upload_folder_to_s3(local_folder, s3_prefix):
    s3 = boto3.client('s3')
    for root, _, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = os.path.join(s3_prefix, os.path.relpath(local_path, local_folder))
            try:
                s3.upload_file(local_path, S3_BUCKET_NAME, s3_path)
                logging.info(f"S3-UPLOAD: Uploaded {local_path} to s3://{S3_BUCKET_NAME}/{s3_path}")
            except NoCredentialsError:
                logging.error("S3-UPLOAD-ERROR: AWS credentials not found")

if __name__ == "__main__":
    logging.info("EMBED-PIPELINE-0001: Starting News Data Preprocessing And Embedding Genertion.")
    try:
        df = load_and_clean_csv(CSV_FOLDER_PATH)
        if df.empty:
            logging.warning("EMBED-PIPELINE-0002: No Valid Articles To Process | Exiting Embedding Pipeline.")
        else:
            chunked_docs = chunk_articles(df)
            vectordb = embed_and_store_chunks(chunked_docs, CHROMA_PERSIST_DIR)
            upload_folder_to_s3(CHROMA_PERSIST_DIR, S3_VECTOR_DB_FOLDER)
            logging.info("EMBED-PIPELINE-0003: Embedding Pipeline All Steps Completed Successfully.")
    except Exception as pipeline_error:
        logging.critical(f"EMBED-PIPELINE-0099: Embedding Pipeline Execution Failed: {pipeline_error}")
import os
import sys

# Ensure Kaggle credentials are read
os.environ['KAGGLE_CONFIG_DIR'] = 'C:\\Users\\coolt\\.kaggle'

class KaggleDownloader:
    def __init__(self):
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            self.api = KaggleApi()
            self.api.authenticate()
            self.authenticated = True
        except Exception as e:
            print(f"Kaggle API Auth failed: {e}")
            self.authenticated = False

    def download_dataset(self, dataset_ref, output_dir):
        if not self.authenticated:
            print("Cannot download, Kaggle API not authenticated.")
            return False
            
        os.makedirs(output_dir, exist_ok=True)
        print(f"Downloading dataset {dataset_ref} to {output_dir}...")
        
        try:
            # download_files downloads and unzips
            self.api.dataset_download_files(dataset_ref, path=output_dir, unzip=True)
            print("Download and extraction complete.")
            return True
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return False

if __name__ == "__main__":
    downloader = KaggleDownloader()
    # Using a small, lightweight player rating dataset for testing
    downloader.download_dataset("spsanderson/soccer-players-dataset", "data/raw/kaggle")

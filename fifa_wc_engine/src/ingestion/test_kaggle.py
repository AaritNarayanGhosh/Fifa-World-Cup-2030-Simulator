import os
import sys

# Set Kaggle config dir explicitly to make sure it finds the json file
os.environ['KAGGLE_CONFIG_DIR'] = 'C:\\Users\\coolt\\.kaggle'

try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    print("Kaggle API Authenticated successfully!")
    
    # Search for a popular small soccer dataset
    datasets = api.dataset_list(search='fifa 22 player ratings')
    print("Found datasets:")
    for ds in datasets[:3]:
        print(f"- {ds.ref} (Size: {ds.size})")
        
except Exception as e:
    print(f"Kaggle API authentication error: {e}")
    sys.exit(1)

from datasets import load_dataset
import pandas as pd
import os

os.makedirs('data', exist_ok=True)
os.makedirs('artifacts', exist_ok=True)

print('Downloading dataset...')
ds = load_dataset('pirocheto/phishing-url', split='train')
df = pd.DataFrame(ds)
df['label'] = (df['status'] == 'phishing').astype(int)
df[['url', 'label']].to_csv('data/urls.csv', index=False)
print('Dataset ready. Training model...')

import timeit
start = timeit.default_timer()
from google.cloud import storage

stop = timeit.default_timer()
print stop - start 
import os

#export GOOGLE_APPLICATION_CREDENTIALS="/home/zacharypina/Downloads/Hello World-7c3a539b6bb0.json"
start1 = timeit.default_timer()

storage_client = storage.Client.from_service_account_json('./Hello World-dfcb81f30525.json')

# TODO (Developer): Replace this with your Cloud Storage bucket name.
bucket_name = 'my_test_bucket32'
bucket = storage_client.get_bucket(bucket_name)

# TODO (Developer): Replace this with the name of the local file to upload.
source_file_name = '105.0e6.npz'
blob = bucket.blob(os.path.basename(source_file_name))

# Upload the local file to Cloud Storage.
blob.upload_from_filename(source_file_name)

print('File {} uploaded to {}.'.format(source_file_name, bucket))

stop1 = timeit.default_timer()
print stop1 - start1 

start2 = timeit.default_timer()

blob.download_to_filename('Marble_data.txt')

stop2 = timeit.default_timer()
print stop2 - start2
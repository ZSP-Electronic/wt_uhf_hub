import timeit

def run_quickstart():
    from google.cloud import datastore

    # Instantiates a client
    client = datastore.Client.from_service_account_json('./Hello World-7e6f498f5c75.json')

    key_complete = client.key('mylist', 'UHF_Hub_test')
    print(key_complete)
    
    start1 = timeit.default_timer()
    task = client.get(key_complete)
    stop1 = timeit.default_timer()
    #task = datastore.Entity(key=key_complete)
    #print(task)
    print(stop1 - start1)
    
    request = task['Request']
    minFreq = task['min_frequency']
    maxfreq = task['max_frequency']
    samprate= task['sample_rate']
    
    data = [request, minFreq, maxfreq, samprate]
    print(data)
    
    start2 = timeit.default_timer()
    task['Request'] = True
    task['sample_rate'] = 2.048e6
    client.put(task)
    stop2 = timeit.default_timer()
    print(stop2 - start2)
    

if __name__ == '__main__':
    run_quickstart()
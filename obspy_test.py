from obspy.clients.seedlink.easyseedlink import create_client

def handle_data(trace):
    print('Received the following trace:')
    print(trace)
    print()

client = create_client('rtserve.iris.washington.edu:18000',

                   handle_data)

client.select_stream('US', 'HLID', 'BHZ')

client.run()
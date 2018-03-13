from connection import api_client
import datetime

# This script will Port a number back and forward between two Carriers.
# Each time the script runs, it does a Number Enquiry to see who the current Carrier is, and will port to which ever carrier currently does not hold the number

# IPMS Interface. Either TRAIN, TEST, or LIVE
ipms_interface = api_client.IPMS_TRAIN

# First Carrier Details
carrier1 = {
    'username': 'wxc',
    'password': '',
    'company_id': 6,
    'carrier_id': 11987,
    'service_provider_id': 19,
    'connection': None
}

carrier2 = {
    'username': 'wxc',
    'password': '',
    'company_id': 6,
    'carrier_id': 11248,
    'service_provider_id': 19,
    'connection': None
}

# Number to port
number_to_port = '099864000'

# How many test loops to run
loop_count = 1

# log HTTP and SOAP requests/responses to console
log_http_detail = False

# Create first Connection to IPMS
carrier1['connection'] = api_client.IPMSConnection(ipms_interface=api_client.IPMS_TRAIN,
                                                   username=carrier1['username'],
                                                   password=carrier1['password'],
                                                   company_id=carrier1['company_id'],
                                                   extra_logging=log_http_detail)

# Create second Connection to IPMS
carrier2['connection'] = api_client.IPMSConnection(ipms_interface=api_client.IPMS_TRAIN,
                                                   username=carrier2['username'],
                                                   password=carrier1['password'],
                                                   company_id=carrier2['company_id'],
                                                   extra_logging=log_http_detail)

# Get list of Carriers and Service providers. This is used to output readable names of Carriers and Service Providers when logging our progress
carrier_list = carrier1['connection'].carriers
service_provider_list = carrier1['connection'].service_providers

for i in range(loop_count):
    print('Running Test Loop, Round {}'.format(i + 1))

    # Get Current Carrier Information
    number_info = carrier1['connection'].number_enquiry(number_to_port)
    current_carrier_id = number_info['carrierId']
    current_service_provider_id = number_info['serviceProviderId']
    print("Number {} is currently ported to Carrier '{}', Service Provider '{}'".format(number_to_port, carrier_list[current_carrier_id]['name'], service_provider_list[current_service_provider_id]['name']))

    # Figure out who to port the number from and to
    if current_carrier_id == carrier1['carrier_id']:
        gaining_carrier = carrier2
        losing_carrier = carrier1
    elif current_carrier_id == carrier2['carrier_id']:
        gaining_carrier = carrier1
        losing_carrier = carrier2
    else:
        raise Exception('Number is not ported to either of the configured Carriers')

    # Request Port

    today = datetime.datetime.now()
    rfs_date = datetime.datetime(today.year, today.month, today.day, 8, 0, 0, 0) + datetime.timedelta(days=2) # 8am two days from now
    number_port = {
        'accountNumber': '12345678',
        'customerName': 'Test',
        'gainingCarrierId': gaining_carrier['carrier_id'],
        'gainingServiceProviderId': gaining_carrier['service_provider_id'],
        'losingServiceProviderId': losing_carrier['service_provider_id'],
        'numbers': [
            {
                'gainingCarrierId': gaining_carrier['carrier_id'],
                'losingCarrierId': losing_carrier['carrier_id'],
                'phoneNumber': {
                    'phoneNumber': number_to_port
                }
            }
        ],
        'rfsDateTimeStart': rfs_date,
    }
    gaining_carrier['connection'].request_port(number_port)
from connection import api_client
import datetime

# This script will Port a number back and forward between two Carriers.
# Each time the script runs, it does a Number Enquiry to see who the current Carrier is, and will port to which ever carrier currently does not hold the number

# IPMS Interface. Either TRAIN, TEST, or LIVE
ipms_interface = api_client.IPMS_TEST

# First Carrier Details
carrier1 = {
    'username': 'VNGS_API_TEST',
    'password': '2XfuqUi6XrgU',
    'company_id': 6,
    'carrier_id': 11987,
    'service_provider_id': 19,
    'connection': None
}

carrier2 = {
    'username': 'FBN_VNGS_API_TEST',
    'password': 'HLFN7eSa3p4u',
    'company_id': 106,
    'carrier_id': 99947,
    'service_provider_id': 106,
    'connection': None
}

# Number to port
number_to_port = '099500000'

# How many test loops to run
loop_count = 1

# log HTTP and SOAP requests/responses to console
log_http_detail = False

# Create first Connection to IPMS
carrier1['connection'] = api_client.IPMSConnection(ipms_interface=ipms_interface,
                                                   username=carrier1['username'],
                                                   password=carrier1['password'],
                                                   company_id=carrier1['company_id'],
                                                   extra_logging=log_http_detail)

# Create second Connection to IPMS
carrier2['connection'] = api_client.IPMSConnection(ipms_interface=ipms_interface,
                                                   username=carrier2['username'],
                                                   password=carrier2['password'],
                                                   company_id=carrier2['company_id'],
                                                   extra_logging=log_http_detail)

# Get list of Carriers and Service providers. This is used to output readable names of Carriers and Service Providers when logging our progress
carrier_list = carrier1['connection'].carriers
service_provider_list = carrier1['connection'].service_providers

for i in range(loop_count):
    print('---')
    print('Running Test Loop, Round {}'.format(i + 1))

    # Get Current Carrier Information
    number_info = carrier1['connection'].number_enquiry(number_to_port)
    current_carrier_id = number_info['carrierId']
    current_service_provider_id = number_info['serviceProviderId']
    if (current_carrier_id is not None):
        print("Number {} is currently ported to Carrier '{}', Service Provider '{}'".format(number_to_port, carrier_list[current_carrier_id]['name'], service_provider_list[current_service_provider_id]['name']))
    else:
        print("Number {} is not currently ported.".format(number_to_port))

    # Figure out who to port the number from and to
    if current_carrier_id is None or current_carrier_id == carrier1['carrier_id']:
        gaining_carrier = carrier2
        losing_carrier = carrier1
    elif current_carrier_id == carrier2['carrier_id']:
        gaining_carrier = carrier1
        losing_carrier = carrier2
    else:
        raise Exception('Number is not ported to either of the configured Carriers')

    print('Creating New Port Request')
    print('Gaining Carrier ID: {}, Carrier Name: {}'.format(gaining_carrier['carrier_id'], gaining_carrier['connection'].carriers[gaining_carrier['carrier_id']]['name']))
    print('Losing Carrier ID: {}, Carrier Name: {}'.format(losing_carrier['carrier_id'], losing_carrier['connection'].carriers[losing_carrier['carrier_id']]['name']))

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
    response = gaining_carrier['connection'].request_port(number_port)
    success = response['success']

    som = 0
    port_in_progress = False

    if not success:
        for error in response['errors']:
            if error['error']['code'] == 520:
                port_in_progress = True
        if port_in_progress:
            som = response['som']
            print('Port is already in progress for Number: {}, SOM: {}'.format(number_to_port, som))

    # Submit LSP Response
    number_port_response = None
    if success:
        som = response['som']
        print('SOM: {}'.format(som))

        number_port_response = {
            'som': som,
            'customerName': number_port['customerName'],
            'accountNumber': number_port['accountNumber'],
            'numbers': number_port['numbers']
        }
        response = losing_carrier['connection'].submit_port_response(number_port_response)
        success = response['success']

    # GSP Approve Port
    if success:
        response = gaining_carrier['connection'].approve_port(number_port_response)
        success = response['success']

    # GSP Request Approved Port Change
    apc_data = {}
    if success:
        apc_data = {
            'lspOverride': False,
            'numbers': number_port['numbers'],
            'rfsDateTimeStart': datetime.datetime.now().replace(hour=8, minute=0, second=0),
            'som': som
        }
        response = gaining_carrier['connection'].request_approved_port_change(apc_data)
        success = response['success']

    # LSP Get Approved Port Change Requests
    version = 0
    if success:
        params = {
            'som': som
        }
        response = losing_carrier['connection'].get_approved_port_change_requests(params)
        success = response['success']
        if success:
            version = response['approvedPortChangeRequests'][0]['version']

    # LSP Approve Port Change Request
    if success:
        params = {
            'som': som,
            'version': version
        }
        response = losing_carrier['connection'].accept_approved_port_change_request(params)
        success = response['success']

    # GC Activate Port
    if success:
        response = gaining_carrier['connection'].activate_port({ 'som': som })
        success = response['success']

    # GC Get Port Progress
    if success:
        response = gaining_carrier['connection'].get_port_progress({ 'som': som })
        print(response)
        success = response['success']
from connection import api_client
from random import randint
import datetime

# This script will Port a number back and forward between two Carriers.
# Each time the script runs, it does a Number Enquiry to see who the current Carrier is, and will port to which ever carrier currently does not hold the number

# IPMS Interface. Either TRAIN, TEST, or LIVE
ipms_interface = api_client.IPMS_TEST

# VNGS Local Carrier
carrier_vngs_local = {
    'username': 'VNGS_API_TEST',
    'password': '', # Removed
    'company_id': 6,
    'carrier_id': 11987,
    'service_provider_id': 19,
    'connection': None
}

# FBN VNGS Local Carrier
carrier_fbn_vngs_local = {
    'username': 'FBN_VNGS_API_TEST',
    'password': '', # Removed
    'company_id': 106,
    'carrier_id': 99947,
    'service_provider_id': 106,
    'connection': None
}

# Dummy Local Carrier
carrier_dummy_local = {
    'username': 'VNGS_Test',
    'password': '', # Removed
    'company_id': 200,
    'carrier_id': 99017,
    'service_provider_id': 201,
    'connection': None
}

# log HTTP and SOAP requests/responses to console
log_http_detail = False

# Create VNGS Connection
carrier_vngs_local['connection'] = api_client.IPMSConnection(ipms_interface=ipms_interface,
                                                             username=carrier_vngs_local['username'],
                                                             password=carrier_vngs_local['password'],
                                                             company_id=carrier_vngs_local['company_id'],
                                                             extra_logging=log_http_detail)

# Create FBN VNGS Connection
carrier_fbn_vngs_local['connection'] = api_client.IPMSConnection(ipms_interface=ipms_interface,
                                                                 username=carrier_fbn_vngs_local['username'],
                                                                 password=carrier_fbn_vngs_local['password'],
                                                                 company_id=carrier_fbn_vngs_local['company_id'],
                                                                 extra_logging=log_http_detail)

# Create Dummy Connection
carrier_dummy_local['connection'] = api_client.IPMSConnection(ipms_interface=ipms_interface,
                                                                 username=carrier_dummy_local['username'],
                                                                 password=carrier_dummy_local['password'],
                                                                 company_id=carrier_dummy_local['company_id'],
                                                                 extra_logging=log_http_detail)

# Get list of Carriers and Service providers. This is used to output readable names of Carriers and Service Providers when logging our progress
carrier_list = carrier_vngs_local['connection'].carriers
service_provider_list = carrier_vngs_local['connection'].service_providers

number_range_to_port = '0958208'

# How many test loops to run
loop_count = 100000 #100,000 ports = ~approx 19 Hours

test_start_time = datetime.datetime.now()
success_count = 0
fail_count = 0

for i in range(loop_count):
    print('---')
    print('Running Test Loop, Round {}'.format(i + 1))

    # Get a random number from the number range
    number_to_port = number_range_to_port + str(randint(0, 999)).rjust(3, "0")
    print('Number to be ported: ' + number_to_port)

    try:
        # Get Current Carrier Information
        number_info = carrier_vngs_local['connection'].number_enquiry(number_to_port)
        current_carrier_id = number_info['carrierId']
        current_service_provider_id = number_info['serviceProviderId']
        if (current_carrier_id is not None):
            print("Number {} is currently ported to Carrier '{}'".format(number_to_port, carrier_list[current_carrier_id]['name']))
            if (current_service_provider_id is not None):
                print('  - Service Provider {}'.format(service_provider_list[current_service_provider_id]['name']))
        else:
            print("Number {} is not currently ported.".format(number_to_port))

        # Figure out who to port the number from and to
        if current_carrier_id is None or current_carrier_id == carrier_vngs_local['carrier_id']:
            gaining_carrier = carrier_fbn_vngs_local
            losing_carrier = carrier_vngs_local
        elif current_carrier_id == carrier_fbn_vngs_local['carrier_id']:
            gaining_carrier = carrier_vngs_local
            losing_carrier = carrier_fbn_vngs_local
        else:
            raise Exception('Number is not ported to either of the configured Carriers')

        print('Creating New Port Request')
        print('Gaining Carrier ID: {}, Carrier Name: {}'.format(gaining_carrier['carrier_id'], gaining_carrier['connection'].carriers[gaining_carrier['carrier_id']]['name']))
        print('Losing Carrier ID: {}, Carrier Name: {}'.format(losing_carrier['carrier_id'], losing_carrier['connection'].carriers[losing_carrier['carrier_id']]['name']))

        # Request Port
        som = 0
        port_in_progress = False
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
        number_port_data = None
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
                # 'gainingCarriers': number_port_data,
                'version': version
            }
            response = losing_carrier['connection'].accept_approved_port_change_request(params)
            success = response['success']

        # GC Activate Port
        if success:
            response = gaining_carrier['connection'].activate_port({ 'som': som })
            success = response['success']

        # GC Get Port Progress
        number_progress = None
        if success:
            response = gaining_carrier['connection'].get_port_progress({ 'som': som })
            success = response['success']
            if success:
                number_progress = gaining_carrier['connection'].deserialize_zeep_object(response['portProgress'][0]['progress'])

        # GC Update Port Progress
        if success:
            number_progress['gainingCarrierProgress'] = 'Done'
            params = {
                'som': som,
                'portProgress': [number_progress]
            }
            response = gaining_carrier['connection'].update_port_progress(params)


        # LC Get Port Progress
        number_progress = None
        if success:
            response = losing_carrier['connection'].get_port_progress({ 'som': som })
            success = response['success']
            if success:
                number_progress = losing_carrier['connection'].deserialize_zeep_object(response['portProgress'][0]['progress'])

        # LC Update Port Progress
        if success:
            number_progress['losingCarrierProgress'] = 'Done'
            params = {
                'som': som,
                'portProgress': [number_progress]
            }
            response = losing_carrier['connection'].update_port_progress(params)

        # GC Get Port Progress
        number_progress = None
        if success:
            response = gaining_carrier['connection'].get_port_progress({ 'som': som })
            success = response['success']
            if success:
                number_progress = gaining_carrier['connection'].deserialize_zeep_object(response['portProgress'][0]['progress'])

        # GC Update Port Progress
        if success:
            number_progress['testedAndCompleteProgress'] = 'Done'
            params = {
                'som': som,
                'portProgress': [number_progress]
            }
            response = gaining_carrier['connection'].update_port_progress(params)

        # GC Approve Port
        if success:
            response = gaining_carrier['connection'].complete_port({ 'som': som })
            success = response['success']

        # VNGS Local Get NU
        if success:
            params = {
                'carriers': [{'carrierIds': carrier_vngs_local['carrier_id']}],
            }
            response = carrier_vngs_local['connection'].get_network_updates(params)
            success = response['success']

        # VNGS Process NU
        if success:
            if response['networkUpdateList'] is not None:
                confirmations = []
                for port in response['networkUpdateList']:
                    confirmation = {}
                    confirmation['carrierId'] = carrier_vngs_local['carrier_id']
                    confirmation['som'] = port['som']['som']
                    confirmations.append(confirmation)
                params = {
                    'confirmations': confirmations
                }
                response = carrier_vngs_local['connection'].confirm_network_updates(params)
                for response_item in response:
                    success = success and response_item['success']

        # Dummy Get NU
        if success:
            params = {
                'carriers': [{'carrierIds': carrier_dummy_local['carrier_id']}],
                'som': som
            }
            response = carrier_dummy_local['connection'].get_network_updates(params)
            success = response['success']

        # Dummy Process NU
        if success:
            if response['networkUpdateList'] is not None:
                confirmations = []
                for port in response['networkUpdateList']:
                    confirmation = {}
                    confirmation['carrierId'] = carrier_dummy_local['carrier_id']
                    confirmation['som'] = port['som']['som']
                    confirmations.append(confirmation)
                params = {
                    'confirmations': confirmations
                }
                response = carrier_dummy_local['connection'].confirm_network_updates(params)
                for response_item in response:
                    success = success and response_item['success']

    except Exception as e:
        success = False
        print('Exception Encountered: {}, {}'.format(type(e) , str(e)))

    if success:
        success_count += 1
    else:
        fail_count += 1

test_duration = datetime.datetime.now() - test_start_time
print('Test Duration: {}'.format(test_duration))

avg_duration = test_duration / loop_count
print('Avg Port Duration: {}'.format(avg_duration))

print('Successful Ports: {}'.format(success_count))
print('Failed Ports: {}'.format(fail_count))
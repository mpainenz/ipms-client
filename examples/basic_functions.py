from connection import api_client
import datetime

# This file contains some basic examples of function calls to IPMS and how to create a Connection object.

# You will need to supply valid IPMS credentials below in order to make a connection
username = 'VNGS_API_TEST'
password = 'just_an_example'
company_id = '6'
carrier_id = 11987
service_provider_id = 19

log_http_detail = False # Log extra HTTP and SOAP information to console, useful when debugging

# Create an IPMS Connection Object. This is used to Communicate to IPMS through the SOAP API
# When created, it will immediately:     1. Import the WSDL file and output the available types and functions which IPMS provides
#                                        2. Call getCompanies, getCarriers, getServiceProviders, output to console, and save them for later access
ipms_connection = api_client.IPMSConnection(ipms_interface=api_client.IPMS_TEST,
                                            username=username,
                                            password=password,
                                            company_id=company_id,
                                            extra_logging=log_http_detail)

# Example SOM Enquiry
som_info_response = ipms_connection.som_enquiry(123456)
success = som_info_response['success']
if success:
    print(som_info_response)

# Example Get Requested Ports
requested_ports_response = ipms_connection.get_requested_ports({})
success = requested_ports_response['success']
if success:
    print(requested_ports_response['requestedPorts'])
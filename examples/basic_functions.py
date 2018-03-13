from connection import api_client
import datetime


# This file contains some basic examples of function calls to IPMS and how to create a Connection object.

username = 'wxc'
password = ''
company_id = '6'
carrier_id = 11987

# log HTTP and SOAP requests/responses to console
log_http_detail = True

# Create an IPMS Connection Object. This is used to Communicate to IPMS through the SOAP API
# When created, it will immediately:     1. Import the WSDL file and output the available types and functions which IPMS provides
#                                        2. Call getCompanies, getCarriers, getServiceProviders, and save them for later access
ipms_connection = api_client.IPMSConnection(ipms_interface=api_client.IPMS_TRAIN,
                                            username=username,
                                            password=password,
                                            company_id=company_id,
                                            extra_logging=log_http_detail)

# List the available Companies, Carriers, and Service Providers.


# Example SOM Enquiry
# som_info = ipms_connection.som_enquiry(3737849)
# print(som_info['portDetail'])

# Example Get Requested Ports
requested_ports = ipms_connection.get_requested_ports({})
for port in requested_ports:
    print(port)
    # print(port['port']['som']) # Get a specific field like this

# Example Port Request
# number_port = {
#     'accountNumber': '12345678',
#     'additionalCustomerInfo': '',
#     'category': 'Simple',
#     'customerContactName': '',
#     'customerContactNumber': '',
#     'customerExistingServiceAddress': '',
#     'customerName': 'test',
#     'gainingCarrierId': '',
#     'gainingServiceProviderContact': '',
#     'gainingServiceProviderId': 9,
#     'gspInternalReference': '',
#     'losingServiceProviderId': 9,
#     'lspOverride': False,
#
#     'numbers': [
#         {
#             'complete': False,
#             'gainingCarrierId': 6,
#             'handsetReference': '',
#             'losingCarrierId': '',
#             'notRequired': '',
#             'number ': {
#                 'phoneNumber': '091234567'
#             }
#         }
#     ],
#
#     'rfsDateTimeStart': datetime.datetime.now(),
#     'prePayPrePaid': False,
#     'som': 0
# }
# ipms_connection.request_port(number_port)
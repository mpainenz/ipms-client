# import urllib, ssl
# from urllib import request
# import xml.etree.ElementTree as ET

import datetime
import logging.config
from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep.transports import Transport

import zeep

IPMS_LIVE = "LIVE"
IPMS_TEST = "TEST"
IPMS_TRAIN = "TRAIN"


class IPMSConnection:

    def __init__(self, ipms_interface, username, password, company_id, extra_logging=False):
        assert ipms_interface in [IPMS_LIVE, IPMS_TEST, IPMS_TRAIN]
        self.ipms_interface = ipms_interface
        print("IPMS API Connecting to {} IPMS Interface".format(self.ipms_interface))

        session = Session()
        session.auth = HTTPBasicAuth('{}${}'.format(username, company_id), password)
        self.service_order_003 = zeep.Client('https://ipms-{}.tcf.org.nz/apiv2/services/service-order-003?wsdl'.format(self.ipms_interface), transport=Transport(session=session))

        # Output a list of the available Functions from the imported WSDL
        self.service_order_003.wsdl.dump()

        # Load and output all Companies by Name and ID
        self.companies = self.get_companies()
        for company_id, company_detail in self.companies.items():
            print('  {} ({})'.format(company_detail.name, company_id))
        print('')

        # Load and output all Carriers by Name and ID
        self.carriers = self.get_carriers()
        for carrier_id, carrier_detail in self.carriers.items():
            print('  {} ({})'.format(carrier_detail.name, carrier_id))
        print('')

        # Load and output all Service Providers by Name and ID
        self.service_providers = self.get_service_providers()
        for service_provider_id, service_provider_detail in self.service_providers.items():
            print('  {} ({})'.format(service_provider_detail.name, service_provider_id))
        print('')

        # If this is enabled, output HTTP SOAP calls and responses to the Console
        if extra_logging:
            logging.config.dictConfig({
                'version': 1,
                'formatters': {
                    'verbose': {
                        'format': '%(name)s: %(message)s'
                    }
                },
                'handlers': {
                    'console': {
                        'level': 'DEBUG',
                        'class': 'logging.StreamHandler',
                        'formatter': 'verbose',
                    },
                },
                'loggers': {
                    'zeep.transports': {
                        'level': 'DEBUG',
                        'propagate': True,
                        'handlers': ['console'],
                    },
                }
            })

        print("Finished Loading IPMS Objects".format(self.ipms_interface))

    def check_response(self, response):
        success = (response is not None) and (response['success'] is not None)
        if success:
            success = response['success']
            if not success:
                for error in response['errors']:
                    print('IPMS Error - {} ({}): {}'.format(error['error']['mnemonic'], error['error']['code'], error['error']['description']))
                    print('   - Name: {}, Value: {}'.format(error['name'], error['value']))
                    print()
        else:
            raise Exception('Invalid or Empty HTTP Response')
        return success

    # IPMS Function Wrappers
    def get_companies(self):
        print("Get Companies")
        response = self.service_order_003.service.getCompanies()
        if self.check_response(response):
            company_dict = {}
            company_list = response['companies']
            for company in company_list:
                company_dict[company['id']] = company
            return company_dict

    def get_carriers(self):
        print("Get Carriers")
        response = self.service_order_003.service.getCarriers()
        if self.check_response(response):
            carrier_dict = {}
            carrier_list = response['carriers']
            for carrier in carrier_list:
                carrier_dict[carrier['id']] = carrier
            return carrier_dict

    def get_service_providers(self):
        print("Get Service Providers")
        response = self.service_order_003.service.getServiceProviders()
        if self.check_response(response):
            service_provider_dict = {}
            carrier_list = response['serviceProviders']
            for carrier in carrier_list:
                service_provider_dict[carrier['id']] = carrier
            return service_provider_dict

    def number_enquiry(self, number):
        print("Number Enquiry: " + number)
        response = self.service_order_003.service.numberEnquiry(number)
        if self.check_response(response):
            return response

    def som_enquiry(self, som):
        print("SOM Enquiry: " + str(som))
        response = self.service_order_003.service.sOMEnquiry(som)
        if self.check_response(response):
            return response

    def get_requested_ports(self, params=None):
        print("Get Requested Ports")

        # Default Params will return all Requested Ports
        default_params = {
            'detail': True,
            'statusList': [{ 'status': 'Awaiting LSP Response'},
                   { 'status': 'Awaiting GSP Approval'},
                   { 'status': 'Approved'},
                   { 'status': 'Rejected'},
                   { 'status': 'Cancelled'},
                   { 'status': 'Request Expired'}],
            'filter': 'All',
            'som': 0,
            'serverDateTime': None,
            'rfsToDate': datetime.datetime.now() + datetime.timedelta(days=14),
            'overdueOnly': False,
            'gainingCarrierId': 0,
            'losingCarrierId': 0
        }

        if params is not None:
            for param_name, param_value in params.items():
                default_params[param_name] = param_value

        response = self.service_order_003.service.getRequestedPorts(default_params['detail'],
                                                                    default_params['statusList'],
                                                                    default_params['filter'],
                                                                    default_params['som'],
                                                                    default_params['serverDateTime'],
                                                                    default_params['rfsToDate'],
                                                                    default_params['overdueOnly'],
                                                                    default_params['gainingCarrierId'],
                                                                    default_params['losingCarrierId'])

        if self.check_response(response):
            return response['requestedPorts']

    def request_port(self, params=None):
        print("Port Request")

        default_params = {
            'accountNumber': '',
            'additionalCustomerInfo': '',
            'category': 'Simple',
            'customerContactName': '',
            'customerContactNumber': '',
            'customerExistingServiceAddress': '',
            'customerName': '',
            'gainingCarrierId': '',
            'gainingServiceProviderContact': '',
            'gainingServiceProviderId': 0,
            'gspInternalReference': '',
            'losingServiceProviderId': 0,
            'lspOverride': False,
            'numbers': [],
            'rfsDateTimeStart': datetime.datetime.now(),
            'prePayPrePaid': False,
            'som': 0
        }

        if params is not None:
            for param_name, param_value in params.items():

                if param_name == 'numbers':
                    for number in param_value:

                        default_number_params = {
                            'complete': False,
                            'gainingCarrierId': 0,
                            'handsetReference': '',
                            'losingCarrierId': '',
                            'notRequired': '',
                            'phoneNumber ': {
                                'phoneNumber': ''
                            }
                        }

                        for number_param, number_param_value in number.items():
                            default_number_params[number_param] = number_param_value

                        default_params['numbers'] = default_number_params

                else:
                    default_params[param_name] = param_value

        response = self.service_order_003.service.requestPort(default_params)
        if self.check_response(response):
            return response
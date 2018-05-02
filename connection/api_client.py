# import urllib, ssl
# from urllib import request
# import xml.etree.ElementTree as ET

import datetime, calendar, copy, json
import logging.config
from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep.transports import Transport
from zeep import helpers

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

        # session.verify = False #Uncomment this to disable SSL Certificate verification

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
        success = (response is not None)
        if success:

            if type(response) == list:
                for item in response:
                   success = success and self.evaluate_response(item)

            else:
                success = self.evaluate_response(response)

        else:
            raise Exception('Invalid or Empty HTTP Response')
        return success

    def evaluate_response(self, response):
        success = response['success']
        if not success:
            for error in response['errors']:
                print('IPMS Error - {} ({}): {}'.format(error['error']['mnemonic'], error['error']['code'], error['error']['description']))
                print('   - Name: {}, Value: {}'.format(error['name'], error['value']))
                print()
        return success

    def deserialize_zeep_object(self, obj):
        input_dict = helpers.serialize_object(obj)
        return json.loads(json.dumps(input_dict))

    # General Functions (Used to simplify Python related code)
    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)

    # This function is used to copy params that a user provides, and apply them against the default_params which are used if the user does not specify a particular param.
    def recursive_update(self, target, src):

        for k, v in src.items():

            # Any time a list is encountered, each item needs to be merged against the default_parameters.
            # Once complete, the list in the target (the defaults) will be overwritten with the merged list
            if type(v) == list:
                merged_list = []
                for li in v:
                    merged_list_item = copy.deepcopy(target[k][0]) # Always copies against the first item in the default's list
                    self.recursive_update(merged_list_item, li)
                    merged_list.append(merged_list_item)

                # Overwrite the list object
                target[k] = merged_list

            elif type(v) == dict:
                if not k in target:
                    target[k] = copy.deepcopy(v)
                else:
                    self.recursive_update(target[k], v)
            else:
                target[k] = copy.copy(v)

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
        self.check_response(response)
        return response

    def som_enquiry(self, som):
        print("SOM Enquiry: " + str(som))
        response = self.service_order_003.service.sOMEnquiry(som)
        self.check_response(response)
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
        self.recursive_update(default_params, params)

        response = self.service_order_003.service.getRequestedPorts(default_params['detail'],
                                                                    default_params['statusList'],
                                                                    default_params['filter'],
                                                                    default_params['som'],
                                                                    default_params['serverDateTime'],
                                                                    default_params['rfsToDate'],
                                                                    default_params['overdueOnly'],
                                                                    default_params['gainingCarrierId'],
                                                                    default_params['losingCarrierId'])

        self.check_response(response)
        return response



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
            'numbers': [{
                        'complete': False,
                        'gainingCarrierId': 0,
                        'handsetReference': '',
                        'losingCarrierId': '',
                        'notRequired': '',
                        'phoneNumber': {
                            'phoneNumber': ''
                        }
                    }],
            'rfsDateTimeStart': datetime.datetime.now(),
            'prePayPrePaid': False,
            'som': 0
        }
        self.recursive_update(default_params, params)

        response = self.service_order_003.service.requestPort(default_params)
        self.check_response(response)
        return response


    def submit_port_response(self, params=None):
        print("Submit Port Response")

        default_params = {
            'accountNumber': '',
            'accountNumberIncorrect': False,
            'category': 'Simple',
            'customerName': '',
            'losingServiceProviderIncorrect': False,
            'lspInternalReference': '',
            'lspOverride': False,
            'numbers': [{
                            'complete': False,
                            'gainingCarrierId': 0,
                            'handsetReference': '',
                            'losingCarrierId': 0,
                            'notRequired': False,
                            'phoneNumber': {
                                'phoneNumber': ''
                            }
                        }],
            'prePayPrePaid': False,
            'som': 0
        }
        self.recursive_update(default_params, params)

        response = self.service_order_003.service.submitPortResponse(default_params)
        self.check_response(response)
        return response

    def approve_port(self, params=None):
        print("Approve Port")

        default_params = {
            'accountNumber': '',
            'accountNumberIncorrect': False,
            'category': 'Simple',
            'customerName': '',
            'losingServiceProviderIncorrect': False,
            'lspInternalReference': '',
            'lspOverride': False,
            'numbers': [{
                            'complete': False,
                            'gainingCarrierId': 0,
                            'handsetReference': '',
                            'losingCarrierId': 0,
                            'notRequired': False,
                            'phoneNumber': {
                                'phoneNumber': ''
                            }
                        }],
            'prePayPrePaid': False,
            'som': 0
        }
        self.recursive_update(default_params, params)

        response = self.service_order_003.service.approvePort(default_params)
        self.check_response(response)
        return response


    def request_approved_port_change(self, params=None):
        print("Request Approved Port Change")

        default_params = {
            'lspOverride': False,
            'numbers': [{
                            'complete': False,
                            'gainingCarrierId': 0,
                            'handsetReference': '',
                            'losingCarrierId': 0,
                            'notRequired': False,
                            'phoneNumber': {
                                'phoneNumber': ''
                            }
                        }],
            'rfsDateTimeStart': datetime.datetime.now(),
            'som': 0
        }
        self.recursive_update(default_params, params)

        response = self.service_order_003.service.requestApprovedPortChange(default_params)
        self.check_response(response)
        return response

    def get_approved_port_change_requests(self, params=None):
        print("Get Approved Port Change Requests")

        default_params = {
            'som': 0,
            'statusList': [
                {
                    'status': 'Awaiting APC Approval'
                }
            ],
            'filter': 'My SP Action',
            'rfsToDate': self.add_months(datetime.datetime.now(), 3),
            'overdueOnly': False
        }
        self.recursive_update(default_params, params)

        response = self.service_order_003.service.getApprovedPortChangeRequests(default_params['som'],
                                                                    default_params['statusList'],
                                                                    default_params['filter'],
                                                                    default_params['rfsToDate'],
                                                                    default_params['overdueOnly'])

        self.check_response(response)
        return response

    def accept_approved_port_change_request(self, params=None):
        print("Accept Approved Port Change Request")

        default_params = {
            'som': 0,
            # 'gainingCarriers': [{ # Data is only passed if a change is required. This may require further testing and work to get working. If required, contact me (Mark Paine) for more info
            #                 'complete': False,
            #                 'gainingCarrierId': 0,
            #                 'handsetReference': '',
            #                 'losingCarrierId': 0,
            #                 'notRequired': False,
            #                 'phoneNumber': {
            #                     'phoneNumber': ''
            #                 }
            #             }],
            'version': 0
        }

        self.recursive_update(default_params, params)

        gainingCarriers = None
        if 'gainingCarriers' in default_params:
            gainingCarriers = default_params['gainingCarriers']

        response = self.service_order_003.service.acceptApprovedPortChange(default_params['som'], gainingCarriers, default_params['version'])
        self.check_response(response)
        return response

    def activate_port(self, params):
        print("Activate Port")
        response = self.service_order_003.service.activatePort(params['som'])
        self.check_response(response)
        return response


    def get_port_progress(self, params):
        print("Get Port Progress")
        response = self.service_order_003.service.getPortProgress(params['som'])
        self.check_response(response)
        return response

    def update_port_progress(self, params):
        print("Update Port Progress")

        default_params = {
            'som': 0,
            'portProgress': [
                {
                    'gainingCarrierProgress': 'Not Done',
                    'losingCarrierProgress': 'Not Done',
                    'number': {
                        'phoneNumber': ''
                    },
                    'testedAndCompleteProgress': 'Not Done',
                    'version': 0
                }
            ]
        }
        self.recursive_update(default_params, params)

        response = self.service_order_003.service.updatePortProgress(default_params['som'], default_params['portProgress'])
        self.check_response(response)
        return response

    def complete_port(self, params):
        print("Complete Port")
        response = self.service_order_003.service.completePort(params['som'])
        self.check_response(response)
        return response

    def get_network_updates(self, params):
        print("Get Network Updates")

        # Default Params will return all Network Updates
        default_params = {
            'carriers': [{'carrierIds': 0}],
            'som': 0,
            'somType': ''
        }
        self.recursive_update(default_params, params)

        response = self.service_order_003.service.getNetworkUpdates(default_params['carriers'], default_params['som'], default_params['somType'])
        self.check_response(response)
        return response

    def confirm_network_updates(self, params):
        print("Confirm Network Updates")

        default_params = {
            'confirmations': [{
                    'carrierId': 0,
                    'som': 0
            }]
        }
        self.recursive_update(default_params, params)

        response = self.service_order_003.service.confirmNetworkUpdates(default_params['confirmations'])
        self.check_response(response)
        return response
# IPMS Client

The [Industry Portability Management System](https://www.tcf.org.nz/industry/numbering/number-portability/access-to-ipms/) is a government regulated service provided to New Zealand Carriers and Service provider Companies in order to Port telephone numbers between members. Number Portability allows New Zealand consumbers to keep ownership of their Telephone numbers when changing Service Providers.

This project contains a very simple, easy to use, IPMS API Client written in Python 3.6. This project will enable an IPMS user to connect to, and perform function calls against the IPMS SOAP Service.

This library supports TLS1.2 SSL.

# Requirements

  - [Python 3.6](https://www.python.org/downloads/release/python-360/)
  - [Zeep](http://docs.python-zeep.org/en/master/) (A Python SOAP client library)


# Available IPMS Functions

Some function calls have not yet been implemented, however because the framework is built, it is not difficult to add any missing functions. If missing functions are needed, please create an issue to request missing functionality be added.

| Function Call  | Implentation Status |
| ------------- | ------------- |
| acceptApprovedPortChange | :black_large_square: Implemented |
| activatePort | :black_large_square: Implemented |
| approvePort | :black_large_square: Implemented |
| cancelPort | :white_large_square: TBC |
| changePassword | :white_large_square: TBC |
| completePort | :black_large_square: Implemented |
| confirmNetworkUpdates | :black_large_square: Implemented |
| failPort | :white_large_square: TBC |
| getApprovedPortChangeRequests | :black_large_square: Implemented |
| getApprovedPorts | :black_large_square: Implemented |
| getCarriers | :black_large_square: Implemented |
| getCompanies | :black_large_square: Implemented |
| getCurrentUserData | :white_large_square: TBC |
| getNetworkUpdates | :black_large_square: Implemented |
| getPortProgress | :black_large_square: Implemented |
| getRequestedPorts | :black_large_square: Implemented |
| getServiceProviders | :black_large_square: Implemented |
| numberEnquiry | :black_large_square: Implemented |
| rejectApprovedPortChange | :white_large_square: TBC |
| rejectPort | :white_large_square: TBC |
| requestApprovedPortChange | :black_large_square: Implemented |
| requestEmergencyReturn | :white_large_square: TBC |
| requestPort | :black_large_square: Implemented |
| requestRelinquishment | :white_large_square: TBC |
| sOMEnquiry | :white_large_square: TBC |
| sOMStatusEnquiry | :white_large_square: TBC |
| submitPortResponse | :black_large_square: Implemented |
| updatePortProgress | :black_large_square: Implemented |
| version | :white_large_square: TBC |
| withdrawPort | :white_large_square: TBC |


# Installation

  - Install [Python 3.6](https://www.python.org/downloads/release/python-360/) or later
  - Clone this library using a Git client, such as [TortoiseGit](https://tortoisegit.org/) for Windows (Or simply download using the green link above)
  - You can then either use Python from command line to execute the example.py script, or I would recommend using an IDE like PyCharm which is a lot more user-friendly


# Usage

For a basic example, look at the [basic_functions.py](basic_functions.py) script.

Simply change the Username, Password, and Carrier ID fields to something valid, and run the script to connect to IPMS

# Example code

In order to make things simple for those who aren't familiar with Programming, most of the more complicated code is wrapped inside a class called TNASConnection. You use this class to connect and run commands against IPMS.

```sh
ipms_connection = api_client.IPMSConnection(ipms_interface=api_client.IPMS_TRAIN,
                                            username='joebloggs',
                                            password='something',
                                            company_id=123)

som_info_response = ipms_connection.som_enquiry(123456)
success = som_info_response['success']
if success:
    print(som_info_response)
```

For more rigourous examples, take a look at [vngs_test_loop.py](vngs_test_loop.py)

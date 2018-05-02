# IPMS Client

The [Industry Portability Management System](https://www.tcf.org.nz/industry/numbering/number-portability/access-to-ipms/) is a regulated government service provided to New Zealand Carriers and Service provider Companies in order to Port telephone numbers between member. Number Portability allows New Zealand consumbers to keep ownership of their Telephone numbers when swapping Service Providers.

This project contains a very simple, easy to use, IPMS API Client written in Python 3.6. This project will enable an IPMS user to connect to, and perform tasks against the IPMS SOAP Service.

This library supports TLS1.2 SSL.


# Example code

In order to make things simple for those who aren't familiar with Programming, most of the more complicated code is wrapped inside a class called TNASConnection. You use this class to connect and run commands against IPMS.

```sh
ipms_connection = api_client.IPMSConnection(ipms_interface=api_client.IPMS_TRAIN,
                                            username='joebloggs',
                                            password='something',
                                            company_id=123)
```

# Requirements

  - [Python 3.6](https://www.python.org/downloads/release/python-360/)
  - [Zeep](http://docs.python-zeep.org/en/master/) (A Python SOAP client library)


# Available Functions

| Function Call  | Implentation Status |
| ------------- | ------------- |
| acceptApprovedPortChange | :white_check_mark: Implemented |
| activatePort | :white_check_mark: Implemented |
| approvePort | :white_check_mark: Implemented |
| cancelPort | :white_large_square: TBC |
| changePassword | :white_large_square: TBC |
| completePort | :white_check_mark: Implemented |
| confirmNetworkUpdates | :white_check_mark: Implemented |
| failPort | :white_large_square: TBC |
| getApprovedPortChangeRequests | :white_check_mark: Implemented |
| getApprovedPorts | :white_check_mark: Implemented |
| getCarriers | :white_check_mark: Implemented |
| getCompanies | :white_check_mark: Implemented |
| getCurrentUserData | :white_large_square: TBC |
| getNetworkUpdates | :white_check_mark: Implemented |
| getPortProgress | :white_check_mark: Implemented |
| getRequestedPorts | :white_check_mark: Implemented |
| getServiceProviders | :white_check_mark: Implemented |
| numberEnquiry | :white_check_mark: Implemented |
| rejectApprovedPortChange | :white_large_square: TBC |
| rejectPort | :white_large_square: TBC |
| requestApprovedPortChange | :white_check_mark: Implemented |
| requestEmergencyReturn | :white_large_square: TBC |
| requestPort | :white_check_mark: Implemented |
| requestRelinquishment | :white_large_square: TBC |
| sOMEnquiry | :white_large_square: TBC |
| sOMStatusEnquiry | :white_large_square: TBC |
| submitPortResponse | :white_check_mark: Implemented |
| updatePortProgress | :white_check_mark: Implemented |
| version | :white_large_square: TBC |
| withdrawPort | :white_large_square: TBC |


# Installation

  - Install [Python 3.6](https://www.python.org/downloads/release/python-360/) or later
  - Clone this library using a Git client, such as [TortoiseGit](https://tortoisegit.org/) for Windows (Or simply download using the green link above)
  - You can then either use Python from command line to execute the example.py script, or I would recommend using an IDE like PyCharm which is a lot more user-friendly


# Usage

For a basic example, look at the [example.py](example.py) script.

Simply change the Username, Password, and Carrier ID fields to something valid, and run the script to connect to IPMS


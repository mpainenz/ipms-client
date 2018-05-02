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
| acceptApprovedPortChange | :white_check_mark: Supported |
| activatePort | :white_check_mark: Supported |
| approvePort | :white_check_mark: Supported |
| cancelPort | :x: Not Supported |
| changePassword | :x: Not Supported |
| completePort | :white_check_mark: Supported |
| confirmNetworkUpdates | :white_check_mark: Supported |
| failPort | :x: Not Supported |
| getApprovedPortChangeRequests | :white_check_mark: Supported |
| getApprovedPorts | :white_check_mark: Supported |
| getCarriers | :white_check_mark: Supported |
| getCompanies | :white_check_mark: Supported |
| getCurrentUserData | :x: Not Supported |
| getNetworkUpdates | :white_check_mark: Supported |
| getPortProgress | :white_check_mark: Supported |
| getRequestedPorts | :white_check_mark: Supported |
| getServiceProviders | :white_check_mark: Supported |
| numberEnquiry | :white_check_mark: Supported |
| rejectApprovedPortChange | :x: Not Supported |
| rejectPort | :x: Not Supported |
| requestApprovedPortChange | :white_check_mark: Supported |
| requestEmergencyReturn | :x: Not Supported |
| requestPort | :white_check_mark: Supported |
| requestRelinquishment | :x: Not Supported |
| sOMEnquiry | :x: Not Supported |
| sOMStatusEnquiry | :x: Not Supported |
| submitPortResponse | :white_check_mark: Supported |
| updatePortProgress | :white_check_mark: Supported |
| version | :x: Not Supported |
| withdrawPort | :x: Not Supported |


# Installation

  - Install [Python 3.6](https://www.python.org/downloads/release/python-360/) or later
  - Clone this library using a Git client, such as [TortoiseGit](https://tortoisegit.org/) for Windows (Or simply download using the green link above)
  - You can then either use Python from command line to execute the example.py script, or I would recommend using an IDE like PyCharm which is a lot more user-friendly


# Usage

For a basic example, look at the [example.py](example.py) script.

Simply change the Username, Password, and Carrier ID fields to something valid, and run the script to connect to IPMS


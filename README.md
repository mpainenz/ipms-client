# IPMS Client

([Industry Portability Management System](https://www.tcf.org.nz/industry/numbering/number-portability/access-to-ipms/)) is a government regulated service provided to New Zealand for use by Carriers and Service providers in order to Port telephone numbers between member Companys.

This project contains a very simple, easy to use, IPMS API Client written in Python 3.6.

This library supports TLS1.2 SSL.


# Example code

In order to make things simple for those who aren't familiar with Programming, most of the more complicated code is wrapped inside a class called TNASConnection. You use this class to connect and run commands against TNAS. This means connecting to TNAS can be done in only three lines of code.

```sh
ipms_connection = api_client.IPMSConnection(ipms_interface=api_client.IPMS_TRAIN,
                                            username='joebloggs',
                                            password='something',
                                            company_id=123)
```


# Installation

  - Install [Python 3.6](https://www.python.org/downloads/release/python-360/) or later
  - Clone this library using a Git client, such as [TortoiseGit](https://tortoisegit.org/) for Windows (Or simply download using the green link above)
  - You can then either use Python from command line to execute the example.py script, or I would recommend using an IDE like PyCharm which is a lot more user-friendly


# Usage

For a basic example, look at the [example.py](example.py) script.

Simply change the Username, Password, and Carrier ID fields to something valid, and run the script to connect to TNAS


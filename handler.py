from datetime import datetime
from urllib.request import ssl, socket
import os
import sys


EXPIRATION_THRESHOLD_DAYS = 14

"""
This function checks whether the certificates of the target domains
are 14 days or less from the expiration.
"""
def main(event, context):
    exit_with_error = False
    domains = os.environ.get("DOMAINS").split(sep=",")
    context = ssl.create_default_context()

    for domain in domains:
        with socket.create_connection((domain, '443')) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssl_sock:
                cert_data = ssl_sock.getpeercert()

        exp = datetime.strptime(cert_data['notAfter'], '%b %d %H:%M:%S %Y GMT')
        delta = exp - datetime.utcnow()

        print (f'domain [{domain}] still [{delta.days}] days left before expiration')
        if delta.days <= EXPIRATION_THRESHOLD_DAYS:
            print (f'domain [{domain}] must be renewed')
            exit_with_error = True

    if exit_with_error:
        sys.exit(-1)
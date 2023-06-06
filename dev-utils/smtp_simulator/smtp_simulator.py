#!/usr/bin/env python3

import smtpd
import os
import datetime
import asyncore
import platform
import sys


class MailServerSimulator(smtpd.SMTPServer):
    """Descendant class of smtpd.SMTPServer

    This class implements our own SMTPServer class with own process_message() method.

    """
    def __init__(self, bind_addr, port):
        """Call the ancestor's __init__ method

        Parameters
        ----------
        localaddr : tuple
            Local address and port in a tupel format
        remoteaddr : tuple
            Remote address and port in a tupel format or None
        decode_data : bool
            decode_data specifies whether the data portion of the SMTP transaction should be decoded using UTF-8.

        """
        smtpd.SMTPServer.__init__(self, (bind_addr, port), None, decode_data=True)
        print('Mail server simulator listening on {} port {}. To stop, press Ctrl+C'.format(bind_addr, port))

    def process_message(self, peer, mailfrom, rcpttos, data):
        """Overloaded process_mesage() method

        Parameters
        ----------
        peer : tuple
            peer is a tuple containing (ipaddr, port) of the client that made the socket connection to our smtp port.
        mailfrom : str
            mailfrom is the raw address the client claims the message is coming from.
        rcpttos : str
            rcpttos is a list of raw addresses the client wishes to deliver the message to.
        data : str
            data is a string containing the contents of the e-mail (which should be in RFC 5321 format).

        """

        is_Windows = False
        # Determine operating sytem type
        os_type = platform.system()
        # Determine the current folder path
        current_folder = os.getcwd()

        if os_type == "Windows":
            is_Windows = True

        # Set path of 'mailboxes' folder
        if is_Windows:
            base_path_of_mailboxes = current_folder + '\\mailboxes'
        else:
            base_path_of_mailboxes = current_folder + '/mailboxes'

        # Write from and to of a mail to the console
        print('Mail from: %s to: %s' % (mailfrom, repr(rcpttos)))

        # Work on all recipients
        for rcpt in rcpttos:
            # Get recipient name from recipint address
            rcpt = rcpt.split('@')[0]
            try:
                # Create path of recipient's mailbox
                if is_Windows:
                    rcpt_mailbox = base_path_of_mailboxes + '\\' + rcpt
                else:
                    rcpt_mailbox = base_path_of_mailboxes + '/' + rcpt
                # Create recipient mailbox foder if doesn't exists
                if not os.path.exists(rcpt_mailbox):
                    os.makedirs(rcpt_mailbox)
            except (OSError, e):
                print("Hiba: " + e.strerror)
                pass

            # Write mail to file
            if is_Windows:
                mail_file = open(
                    base_path_of_mailboxes + '\\' + rcpt + '\\' + mailfrom +
                    datetime.datetime.now().strftime('%Y%m%d%H%M%S-%f'), 'w')
            else:
                mail_file = open(
                    base_path_of_mailboxes + '/' + rcpt + '/' + mailfrom +
                    datetime.datetime.now().strftime('%Y%m%d%H%M%S-%f'), 'w')
            mail_file.write(data)
            mail_file.close()


def loop(bind_addr, port):
    """Use asynchronous socket service to run the simulator

    """

    smtp_simulator = MailServerSimulator(bind_addr, port)

    try:
        asyncore.loop(timeout=2)
    except KeyboardInterrupt:
        print('\nMail server simulator has interrupted')
        smtp_simulator.close()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
        bind_addr = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        loop(bind_addr, port)
    else:
        loop('localhost', 1025)

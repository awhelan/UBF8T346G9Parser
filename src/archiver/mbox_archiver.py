import logging
import pathlib
import shutil
from datetime import datetime
from typing import Dict

from src.helpers import helpers #type: ignore
from src.logger import config_logger #type: ignore

import locale
try:
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')
except:
    pass

class MboxMailArchiver(config_logger.Logger):
    """Archive email
    """

    def __init__(self) -> None:
        self.mailsdir = 'MailArchive/Mails'
        self.attachmentsdir = 'MailArchive/Attachments/'
        self.save_paths = {}

    def archive_mail(self, mail: Dict, message: bytes) -> None:
        mbox_path = self.mailsdir + '/inbox.mbox'
        self._write_styled_mail(mail, mbox_path, message)

    def archive_attachment(self, attachment_content: bytes, attachment_name: str) -> None:
        pathlib.Path(self.attachmentsdir).mkdir(parents=True, exist_ok=True)
        if attachment_content != b'':
            try:
                with open(self.attachmentsdir + attachment_name, 'wb') as attachment_file:
                    attachment_file.write(attachment_content)
            except FileNotFoundError:
                """ Log and Ignore if file isn't found..."""
                logging.warning(f'File {attachment_name} not found.')
            except NotADirectoryError:
                logging.warning(f'Not a directory')

    def _write_styled_mail(self, mail: Dict, mbox_file_path: str, message: bytes):

        with helpers.Helper.open_file(mbox_file_path) as f:
            f.write('<head>\n<link rel="stylesheet" href="../../../../static/css/custom.css">\n</head>\n')
            self._write_meta_data(mail, f)
            f.write('\n<div class="bordermail">\n')
            f.write(message.decode('utf-16-le','ignore'))
            f.write('\n</div>\n')

    def _parse_email_address(self, address: Dict) -> str:
        if address is None:
            return ''
        return f"{address.get('email')} {address.get('name')}"

    def _write_meta_data(self, mail: Dict, mail_file):
        sender = mail.get('sender')
        sender_text = self._parse_email_address(sender)
        recipients = mail.get('recipients')
        recipients_text = []
        for recipient in recipients:
            recipients_text.append(self._parse_email_address(recipient))
        time = datetime.fromtimestamp(mail.get('time'))
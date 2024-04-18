import pathlib
import shutil
from datetime import datetime
from typing import Dict

from src.helpers import helpers #type: ignore
from src.logger import config_logger #type: ignore

import locale
try:
    locale.setlocale(locale.LC_ALL, 'da_DK.utf8')
except:
    pass

class MailArchiver(config_logger.Logger):
    """Archive email
    """

    def __init__(self) -> None:
        self.mailsdir = 'MailArchive/Mails'
        self.attachmentsdir = 'MailArchive/Attachments/'
        self._check_mailsdir(self.mailsdir)
        self.mails_info = {}

    def archive_mail(self, mail: Dict, message: bytes) -> None:
        mail_times = self._get_date(mail)
        mail_path = self._get_mail_path(mail, mail_times)
        self._update_mails_info(mail, mail_times)
        self._style_mails(mail, mail_path, message)

    def archive_attachment(self, attachment_content: bytes, attachment_name: str) -> None:
        pathlib.Path(self.attachmentsdir).mkdir(parents=True, exist_ok=True)
        if attachment_content != b'':
            with open(self.attachmentsdir + attachment_name, 'wb') as attachment_file:
                attachment_file.write(attachment_content)

    def _update_mails_info(self, mail, mail_times):
        year = mail_times.get('year')
        month = mail_times.get('month')
        day = mail_times.get('day')
        mailid = mail.get('id')

        mail_info = {
            'path': 'Mails/{year}/{month}/{day}/{mailid}.html'.format(
                year=year,
                month=month,
                day=day,
                mailid=mailid
            ),
            'subject': mail.get('subject'),
            'id': mailid
        }

        if not self.mails_info.get(year):
            self.mails_info[year] = {}

        if not self.mails_info[year].get(month):
            self.mails_info[year][month] = {}

        if not self.mails_info[year][month].get(day):
            self.mails_info[year][month][day] = [mail_info]
        elif mail_info not in self.mails_info[year][month][day]:
            self.mails_info[year][month][day].append(mail_info)


    def _style_mails(self, mail: Dict, mail_path: str, message: bytes):

        with helpers.Helper.open_file(mail_path) as f:
            f.write('<head>\n<link rel="stylesheet" href="../../../../static/css/custom.css">\n</head>\n')
            self._write_meta_data(mail, f)
            f.write('\n<div class="bordermail">\n')
            f.write(message.decode('utf-16-le','ignore'))
            f.write('\n</div>\n')

    def _write_meta_data(self, mail: Dict, mail_file):
        meta_data = '''\n<div class="bordermeta">\n<p>\nSubject: <b>{subject}</b>\n</p>\n<p>\nFrom: {sender}\n</p>\n<p>\nTo: {recipients}\n</p>\n<p>\nCC: {cc}\n</p>\n<p>\nDate: {date}\n</p>\n</div>\n'''
        sendertext = self._get_sender(mail)
        recipientstext = self._get_recipients(mail)
        timetext = self._get_time(mail)

        meta_data = meta_data.format(
            subject=mail.get('subject'),
            sender=sendertext,
            recipients=' | '.join(recipientstext),
            cc=mail.get('cc'),
            date=timetext
        )

        mail_file.write(meta_data)

    def _get_time(self, mail):
        time = self._get_date(mail)
        timetext = '{hours}:{minutes}:{seconds} {day}/{month}/{year}'.format(
            year=time.get('year'),
            month=time.get('month'),
            day=time.get('day'),
            hours=time.get('hours'),
            minutes=time.get('minutes'),
            seconds=time.get('seconds'),
        )
        return timetext

    def _get_sender(self, mail):
        sender = mail.get('sender')
        sendertext = '<b>{name}</b> - <b>{email}</b>'.format(
            email=sender.get('email'), #type: ignore
            name=sender.get('name') #type: ignore
        )
        return sendertext

    def _get_recipients(self, mail):
        recipients = mail.get('recipients')
        recipientstext = []
        if recipients != [None]:
            for recipient in recipients: #type: ignore
                recipientstext.append('<b>{name}</b> - <b>{email}</b>'.format(
                    email=recipient.get('email'), #type: ignore
                    name=recipient.get('name') #type: ignore
                ))
        return recipientstext

    def _get_date(self, mail: Dict) -> Dict:
        mail_date = datetime.fromtimestamp(mail.get('time'))
        return {
            'year': mail_date.strftime("%Y"),
            'month': mail_date.strftime("%m"),
            'day': mail_date.strftime("%d"),
            'hours': mail_date.strftime("%H"),
            'minutes': mail_date.strftime("%M"),
            'seconds': mail_date.strftime("%S"),
        }

    def _get_mail_path(self, mail: Dict, mail_times: Dict) -> str:
        mail_dir = self._create_mail_dirs(mail_times)
        return '{}/{}.html'.format(mail_dir, mail.get('id'))

    def _create_mail_dirs(self, mail_times: Dict) -> str:
        mail_dir = '{mailsdir}/{year}/{month}/{day}'.format(
            mailsdir=self.mailsdir,
            year=mail_times.get('year'),
            month=mail_times.get('month'),
            day=mail_times.get('day')
        )

        pathlib.Path(mail_dir).mkdir(parents=True, exist_ok=True)
        return mail_dir

    def _check_mailsdir(self, mailsdir: str):
        mails_dir = pathlib.Path(mailsdir)
        if mails_dir.is_dir():
            userinput = input('The Mails directory already exists, do you want '
                              'to start over? [Y/n]: ')

            if 'n' == userinput.lower() or 'no' == userinput.lower():
                self.logger.info('Exiting.')
                exit(0)
            else:
                self.logger.info(f'Removing {mails_dir}')
                shutil.rmtree(mails_dir)


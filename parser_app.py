#!/usr/bin/env python
from src.archiver.html_indexer import HtmlIndexer
from src.backupreader import reader
from src.olk15parser import parser
from src.archiver import html_archiver
from src.helpers import helpers
from src.helpers import progress
from src.logger import config_logger

logger = config_logger.Logger()

if __name__ == "__main__":
    profile_data_location = helpers.Helper.get_location()
    backupreader_app = reader.BackupReader(profile_data_location)
    olk15parser_app = parser.OLK15Parser()
    archiver_app = html_archiver.HtmlMailArchiver()

    for i, mail in enumerate(backupreader_app.get_mails_from_database()):
        mail_path = profile_data_location + mail.get('content_path')
        print(i, mail)
        message = olk15parser_app.get_mail_content(mail_path, mail.get('subject'))

    mails_amount = backupreader_app.get_mails_amount()
    progressbar = progress.ProgressBar(mails_amount)

    mails = backupreader_app.get_mails_from_database()
    logger.logger.info('Getting email content and writing to files')
    for mail in mails:
        progressbar.update()
        mail_path = profile_data_location + mail.get('content_path')
        message = olk15parser_app.get_mail_content(mail_path, mail.get('subject'))
        archiver_app.archive_mail(mail, message)

    progressbar.progress_done()
    logger.logger.info('Done getting emails')

    html_indexer = HtmlIndexer(archiver_app.save_paths)
    html_indexer.write_index()

    attachments_amount = backupreader_app.get_attachments_amount()
    progressbar = progress.ProgressBar(attachments_amount)

    attachments = backupreader_app.get_attachments_from_folder()
    logger.logger.info('Getting attached files')
    for num, attachment in enumerate(attachments):
        progressbar.update()
        attachment_content, attachment_name = olk15parser_app.get_file_content(attachment)
        archiver_app.archive_attachment(attachment_content, '{}_{}'.format(num, attachment_name))

    progressbar.progress_done()

    logger.logger.info('Done getting emails, updating index')

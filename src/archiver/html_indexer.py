from datetime import datetime

from src.logger import config_logger


class HtmlIndexer(config_logger.Logger):

    def __init__(self, save_paths) -> None:
        self.save_paths = save_paths

    def write_index(self) -> None:
        self.logger.info('Updating index')
        index_location = 'MailArchive/index.html'

        html_start = '<head>\n<link rel="stylesheet" href="./static/css/custom.css">\n</head>\n'
        html_title = '<h2>\nEmails found by the UBF8T346G9 Parser\n</h2>\n'
        html_end = '</body>\n</html>\n'
        html_year = '<details>\n<summary>{year}</summary>\n{months}\n</details>\n'
        html_month = '<details>\n<summary>{month}</summary>\n{days}\n</details>\n'
        html_day = '<details>\n<summary>{day}</summary>\n{topics}\n</details>\n'
        html_topic_entry = '''<p>\n<a href='{path}'>{subject}</a> - id: {id}\n</p>\n'''

        years_to_write = []
        for year in sorted(self.save_paths.keys()):

            months_for_the_year = []
            for month in sorted(self.save_paths[year].keys()):

                days_for_the_month = []
                for day in sorted(self.save_paths[year][month].keys()):

                    topics_for_the_day = []
                    for topic in self.save_paths[year][month][day]:
                        topics_for_the_day.append(html_topic_entry.format(
                            path=topic.get('path'),
                            subject=topic.get('subject'),
                            id=topic.get('id'),
                        ))

                    days_for_the_month.append(
                        html_day.format(day=day, topics=''.join(topics_for_the_day)))

                months_for_the_year.append(
                    html_month.format(month=datetime.strptime(month, '%m').strftime('%B'), days=''.join(days_for_the_month)))

            years_to_write.append(
                html_year.format(year=year, months=''.join(months_for_the_year)))

        index_content = html_start + html_title + ''.join(years_to_write) + html_end

        with open(index_location, 'w') as f:
            f.write(index_content)

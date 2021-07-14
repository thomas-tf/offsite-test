import random
import pandas as pd

from io import StringIO
from datetime import datetime


class CDNLog:

    def __init__(self, number_of_records=100_000):
        self.schema = {
            'date': datetime.date,
            'time': datetime.time,
            'size': int,
            'url': str
        }
        self.number_of_records = number_of_records
        self.text_buffer = StringIO()
        self.generate_data()

    @staticmethod
    def get_random_date_and_time(start, end):
        random_datetime = random.random() * (end - start) + start
        return random_datetime.date().strftime("%Y-%m-%d"), random_datetime.time().strftime("%H:%M:%S")

    def generate_data(self):
        """
        generate dummy data into a tab separated string buffer
        :return:
        """
        start = datetime.strptime('2017-08-23', '%Y-%m-%d')
        end = datetime.strptime('2017-08-26', '%Y-%m-%d')
        file_extensions = ['.jpg', '.js', '.css']
        size_upper_bound = 100_000
        size_lower_bound = 0

        dummy_data = [(
            *self.get_random_date_and_time(start, end),  # date and time
            random.randrange(size_lower_bound, size_upper_bound),  # file size
            random.choice(file_extensions)  # file extension
        ) for _ in range(self.number_of_records)]

        # output dataframe with tab separated into buffer
        pd.DataFrame(dummy_data, columns=['date', 'time', 'size', 'url']).to_csv(self.text_buffer, sep="\t", index=False)

        # buffer position reset to 0
        self.text_buffer.seek(0)


if __name__ == '__main__':

    # setup question data
    cdnlog = CDNLog()

    df = pd.read_csv(cdnlog.text_buffer, sep='\t')

    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d")

    total_data_transfer_by_jpg_files = df[
        (df['url'].str.endswith('.jpg'))  # url endswith .jpg
        & (df['date'] >= pd.to_datetime("2017-08-24", format="%Y-%m-%d"))  # date larger than or equal to 24th Aug
        & (df['date'] <= pd.to_datetime("2017-08-25", format="%Y-%m-%d"))  # date smaller than or equal to 25th Aug
    ]['size'].sum()  # sum up the sizes

    print(f"Total data transfer by jpg files from 24th Aug to 25th Aug: {total_data_transfer_by_jpg_files}")

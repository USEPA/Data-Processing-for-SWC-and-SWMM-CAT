import datetime
from collections import namedtuple
from dataclasses import dataclass
import os

# plan is to keep this date at 1990
EARLIEST_START_DATE = datetime.datetime(1990, 1, 1)

# set the following variable to the year you are in minus 1
CURRENT_END_YEAR = 2019
CURRENT_END_DATE = datetime.datetime(CURRENT_END_YEAR, 12, 31)
CUTOFF_START_DATE = datetime.datetime(CURRENT_END_YEAR - 10 + 1, 1, 1)
CUTOFF_END_DATE = datetime.datetime(CURRENT_END_YEAR, 12, 31)


@dataclass
class Station:
    station_id: str
    station_name: str
    start_date: datetime.datetime
    end_date: datetime.datetime
    latitude: str
    longitude: str
    in_basins: bool
    break_with_basins: bool

    def get_start_date_to_use(self, basins_stations):
        if self.in_basins:
            basins_match = [x for x in basins_stations if self.station_id == x.station_id]
            assert len(basins_match) == 1
            x = basins_match[0]
            return(x.end_date + datetime.timedelta(days=1))
        else:
            if self.start_date <= EARLIEST_START_DATE:
                return EARLIEST_START_DATE
            else:
                pass

            

    def get_end_date_to_use(self, basins_stations):
        # TODO does it matter if in basins?
        if self.end_date >= CUTOFF_END_DATE:
            return CUTOFF_END_DATE
        else:
            # TODO confirm this is what they want 
            # use last complete year
            return datetime.datetime(self.end_date.year - 1, 12, 31)
            print(self.end_date)
            

# class Station:
#     def __init__(self, station_id, station_name, start_date, end_date, latitude, longitude):
#         self.station_id = station_id
#         self.station_name = station_name
#         self.start_date = start_date
#         self.end_date = end_date
#         self.latitude = latitude
#         self.longitude = longitude
#         self.in_basins = False

# Station = namedtuple('Station', ['station_id', 'station_name', 'start_date', 
#                                  'end_date', 'latitude', 'longitude'])

def make_date(input_date):
    return datetime.datetime(int(input_date[0:4]), int(input_date[4:6]), int(input_date[6:]))

def make_basins_date(input_date):
    list_date = input_date.strip('\'').split('/')
    return datetime.datetime(int(list_date[0]), int(list_date[1]), int(list_date[2]))



def read_basins_file():
    """
    Reads BASINS file
    Returns a list of Station objects representing each entry in file
    """

    basins_file = os.path.join(os.getcwd(), 'src', 'D4EMLite_PREC_Details.txt')

    with open(basins_file, 'r') as file:
        data = file.readlines()

    split_data = [item.strip('\n').split('\t') for item in data]
    header = split_data.pop(0)


    stations = [Station(item[0], item[-1], make_basins_date(item[8]), make_basins_date(item[9]), 
                        item[4], item[5], True, True) for item in split_data]

    return stations
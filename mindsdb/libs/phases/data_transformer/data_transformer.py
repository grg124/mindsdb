from dateutil.parser import parse as parse_datetime
import datetime

from mindsdb.libs.constants.mindsdb import *
from mindsdb.libs.phases.base_module import BaseModule
from mindsdb.libs.helpers.text_helpers import clean_float


class DataTransformer(BaseModule):

    @staticmethod
    def _try_round(x):
        try:
            return round(x)
        except:
            return None

    def _aply_to_all_data(self, column, func):
        input_data.data_frame[column] = input_data.data_frame[column].apply(func)
        input_data.train_df[column] = input_data.train_df[column].apply(func)
        input_data.test_df[column] = input_data.test_df[column].apply(func)
        input_data.validation_df[column] = input_data.validation_df[column].apply(func)

    def run(self, input_data, mode=None):
        for column in input_data.columns:
            if column in self.transaction.lmd['malformed_columns']['names']:
                continue

            data_type = self.transaction.lmd['column_stats'][column]['data_type']
            data_stype = self.transaction.lmd['column_stats'][column]['data_subtype']

            if data_type == DATA_TYPES.NUMERIC:
                self._aply_to_all_data(column, clean_float)

                if data_stype == DATA_SUBTYPES.INT:
                    self._aply_to_all_data(column, DataTransformer._try_round)

            if data_type = DATA_TYPES.DATE:
                if data_stype == DATA_SUBTYPES.DATE:
                    pass
                    date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

                elif data_subtype == DATA_SUBTYPES.TIMESTAMP:
                    if self.transaction.input_data.data_frame[col][row_ind] is None:
                        unix_ts = 0
                    else:
                        unix_ts = parse_datetime(self.transaction.input_data.data_frame[col][row_ind]).timestamp()

        # Un-bias dataset for training
        for colum in self.transaction.lmd['predict_columns']:
            if self.transaction.lmd['column_stats'][column]['data_type'] == DATA_TYPES.CATEGORICAL and self.transaction.lmd['balance_target_category'] == True and mode == 'train':
                occurance_map = {}
                ciclying_map = {}

                for i in range(0,len(self.transaction.lmd['column_stats'][column]['histogram']['x'])):
                    ciclying_map[self.transaction.lmd['column_stats'][column]['histogram']['x'][i]] = 0
                    occurance_map[self.transaction.lmd['column_stats'][column]['histogram']['x'][i]] = self.transaction.lmd['column_stats'][column]['histogram']['y'][i]


                max_val_occurances = max(occurance_map.values())
                for val in occurance_map:
                    while occurance_map[val] < max_val_occurances:
                        copied_row = input_data.data_frame[input_data.data_frame[colum] == val].iloc[ciclying_map[val]]

                        input_data.data_frame = input_data.data_frame.append(copied_row)
                        input_data.train_df = input_data.train_df.append(copied_row)

                        index = len(input_data.data_frame)
                        self.transaction.input_data.all_indexes[KEY_NO_GROUP_BY].append(index)
                        self.transaction.input_data.train_indexes[KEY_NO_GROUP_BY].append(index)

                        occurance_map[val] += 1
                        ciclying_map[val] += 1

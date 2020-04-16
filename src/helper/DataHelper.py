import pandas as pd 
from datetime import date, timedelta, datetime

def get_dates():
    dates = []
    for i in range(1, datetime.now().day+1):
        day = date(datetime.now().year, datetime.now().month, i)
        day = day.strftime('20%y%m%d')
        dates.append(day)
    return dates

class DataHelper():
    def __init__(self, manager=''):
        self.manager = manager

    def read_parquet(self, bucket, platform, date, country, option):
        if option == 'outlet' or option == 'information':
            option = 'information'
        elif option == 'meal':
            pass
        else:
            return 'option is invalid'

        prefix = f'{platform}/{date}/{country}_outlet_{option}.parquet.gzip'
        data = pd.read_parquet(f's3://{bucket}/{prefix}')

        return data

    def lookup(self, df, column, input):
        _temp = df[df[column].str.contains(input)]
        return _temp

    def match_outlet_meal(self, outlet_df, meal_df, outlet_name, meal_name):
        try:
            id_source = list(outlet_df[outlet_df['name'].str.contains(outlet_name)]['id_source'])[0]
        except:
            return 'Outlet does not exsit in outlet dataframe'
        
        meal_df = meal_df[meal_df['id_source'] == id_source]
        return meal_df[meal_df['name'].str.contains(meal_name)]

    def concat_daily(self, file_list, bucket='dashmote-product-daily', dup_filter = ['id_source']):
        df = pd.DataFrame()
        for key in file_list:
            print (key)
            _file = pd.read_parquet(f's3://{bucket}/{key}')
            df = pd.concat([_file, df], sort=False)
            del(_file)
        df = df.drop_duplicates(dup_filter).reset_index()
        return df

    def get_files(self, bucket, platform, date, country, option):
        results = []
        for _date in get_dates():
            files = self.manager.get_files(bucket, f'{platform}/{_date}/{country}_outlet_{option}')
            results.extend(files)
        return results



import pandas as pd 

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



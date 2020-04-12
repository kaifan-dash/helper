import DataHelper

helper = DataHelper()
bucket = 'dashmote-product-daily'
platform = 'deliveroo'
date = '20200410'
country = 'AU'
option = 'outlet'

helper.read_parquet(bucket, platform, date, country, option)
print (helper)
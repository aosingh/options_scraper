# NASDAQ Options chain Scraper

Python Options Chain scraper for the old NASDAQ website : https://old.nasdaq.com

## Install 

```bash
pip install options-scraper
```

## API

Use the API if you want to access the scraped data records ( as python objects ) directly.

### Usage

```python

from options_scraper.scraper import NASDAQOptionsScraper
from options_scraper.utils import batched

scraper = NASDAQOptionsScraper()
ticker_symbol = 'XOM'
kwargs = { "money": 'all',
           "expir": 'week',
           "excode": None,
           "callput": None
         }

records_generator = scraper(ticker_symbol, **kwargs)

# Either access each record individually as shown below
for item in records_generator:
    print(item)

# Or use the batched util to get a list of items
for items in batched(records_generator, batch_size=100):
    print(items)

```

### Output

Each scraped record will have the following structure


```python

{'Ask': '23.20',
 'Bid': '18.50',
 'Calls': 'Apr 24, 2020',
 'Chg': '',
 'Last': '19.40',
 'Open Int': '15',
 'Puts': 'Apr 24, 2020',
 'Root': 'XOM',
 'Strike': '60',
 'Vol': '0'}

{'Ask': '28.20',
 'Bid': '23.50',
 'Calls': 'Apr 24, 2020',
 'Chg': '',
 'Last': '29.67',
 'Open Int': '3',
 'Puts': 'Apr 24, 2020',
 'Root': 'XOM',
 'Strike': '65',
 'Vol': '0'}

```

## Console Script

Use this script to scrape records and save them either in CSV or JSON format.

```bash
options-scraper --help
```

```text
usage: options-scraper [-h]
                       [-l {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}]
                       [-t TICKER] 
                       [-o ODIR] 
                       [-b BATCH_SIZE] 
                       [-c {call,put}]
                       [-m {all,in,out,near}] 
                       [-e EXCODE]
                       [-x {week,stan,quart,cebo}] 
                       [-s {json,csv}]

optional arguments:
  -h, --help            show this help message and exit
  -l {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}, --log-level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}
  -t TICKER, --ticker TICKER Ticker Symbol
  -o ODIR, --odir ODIR  Output directory
  -b BATCH_SIZE, --batch_size BATCH_SIZE Batch Size
  -c {call,put}, --callput {call,put}
  -m {all,in,out,near}, --money {all,in,out,near}
  -e EXCODE, --excode EXCODE excode
  -x {week,stan,quart,cebo}, --expir {week,stan,quart,cebo}
  -s {json,csv}, --serialize {json,csv} Serialization format
```


#### Serialization format (-s)
You have an option to output the data either in a CSV file or a JSON file.
Default format is CSV.

#### Batch Size (-b)
Define how many records each csv or json file should have.


### Examples
1. To get all the option chain for XOM in a batch_size of 1000 and `csv` file format.
This will make sure that each CSV file has 1000 records in it.
The last file will have the remaining records

```bash
options-scraper -t XOM -o /Users/abhishek/options_data -b 1000 -s csv
```


2. To get all option chain data for MSFT in a batch_size of 10 and `json` file format.
```bash
options-scraper -t MSFT -o /Users/abhishek/options_data -b 10 -s json
```

3. To get all `put` options with weekly expiry.
```bash
options-scraper -t XOM -e cbo -c put -x week -o /Users/abhishek/options_data
```

4. To get all `call` options with `cebo` expiry.
```bash
options-scraper -t XOM -c call -x cebo -o /Users/abhishek/options_data
```



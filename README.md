# NASDAQ Options chain Scraper

Python Options Chain scraper for the old NASDAQ website : https://old.nasdaq.com

## Install 

```bash
pip install options-scraper
```

## Console Script


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


## Examples
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

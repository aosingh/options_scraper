# NASDAQ Options chain Scraper

## Steps to run the script.

1. Go the directory where you want to work from. 
```bash
cd <ROOT_DIR>
```

2. Clone this project in that directory using the following command.
```bash
git clone https://github.com/aosingh/options_scraper.git
ls -lrt
cd options_scraper

```

3. Create a virtual environment by typing the following command. 

```bash
virtualenv --python=python3 .venv
```

4. Activate the virtual environment using the following command

```bash
source .venv/bin/activate

```

5. Install the packages defined in the requirements.txt file using

```bash
pip install -r requirements.txt
```

6. Run the script by passing the `ticker symbol` and `output directory`. 
Please make sure that the directory location passed as input to this script exists. 
Else an `IOError` will be raise. 

```bash
python scraper.py -t XOM -o /Users/abhishek/options_data

```

7. Now, go to the directory where the output files have been generated. 
You should see the `json` files generated.

```bash
cd /Users/abhishek/options_data
ls -lrt
```

## Code Changes

To get the latest code, go the project directory where you have cloned this repository. 
```bash
cd <PROJ_DIR>
```

```bash
git pull origin master
```

## Arguments

#### Serialization format (-s)
You have an option to output the data either in a CSV file or a JSON file. 
Default format is CSV. 

#### Batch Size (-b)
Define how many records should each csv or json file should have.  


## Examples
1. To get all the option chain for XOM in a batch_size of 1000 and `csv` file format. 
This will make sure that each CSV file has 1000 records in it. 
The last file will have the remaining records
```bash
python scraper.py -t XOM -o /Users/abhishek/options_data -b 1000 -s csv
```


2. To get all option chain data for MSFT in a batch_size of 10 and `json` file format. 
```bash
python scraper.py -t MSFT -o /Users/abhishek/options_data -b 10 -s json
```




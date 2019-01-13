# Options Scraper

# Steps

1. Go the directory where you want to work from. 

2. Clone this project repo in that directory using the following command.

3. Now go the the project directory. 

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
Please make sure that the directory location passed in input exists. 

```bash
python scraper.py -t XOM -o /Users/abhishek/options_data

```

7. Now, go to the directory where the output files have been generated. 
You should see the `json` files generated.

```bash
cd /Users/abhishek/options_data
ls -lrt
```
import os
import re
import csv
import time
import json
import requests
import argparse
import datetime
import urllib.parse

from lxml import etree
from itertools import islice


last_number_pattern = re.compile(r"(?<=&page=)\d+")


def gen_pages(url):
    """
    Description:
        If for a given query the results are paginated then
        we should traverse the pages too. This function exactly does that.

    Args:
        URL - The main URL

    Returns:
        Generator - All the other pages in the search results if present.

    """
    response = requests.get(url)
    tree = etree.HTML(response.content)
    for element in tree.xpath("//*[@id='quotes_content_left_lb_LastPage']"):
        if element is not None:
            last_url = element.attrib['href']
            page_numbers = re.findall(last_number_pattern, last_url)
            if page_numbers:
                last_page = int(page_numbers[0])
                for i in range(2, last_page+1):
                    url_to_scrap = "{0}&page={1}".format(url, i)
                    yield url_to_scrap


def gen_page_records(url):
    """
    Description:
        Scrape Options data from the given URL.
        This is a 2 step process.
            1. First, extract the headers
            2. Then, the data rows.

    Args:
        url: NASDAQ URL to scrape

    Returns:
        Generator: Data records each as a dictionary

    """
    response = requests.get(url)
    tree = etree.HTML(response.content)
    headers = []
    # First, we will extract the table headers.
    for element in tree.xpath("//div[@class='OptionsChain-chart borderAll thin']"):
        for thead_element in element.xpath("table/thead/tr/th"):
            a_element = thead_element.find('a')
            if a_element is not None:
                headers.append(a_element.text.strip())
            else:
                headers.append(thead_element.text.strip())
    # Then, the data rows.
    for element in tree.xpath("//div[@class='OptionsChain-chart borderAll thin']"):
        for trow_elem in element.xpath("//tr"):
            data_row = [get_text(x) for x in trow_elem.findall("td")]
            if len(headers) == len(data_row):
                data_dict = {}
                for header_label, data_val in zip(headers, data_row):
                    data_dict[header_label] = data_val
                yield data_dict


def get_text(elt):
    """
    Description:
        Returns the text from tags.

    Args:
        elt: An lxml etree element

    Returns:
        Text within the element.
    """
    return etree.tostring(elt, method="text", encoding="unicode").strip()


def gen_options(ticker, **kwargs):
    """
    Description:
        Constructs a NASDAQ specific URL for the given Ticker Symbol and options.
        Then traverses the option data found at the URL. If there are more pages,
        the data records on the pages are traversed too.

    Args:
        ticker: A valid Ticker Symbol
        **kwargs: Mapping of query parameters that should be passed to the NASDAQ URL

    Returns:
        Generator: Options Data till the last page is reached.

    """
    params = urllib.parse.urlencode(dict((k, v) for k, v in kwargs.items() if v is not None))
    url = "https://www.nasdaq.com/symbol/{0}/option-chain?{1}".format(ticker.lower(), params)
    print("Scraping data from URL %s" % url)
    for rec in gen_page_records(url):
        yield rec

    for url in gen_pages(url):
        print("Scraping data from URL %s" % url)
        for rec in gen_page_records(url):
            yield rec


def batched(gen, batch_size):
    """
    Description:
        A util to slice a generator in a batch_size.
        The consumer can consume the generator in batches of given batch_size

    Args:
        gen: The generator to be consumed.
        batch_size: Consume batches of what size ?

    """
    while True:
        batch = list(islice(gen, 0, batch_size))
        if len(batch) == 0:
            return
        yield batch


def serialize_json(ticker, root_dir, batch_size=100, **kwargs):
    """
    Description:
        Serializes scraped options data as CSV values. Uses the `batch_size`
        parameter to decide the number of output files and distributes the total
        records equally amongst all the files. The last file will have the
        remaining records if the distribution is not even.

    Args:
        ticker: Ticker symbol. Please provide a valid Ticker Symbol.
                As of now, there is no mechanism to check if the ticker symbol is valid.
                So, it is the user's responsibility to pass the correct symbol.

        root_dir: Output directory where the files should be generated.

        batch_size: Each CSV file will have a maximum of `batch_size` records.

        **kwargs: Pass additional options which are defined in the `main()` entry-point
                  of this script.

    """
    gen = gen_options(ticker, **kwargs)
    total = 0
    for items in batched(gen, batch_size=batch_size):
        file_name = "{0}_{1}.json".format(ticker, datetime.datetime.now().isoformat())
        output_path = os.path.join(root_dir, ticker)
        output_file_path = os.path.join(output_path, file_name)
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        items_serialize = {"items": items}
        print("Scraped %s records" % len(items))
        total += len(items)

        with open(output_file_path, 'w') as output_file:
            json.dump(items_serialize, output_file, indent=4)

    print("Scraped a total of %s records for %s" % (total, ticker))


def serialize_csv(ticker, root_dir, batch_size=100, **kwargs):
    """
    Description:
        Serializes scraped options data as CSV values. Uses the `batch_size`
        parameter to decide the number of output files and distributes the total
        records equally amongst all the files. The last file will have the
        remaining records if the distribution is not even.

    Args:
        ticker: Ticker symbol. Please provide a valid Ticker Symbol.
                As of now, there is no mechanism to check if the ticker symbol is valid.
                So, it is the user's responsibility to pass the correct symbol.

        root_dir: Output directory where the files should be generated.

        batch_size: Each CSV file will have a maximum of `batch_size` records.

        **kwargs: Pass additional options which are defined in the `main()` entry-point
                  of this script.

    """
    gen = gen_options(ticker, **kwargs)
    total = 0

    for items in batched(gen, batch_size=batch_size):
        if items:
            file_name = "{0}_{1}.csv".format(ticker, datetime.datetime.now().isoformat())
            output_path = os.path.join(root_dir, ticker)
            output_file_path = os.path.join(output_path, file_name)
            if not os.path.exists(output_path):
                os.mkdir(output_path)

            with open(output_file_path, 'a') as csv_file:
                headers = list(items[0])
                # print("Headers are %s" % headers)
                writer = csv.DictWriter(csv_file, delimiter=',', lineterminator='\n', fieldnames=headers)

                # if not os.path.exists(output_file_path):
                writer.writeheader()  # file doesn't exist yet, write a header

                for item in items:
                    writer.writerow(item)
                print("Scraped %s records" % len(items))

            total += len(items)
    print("Scraped a total of %s records for %s" % (total, ticker))


def main():
    """
    Description:
        Entry-point to the script.
        Type `python <script_name.py> --help` to get details about the arguments.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--ticker", help="Ticker Symbol")
    parser.add_argument("-o", "--odir", help="Output directory")
    parser.add_argument("-b", "--batch_size", help="Batch Size", default=100, type=int)
    parser.add_argument("-c", "--callput", help="call, put or leave it blank")
    parser.add_argument("-m", "--money", help="all, in, out, near", default="all")
    parser.add_argument("-e", "--excode", help="excode")
    parser.add_argument("-x", "--expir", help="week,stan,quart,cebo")
    parser.add_argument("-s", "--serialize", help="Serialization format", default="csv")

    #     excode = None, money = "all", expir = None, callput = None

    args = parser.parse_args()
    if args.ticker is None:
        raise ValueError("Ticker symbol not passed")

    if args.odir is None:
        raise ValueError("Output Directory not passed. Provide the complete path where you want to output the files")

    if not os.path.exists(args.odir):
        raise IOError("Path {0} does not exists".format(args.odir))

    kwargs = {
        "money": args.money.lower(),
        "expir": args.expir.lower() if args.expir else None,
        "excode": args.excode.lower() if args.excode else None,
        "callput": args.callput.lower() if args.callput else None
    }

    print("Serialization format is %s. You can override this by -s parameter." % args.serialize.upper())
    print("Batch Size is %s" % args.batch_size)

    if args.serialize.lower() == "json":
        serialize_json(args.ticker, args.odir, args.batch_size, **kwargs)
    else:
        serialize_csv(args.ticker, args.odir, args.batch_size, **kwargs)


if __name__ == '__main__':
    main()


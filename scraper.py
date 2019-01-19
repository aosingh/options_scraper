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


def gen_children_url(url):
    """
    (?<=&page=)\d+
    //*[@id='quotes_content_left_lb_LastPage']
    :param url:
    :return:
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

    :param url:
    :return:
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
    """
    return etree.tostring(elt, method="text", encoding="unicode").strip()


def gen_options(ticker, **kwargs):
    """
    excode=None, money="all", expir=None, callput=None
    :param TICKER:
    :return:
    """
    params = urllib.parse.urlencode(dict((k,v) for k,v in kwargs.items() if v is not None))
    url = "https://www.nasdaq.com/symbol/{0}/option-chain?{1}".format(ticker.lower(), params)
    print("Scraping data from URL %s" % url)
    for rec in gen_page_records(url):
        yield rec

    for url in gen_children_url(url):
        print("Scraping data from URL %s" % url)
        for rec in gen_page_records(url):
            yield rec


def batched(gen, batch_size):
    """

    :param gen:
    :param batch_size:
    :return:
    """
    while True:
        batch = list(islice(gen, 0, batch_size))
        if len(batch) == 0:
            return
        yield batch


def serialize_json(ticker, root_dir, batch_size=100, **kwargs):
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
    excode=None, money="all", expir=None, callput=None
    :return:
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


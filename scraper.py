import os
import time
import json
import requests
import argparse

from lxml import etree
from itertools import islice


def gen_children_url(url):
    """

    :param url:
    :return:
    """
    response = requests.get(url)
    tree = etree.HTML(response.content)
    for element in tree.xpath("//li/a[@class='pagerlink']"):
        if element is not None and element.text and not (element.text.startswith('next') or element.text.startswith('last')):
            yield element.attrib['href']


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


def gen_options(ticker):
    """

    :param TICKER:
    :return:
    """
    url = "https://www.nasdaq.com/symbol/{0}/option-chain?excode=cbo&money=all".format(ticker.lower())
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


def serialize(ticker, root_dir, batch_size=10):
    gen = gen_options(ticker)
    total = 0
    for items in batched(gen, batch_size=batch_size):
        timestr = time.strftime("%Y_%b_%dT%H:%M:%S")
        file_name = "{0}_{1}.json".format(ticker, timestr)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--ticker", help="Ticker Symbol. Options will be scraped for this ticker symbol")
    parser.add_argument("-o", "--odir", help="Output directory where you want the output files to be generated")
    parser.add_argument("-b", "--batch_size", help="Batch Size of output file", default=100)

    args = parser.parse_args()
    if args.ticker is None:
        raise ValueError("Ticker symbol not passed")

    if args.odir is None:
        raise ValueError("Output Directory not passed. Provide the complete path where you want to output the files")

    if not os.path.exists(args.odir):
        raise IOError("Path {0} does not exists".format(args.odir))

    serialize(args.ticker, args.odir, args.batch_size)


if __name__ == '__main__':
    main()


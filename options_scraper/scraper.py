import argparse
import csv
import datetime
import json
import logging
import os
import re
import urllib.parse
from pprint import pformat
from typing import List, Mapping

import requests
from lxml import etree

from options_scraper.utils import batched, get_text

LOG = logging.getLogger(__name__)

__all__ = ['NASDAQOptionsScraper', 'NASDAQOptionsSerializer']

last_number_pattern = re.compile(r"(?<=&page=)\d+")
nasdaq_base_url = "https://old.nasdaq.com"


class NASDAQOptionsScraper:

    @staticmethod
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
                last_url = element.attrib["href"]
                page_numbers = re.findall(last_number_pattern, last_url)
                if page_numbers:
                    last_page = int(page_numbers[0])
                    for i in range(2, last_page + 1):
                        url_to_scrap = "{0}&page={1}".format(url, i)
                        yield url_to_scrap

    @staticmethod
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
        for element in tree.xpath(
                "//div[@class='OptionsChain-chart borderAll thin']"):
            for thead_element in element.xpath("table/thead/tr/th"):
                a_element = thead_element.find("a")
                if a_element is not None:
                    headers.append(a_element.text.strip())
                else:
                    headers.append(thead_element.text.strip())
        # Then, the data rows.
        for element in tree.xpath(
                "//div[@class='OptionsChain-chart borderAll thin']"):
            for trow_elem in element.xpath("//tr"):
                data_row = [get_text(x) for x in trow_elem.findall("td")]
                if len(headers) == len(data_row):
                    data_dict = {}
                    for header_label, data_val in zip(headers, data_row):
                        data_dict[header_label] = data_val
                    yield data_dict

    def __call__(self, ticker, **kwargs):
        """
        Description:
            Constructs a NASDAQ specific URL for the given Ticker Symbol and options.
            Then traverses the option data found at the URL. If there are more pages,
            the data records on the pages are scraped too.

        Args:
            ticker: A valid Ticker Symbol
            **kwargs: Mapping of query parameters that should be passed to the NASDAQ URL

        Returns:
            Generator: Each options data record as a python dictionary till
            the last page is reached.
        """
        params = urllib.parse.urlencode(
            dict((k, v) for k, v in kwargs.items() if v is not None))
        url = f"{nasdaq_base_url}/symbol/{ticker.lower()}/option-chain?{params}"

        LOG.info("Scraping data from URL %s" % url)
        for rec in self.gen_page_records(url):
            yield rec

        for url in self.gen_pages(url):
            LOG.info("Scraping data from URL %s" % url)
            for rec in self.gen_page_records(url):
                yield rec


class NASDAQOptionsSerializer:
    def __init__(
        self,
        ticker: str,
        root_dir: str,
        serialization_format: str = "csv",
        batch_size: int = 100,
    ):

        self.ticker = ticker
        self.serialization_format = serialization_format
        self.serializer = (self._to_json
                           if serialization_format == "json" else self._to_csv)
        self.output_file_date_fmt = "%Y-%m-%dT%H-%M-%S-%f"

        output_path = os.path.join(root_dir, ticker)
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        self.output_path = output_path

        self.batch_size = batch_size
        self._scraped_records = 0
        self._scraper = NASDAQOptionsScraper()

    def serialize(self, **kwargs):
        records_generator = self._scraper(self.ticker, **kwargs)
        for items in batched(records_generator, batch_size=self.batch_size):

            if items:
                timestamp = datetime.datetime.utcnow().strftime(
                    self.output_file_date_fmt)
                file_name = f"{self.ticker}_{timestamp}.{self.serialization_format}"
                self.serializer(items, os.path.join(self.output_path,
                                                    file_name))
                LOG.info("Scraped batch %s records" % len(items))

                self._scraped_records += len(items)

        LOG.info("Scraped a total of %s records for %s" %
                 (self._scraped_records, self.ticker))

    @staticmethod
    def _to_json(items: List[Mapping], file_path: str):
        items_to_serialize = {"items": items}
        with open(file_path, "w") as output_file:
            json.dump(items_to_serialize, output_file, indent=4)

    @staticmethod
    def _to_csv(items: List[Mapping], file_path: str):
        with open(file_path, "a") as csv_file:
            headers = list(items[0])
            writer = csv.DictWriter(csv_file,
                                    delimiter=",",
                                    lineterminator="\n",
                                    fieldnames=headers)
            writer.writeheader()  # file doesn't exist yet, write a header
            for item in items:
                writer.writerow(item)


def main():
    """
    Description:
        Entry point to the options scraper

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-l",
                        "--log-level",
                        default="INFO",
                        choices=list(logging._nameToLevel.keys()))
    parser.add_argument("-t", "--ticker", help="Ticker Symbol")
    parser.add_argument("-o", "--odir", help="Output directory")
    parser.add_argument("-b",
                        "--batch_size",
                        help="Batch Size",
                        default=100,
                        type=int)
    parser.add_argument("-c", "--callput", choices=["call", "put"])
    parser.add_argument("-m",
                        "--money",
                        default="all",
                        choices=["all", "in", "out", "near"])
    parser.add_argument("-e", "--excode", help="excode")
    parser.add_argument("-x",
                        "--expir",
                        choices=["week", "stan", "quart", "cebo"])
    parser.add_argument(
                        "-s",
                        "--serialize",
                        help="Serialization format",
                        default="csv",
                        choices=["json", "csv"])
    args = parser.parse_args()

    logging.basicConfig(
        level=logging._nameToLevel[args.log_level],
        format="%(asctime)s :: %(levelname)s :: %(message)s",
    )

    if args.ticker is None:
        raise ValueError("Ticker symbol not passed")

    if args.odir is None:
        raise ValueError(
            "Output Directory not passed. Provide the complete path where you want to output the files"
        )

    if not os.path.exists(args.odir):
        raise IOError("Path {0} does not exists".format(args.odir))

    kwargs = {
        "money": args.money.lower(),
        "expir": args.expir.lower() if args.expir else None,
        "excode": args.excode.lower() if args.excode else None,
        "callput": args.callput.lower() if args.callput else None,
    }

    LOG.info("VERIFY: arguments passed %s" % pformat(kwargs))
    LOG.info("Serialization format is %s" % args.serialize.upper())
    LOG.info("Batch Size is %s" % args.batch_size)

    serializer = NASDAQOptionsSerializer(
        ticker=args.ticker,
        root_dir=args.odir,
        serialization_format=args.serialize.lower(),
    )
    serializer.serialize(**kwargs)
    LOG.info("Finished Scraping")

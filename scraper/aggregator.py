from handler import SpiderFactory
from concurrent.futures import ProcessPoolExecutor
from scrapy.crawler import CrawlerProcess
import yaml, time
from glob import glob
from scrapy import signals
from scrapy.signalmanager import dispatcher
import csv, os
import pandas as pd
import argparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
from multiprocessing.context import Process
import time

output_folder = "/home/ubuntu/shared_data/scraped_articles"
os.makedirs(output_folder, exist_ok=True)

def make_csv_file(save_path, spider_name, first_row):
    csv_files = [x for x in glob(save_path + "*.csv") if spider_name in x]
    if len(csv_files) == 0:
        timestr = time.strftime("%Y%m%d_%H%M")
        filename = save_path + f"{spider_name}_{timestr}.csv"
        csv_fp = open(filename, mode='w', encoding="utf-8")
        csv_file = csv.writer(csv_fp, 
                                delimiter=',', 
                                quotechar='"', 
                                quoting=csv.QUOTE_MINIMAL)
        csv_file.writerow(first_row)
        df = None
    else:
        filename = csv_files[0]
        csv_fp = open(filename, mode='a', encoding="utf-8")
        csv_file = csv.writer(csv_fp, 
                                delimiter=',', 
                                quotechar='"', 
                                quoting=csv.QUOTE_MINIMAL)
        df = pd.read_csv(filename)
    return csv_file, filename, df, csv_fp

def load_yaml(configfp):
    with open(configfp, "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)
    return config
         
class Aggregator:
    def run(self, config):
        process = CrawlerProcess({
            "USER_AGENT": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
        })
        spider_name = config.get('spider', None)
        if spider_name is None:
            print(f"Specify Spider in config")
            return

        results = []
        on_update = False
        
        def crawler_results(signal, sender, item, response, spider):
            results.append(item)
        dispatcher.connect(crawler_results, signal=signals.item_scraped)
        
        spider = SpiderFactory.get(spider_name)
        process.crawl(spider.__class__, url=config['url'])
        process.start()
        
        if len(results) == 0:
            # nothing was returned
            print(f"Nothing was returned, so updated nothing!")
            return 

        # write results to file
        keys = list(results[0].keys()) 
        csv_file, filename, df, csv_fp = make_csv_file(output_folder, spider_name, keys)
        if df is not None:
            on_update = True
            available_hex =  list(df['hex'].values)
                    
        # add content to file
        for index in range(len(results)):
            to_append_lst = []
            for _, v in results[index].items():
                to_append_lst.append(str(v))
            content = to_append_lst[-1]
            
            # all checks go here.
            if len(content) == 0:
                print(f"Article {to_append_lst[0]} has no content")
                continue

            if on_update:
                # check if there exists this article already
                current_hex = to_append_lst[2]
                if current_hex in available_hex:
                    print(f"Article {to_append_lst[0]} is already available")
                    continue

            csv_file.writerow(to_append_lst)
            csv_fp.flush()
        csv_fp.close()
# main

def run_spider(spider_config):
    print(f"Spider {spider_config['spider']} started.")
    aggregator = Aggregator()
    aggregator.run(spider_config)
    print(f"Spider {spider_config['spider']} completed.")

def main():
    parser = argparse.ArgumentParser(
        prog='SpiderAggregator',
        description='Scraps websites.')
    parser.add_argument("-c", "--config", help="Path to the config.yaml file.")
    args = parser.parse_args()

    if args.config is None:
        print("Please provide a path to the config.yaml file using the -c or --config argument.")
        return

    config = load_yaml(args.config)
    spiders = config.get('spiders', [])

    with ProcessPoolExecutor() as executor:
        executor.map(run_spider, spiders)

if __name__ == "__main__":
    main()
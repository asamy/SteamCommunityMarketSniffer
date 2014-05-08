#
# MarketSniffer - Steam Community Market Sniffer
#
# Copyright (c) 2014 Ahmed Samy  <f.fallen45@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib.request
import urllib.error

import sys
import re
import getopt

from time import sleep
from html.parser import HTMLParser

class MarketParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.items = []
		self.foundItem = False
		self.br_before = False
		self.checkBr = False
		self.current_item_url = ""

	def handle_data(self, data):
		if self.foundItem:
			price = re.search(r'\d+.\d+', data)
			if price != None:
				self.items.append((self.current_item_url, float(price.group(0))))

	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			foundItemListing = False
			for name, value in attrs:
				if name == "class" and value == "market_listing_row_link":
					foundItemListing = True
				elif foundItemListing and name == "href":
					self.current_item_url = value
		elif tag == "span":
			for name, value in attrs:
				if value == "market_table_value":
					self.checkBr = True
		elif self.checkBr and tag == "br":
			self.foundItem = True

	def handle_endtag(self, tag):
		if tag == "br" and self.checkBr:
			self.foundItem = True
			self.checkBr = False
		elif tag == "span":
			self.foundItem = False

	def reset_all(self):
		self.reset()
		self.items = []

def help(name):
	print("Usage:")
	print("-s 	What to search for (e.g. Knife)")
	print("-n 	Number of pages to check (check that in your browser) (e.g. 35 for 35 pages)")
	print("-m 	Maximum price for the item you need (e.g. 1.3)")

def main(name, argv):
	print("Market Sniffer - Copyright (C) Ahmed Samy 2014 <f.fallen45@gmail.com>")
	print("Licensed under MIT, see this file for details.")

	try:
		opts, args = getopt.getopt(argv, "s:n:m:")
	except getopt.GetoptError:
		help(name)
		sys.exit(1)

	url = "http://steamcommunity.com/market/search?q=appid%3A730"	# appid:730 = CS:GO
	npages = 30
	max = 1

	for opt, arg in opts:
		if opt == "-h":
			help(name)
		elif opt == "-n":
			npages = int(arg)
		elif opt == "-m":
			max = float(arg)
		elif opt == "-s":
			url = url + "+" + arg

	print("Entering Main Loop, CTRL+C to exit\n")
	sleep(2)

	parser = MarketParser()
	while True:
		for i in range(1, npages + 1):
			try:
				response = urllib.request.urlopen(url + "#p" + str(i))

				parser.reset_all()
				parser.feed(str(response.read()))

				if len(parser.items) == 0:
					print("WARNING: Could not find any items on page " + str(i) + "!  Examine your search pattern.")
				else:
					for itemurl, price in parser.items:
						if price <= max:
							print("Found item with price ", price, " URL: ", itemurl)
			except urllib.error.URLError as e:
				print("Failed to check page " + str(i) + ": (" + e.reason + ")!")

if __name__ == '__main__':
	main(sys.argv[0], sys.argv[1:])

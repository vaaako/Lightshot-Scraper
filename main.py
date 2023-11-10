import requests, sys, string, webbrowser
from string import ascii_letters, digits
from time import sleep
from random import randint, choice
from bs4 import BeautifulSoup

class LightshotScraper:
	def __init__(self, mode: int = 0, url_length: int = 6, wait_time: int = 3, max: int = 999_999):
		# self.alphanumeric = alphanumeric
		_modes = [self._numeric, self._alphanumeric, self._random]
		if mode < 0 or mode > (len(_modes) - 1):
			raise RuntimeError("Type must be between 0 and " + str(len(_modes) - 1))

		self.MODE = _modes[mode]
		self.URL_LENGTH = url_length
		self.WAIT_TIME = wait_time
		self.MAX = max

		self.url = "https://prnt.sc/"
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'} # Pass cloudfare


	def _request(self, url: str):
		return requests.get(url, headers=self.headers)

	def _has_img(self, res) -> bool:
		# Pass response to soup to get HTML element
		soup = BeautifulSoup(res.text, 'html.parser')

		elements = soup.find_all('img')
		img = elements[0].get('src') # Imgur URl (just to clarify)

		# Not an imgur URL or prntscr url ("The screenshot was removed" image)
		if img.startswith('//st.prntscr.com'):
			return False

		# Query image link (can be "image.prntscr.com" or "i.imgur.com")
		img_query = self._request(img)

		# Not imgur, but image was deleted
		if img_query.status_code != 200:
			return False

		# If has redirection, was redirect to "The image you are requesting does not exist..." page (Imgur)
		if len(img_query.history) > 0:
			return False

		return True

	def _alphanumeric(self, length: int = 6) -> str:
		return ''.join(choice( ascii_letters + digits ) for _ in range(length))

	def _numeric(self) -> str:
		return str(randint(1, (10 ** self.URL_LENGTH) - 1))

	def _random(self) -> str:
		return choice([self._alphanumeric(), self._numeric()])

	def run(self, attempts: int) -> str:
		found_urls = []
		att = attempts # Just renaming to keep track

		while att > 0:
			url = self.url + str(self.MODE())
			res = self._request(url)

			# print(url)

			# URL not found
			if res.status_code != 200:
				print(f"Blocked. Waiting {self.WAIT_TIME} seconds to try again...")
				sleep(self.WAIT_TIME)
				continue # Try again

			# Query with sucess response
			if not self._has_img(res):
				continue

			# Sucess
			att -= 1
			found_urls.append(url)
			print(f"{attempts - att}. Found ({url})")

			sleep(0.50) # Wait a little bit

		return found_urls



if __name__ == "__main__":
	_modes = [ "Numeric", "Alphanumeric", "Random" ] # To display only	
	attempts = 1
	mode = 0

	if(len(sys.argv) > 1):
		try:
			attempts = int(sys.argv[1])
			if attempts < 1 or attempts > 20:
				raise ValueError("Attempts needs to be a number between 1 and 20")

			if len(sys.argv) > 2:
				mode = int(sys.argv[2])
		except (IndexError, ValueError):
			print("Attempts and Type needs to be a number between 1 and 10")
			exit()


	scraper = LightshotScraper(mode)
	print(f"Running {attempts} times with {_modes[mode]} mode...")
	urls = scraper.run(attempts)

	print("\n-= URLs =-")
	for index, url in enumerate(urls):
		print(f"{index + 1}: {url}")
		webbrowser.open(url)

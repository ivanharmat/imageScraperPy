from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.parse import urlsplit
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.error import URLError
import requests
import requests
import sys
import os
import zipfile


def urlCheck(url):
    minAttr = ('scheme' , 'netloc')
    try:
        result = urlparse(url)
        if all([result.scheme, result.netloc]):
            return True
        else:
            return False
    except:
        return False

def getBSObject(url) :
	try :
		html = urlopen(url)
	except HTTPError as e :
		return None
	except URLError as e :
		return None
	try :
		bsObj = BeautifulSoup(html.read(), "html.parser") 
	except AttributeError as e:
		return None
	return bsObj

def getAllImagesUrls(bsObj) :
	imagesUrl = []
	try :
		imagesOnPage = bsObj.findAll('img')
		for image in imagesOnPage :
			imagesUrl.append(image.get('src'))
		return imagesUrl
	except AttributeError :
		return None

def downloadImagesAndZip(url, imagesUrl) :
	url = url.rstrip('/') # remove backslash from url

	zipFileSavedToFolder = os.path.dirname(os.path.realpath(__file__))
	domainName = "{0.netloc}".format(urlsplit(url))
	zipFileName = domainName+".zip"
	zf = zipfile.ZipFile(zipFileName, mode='w')

	for downloadableUrl in imagesUrl :
		if downloadableUrl.startswith("//") :
			downloadableUrl = "https:" + downloadableUrl
		else :
			if downloadableUrl.startswith("/") :
				downloadableUrl = url + downloadableUrl

			if not downloadableUrl.startswith("http") : # still not valid url
				downloadableUrl = url + "/" + downloadableUrl
		try :
			imageExists = requests.head(downloadableUrl)
			if imageExists.status_code == 200 :
				print("downloading "+downloadableUrl)
				# download image
				imageName = downloadableUrl.split('/')[-1]
				urlretrieve(downloadableUrl, imageName)
				# add to zip archive
				zf.write(imageName)
				# remove from disk
				os.remove(imageName)
			else :
				print("Error - image doesn't exist - "+downloadableUrl)
		except requests.ConnectionError :
			print("Error - failed to download image - "+downloadableUrl)
		except requests.exceptions.MissingSchema :
			print("Error - missing schema for this image - "+downloadableUrl)

	if os.stat(zipFileName).st_size == 0 :
		print("No images found on this website.")
		zf.close()
		os.remove(zipFileName)
	else :
		print("Success - the zip file of all images was saved to "+zipFileSavedToFolder+"/"+zipFileName)
		zf.close()


if len(sys.argv) > 1 : 
	url = sys.argv[1]
	if urlCheck(url) :
		bsObj = getBSObject(url)
		imagesUrl = getAllImagesUrls(bsObj)
		downloadImagesAndZip(url, imagesUrl)
	else :
		print("Error - invalid url.")
else :
	print("Error - Enter full web url to scrape.")




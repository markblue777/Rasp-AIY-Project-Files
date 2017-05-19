################################################################################################
# Created By Mark Davies (2017)
#
# Contact: mark@mandppcs.co.uk
#
# Released under the GNU General Public License v3.0
# 
# Version 0.2
#
################################################################################################

import feedparser
import html
import time
import logging
import RPi.GPIO as gpio # Comment out when not on pi and no GPIO access
import threading

logger = logging.getLogger('rss')

class ReadRssFeed(object):
    # This is the bbc rss feed for top news in the uk
    # http://feeds.bbci.co.uk/news/rss.xml?edition=uk#

    #######################################################################################
    # constructor
    # url - rss feed url to read
    # feedCount - number of records to read
    #           -(for example bbc rss returns around 62 items and you may not want all of
    #           them read out so this allows limiting
    # properties - the rss feed properties you want spoken
    #######################################################################################
    def __init__(self, say, url, feedCount, properties):
        self.say = say
        self.rssFeedUrl = url
        self.feedCount = feedCount
        self.properties = properties
        self.cancelSpeech = False
        self.threadListenButton = None
        self.threadSpeech = None
        self.count = 0

    def run(self, voice_command):
        res = self.getNewsFeed()
        self.resetVariables()

        # If res is empty then let user know
        if res == "":
            if self.say is not None:
                self.say('Cannot get the feed')
            logger.info('Cannot get the feed')
            return

        if len(self.properties) == 0:
            if self.say is not None:
                self.say('No properties')
            logger.info('No properties')
            return

        # Setup GPIO - Comment out when not on pi and no GPIO access
        gpio.setmode(gpio.BCM)
        gpio.setup(23, gpio.IN)

        # This thread handles listening for the gpio button press to cancel out
        self.threadListenButton = threading.Thread(target=self.listenForButton, args=())
        self.threadListenButton.daemon = True
        self.threadListenButton.start()

        # This thread handles the speech
        self.threadSpeech = threading.Thread(target=self.processSpeech, args=[res])
        self.threadSpeech.daemon = True
        self.threadSpeech.start()

        # Keep alive until the user cancels speech with button press or all records are read out
        while not self.cancelSpeech:
            time.sleep(0.1)

    def getNewsFeed(self):
        # parse the feed and get the result in res
        res = feedparser.parse(self.rssFeedUrl)

        # get the total number of entries returned
        resCount = len(res.entries)

        # exit out if empty
        if resCount == 0:
            return ""

        # if the resCount is less than the feedCount specified cap the feedCount to the resCount
        if resCount < self.feedCount:
            self.feedCount = resCount

        # create empty array
        resultList = []

        # loop from 0 to feedCount so we append the right number of entries to the return list
        for x in range(0, self.feedCount):
            resultList.append(res.entries[x])

        return resultList

    def resetVariables(self):
        self.cancelSpeech = False
        self.threadListenButton = None
        self.threadSpeech = None
        self.count = 0

    def listenForButton(self):
        while not self.cancelSpeech:
            # Comment out when not on pi and no GPIO access
            if gpio.input(23) == 0:
                self.cancelSpeech = True

            # used to simulate button press (when not on a pi)
            '''
            self.count = self.count + 1
            time.sleep(1)
            if self.count == 5:
                self.cancelSpeech = #True
            '''
    def processSpeech(self, res):
        # check in various places of speech thread to see if we should terminate out of speech
        if not self.cancelSpeech:
            for item in res:
                speakMessage = ''

                if self.cancelSpeech:
                    logger.info('Cancel Speech detected')
                    break

                for property in self.properties:
                    if property in item:
                        if not speakMessage:
                            speakMessage = self.stripSpecialCharacters(item[property])
                        else:
                            speakMessage = speakMessage + ", " + self.stripSpecialCharacters(item[property])

                if self.cancelSpeech:
                    logger.info('Cancel Speech detected')
                    break

                if speakMessage != '':
                    # get item number that is being read so you can put it at the front of the message
                    logger.info('Msg: ' + speakMessage)
                    # mock the time it takes to speak the text (only needed when not using pi to actually speak)
                    # time.sleep(2)

                if self.say is not None:
                    self.say(speakMessage)

                if self.cancelSpeech:
                    logger.info('Cancel Speech detected')
                    break

            # all records read, so allow exit
            self.cancelSpeech = True

        else:
            logger.info('Cancel Speech detected')

    def stripSpecialCharacters(self, inputValue):
        return inputValue.replace('<br/>', '\n').replace('<br>', '\n').replace('<br />', '\n')

########################
# UNIT TESTS (sort of) #
########################
def main():
    # Get feed and just the title
    feed = ReadRssFeed(None, "http://feeds.bbci.co.uk/news/rss.xml?edition=uk#", 1, ['title'])
    feed.run('')

    # Get feed and the title and subtitle
    feed = ReadRssFeed(None, "http://feeds.bbci.co.uk/news/rss.xml?edition=uk#", 4, ['title', 'summary'])
    feed.run('')

    # handle no properties - empty array
    feed = ReadRssFeed(None, "http://feeds.bbci.co.uk/news/rss.xml?edition=uk#", 1, [])
    feed.run('')

    # Handle errors of invalid feed - should return cannot get feed
    feed = ReadRssFeed(None, "http://feeds.bbci.co.uk/news/rss.xm", 1, ['title', 'summary'])
    feed.run('')

    # Handle errors of invalid passed properties
    feed = ReadRssFeed(None, "http://feeds.bbci.co.uk/news/rss.xml?edition=uk#", 2, ['title_b', 'summary_b'])
    feed.run('')


if __name__ == '__main__':
    main()



# usage of it
# actor.add_keyword(_('the news'), ReadRssFeed(say, "http://feeds.bbci.co.uk/news/rss.xml?edition=uk#", 10, ['title']))


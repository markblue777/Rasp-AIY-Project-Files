################################################################################################
# Created By Mark Davies (2017)
# 
# Released under the GNU General Public License v3.0
# 
# Version 0.1
#
################################################################################################

import feedparser

#This is the class to read rss feeds (add under the section of "Makers! Implement your own actions here")
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

    def run(self, voice_command):
        res = self.getNewsFeed()

        # If res is empty then let user know
        if res == "":
            self.say('Cannot get the feed')

        # loop res and speak the title of the rss feed
        # here you could add further fields to read out
        for item in res:
            # when looping we want to to see if the item has the properties - store them in a complete string that we will read out

            # get item number that is being red

            self.say(item.title_detail.value)

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
        for x in range(0,self.feedCount):
            resultList.append(res.entries[x])

        return resultList

    # Under the "Makers! Add your own voice commands here" you can use the following to add a news reader from the bbc
    # by saying 'the news' you will be told of the top 10 news headlines from within the uk
    actor.add_keyword(_('the news'), ReadRssFeed(say, "http://feeds.bbci.co.uk/news/rss.xml?edition=uk#", 10))

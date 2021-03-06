"""
Test the topic-tree caching code (but only if caching is enabled in settings)
"""
import sys
import random
import requests
import urllib

from django.test.client import Client
from django.utils import unittest

import settings
from main import topicdata
from shared import caching
from shared.testing.base import KALiteTestCase
from shared.testing.decorators import distributed_server_test
from utils.django_utils import call_command_with_output


@distributed_server_test
class CachingTest(KALiteTestCase):

    @unittest.skipIf(settings.CACHE_TIME==0, "Test only relevant when caching is enabled")
    def test_cache_invalidation(self):
        """Create the cache item, then invalidate it and show that it is deleted."""
        
        # Get a random video id
        n_videos = len(topicdata.NODE_CACHE['Video'])
        video_id = topicdata.NODE_CACHE['Video'].keys()[10]#random.choice(topicdata.NODE_CACHE['Video'].keys())
        sys.stdout.write("Testing on video_id = %s\n" % video_id)
        video_path = topicdata.NODE_CACHE['Video'][video_id][0]['path']

        # Clean the cache for this item
        caching.expire_page(path=video_path, failure_ok=True)
        
        # Create the cache item, and check it
        self.assertTrue(not caching.has_cache_key(path=video_path), "expect: no cache key after expiring the page")
        caching.regenerate_all_pages_related_to_videos(video_ids=[video_id])
        self.assertTrue(caching.has_cache_key(path=video_path), "expect: Cache key exists after Django Client get")

        # Invalidate the cache item, and check it
        caching.invalidate_all_pages_related_to_video(video_id=video_id) # test the convenience function
        self.assertTrue(not caching.has_cache_key(path=video_path), "expect: no cache key after expiring the page")

    
    @unittest.skipIf(settings.CACHE_TIME==0, "Test only relevant when caching is enabled")
    def test_cache_across_clients(self):
        """Show that caching is accessible across all clients 
        (i.e. that different clients don't generate different cache keys)"""
        
        # Get a random video id
        n_videos = len(topicdata.NODE_CACHE['Video'])
        video_id = random.choice(topicdata.NODE_CACHE['Video'].keys())
        sys.stdout.write("Testing on video_id = %s\n" % video_id)
        video_path = topicdata.NODE_CACHE['Video'][video_id][0]['path']

        # Clean the cache for this item
        caching.expire_page(path=video_path, failure_ok=True)
        self.assertTrue(not caching.has_cache_key(path=video_path), "expect: No cache key after expiring the page")
                
        # Set up the cache with Django client
        Client().get(video_path)
        self.assertTrue(caching.has_cache_key(path=video_path), "expect: Cache key exists after Django Client get")
        caching.expire_page(path=video_path) # clean cache
        self.assertTrue(not caching.has_cache_key(path=video_path), "expect: No cache key after expiring the page")
                
        # Get the same cache key when getting with urllib, and make sure the cache is created again
        urllib.urlopen(self.live_server_url + video_path).close()
        self.assertTrue(caching.has_cache_key(path=video_path), "expect: Cache key exists after urllib get")
        caching.expire_page(path=video_path) # clean cache
        self.assertTrue(not caching.has_cache_key(path=video_path), "expect: No cache key after expiring the page")
        
        # Same deal, now using requests library
        requests.get(self.live_server_url + video_path)
        self.assertTrue(caching.has_cache_key(path=video_path), "expect: Cache key exists after requestsget")
        caching.expire_page(path=video_path) # clean cache
        self.assertTrue(not caching.has_cache_key(path=video_path), "expect: No cache key after expiring the page")

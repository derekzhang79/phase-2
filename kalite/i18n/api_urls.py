from django.conf.urls.defaults import patterns, include, url

import settings

if settings.CENTRAL_SERVER:
    urlpatterns = patterns('i18n.api_views',
        url(r'^language_packs/available$', 'get_available_language_packs', {}, 'get_available_language_packs'),
        url(r'^subtitles/counts/?$', 'get_subtitle_counts', {}, 'get_subtitle_counts'),
        url(r'^videos/dubbed_video_map$', 'get_dubbed_video_mappings', {}, 'get_dubbed_video_mappings'),
    )
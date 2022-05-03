import json
from copy import copy

from .common import InfoExtractor
from ..utils import ExtractorError, int_or_none, traverse_obj, try_get


class MiniTVIE(InfoExtractor):
    _VALID_URL = r'(?:https?://(?:www\.)?amazon\.in/minitv/tp/|minitv:(?:amzn1\.dv\.gti\.)?)(?P<id>[a-f0-9-]+)'
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36',
    }
    _CLIENT_ID = 'ATVIN'
    _DEVICE_LOCALE = 'en_GB'
    _TESTS = [{
        'url': 'https://www.amazon.in/minitv/tp/75fe3a75-b8fe-4499-8100-5c9424344840?referrer=https%3A%2F%2Fwww.amazon.in%2Fminitv',
        'md5': '0045a5ea38dddd4de5a5fcec7274b476',
        'info_dict': {
            'id': 'amzn1.dv.gti.75fe3a75-b8fe-4499-8100-5c9424344840',
            'ext': 'mp4',
            'title': 'May I Kiss You?',
            'language': 'Hindi',
            'thumbnail': r're:^https?://.*\.jpg$',
            'description': 'md5:a549bfc747973e04feb707833474e59d',
            'release_timestamp': 1644710400,
            'release_date': '20220213',
            'duration': 846,
            'chapters': [{
                'start_time': 815.0,
                'end_time': 846,
                'title': 'End Credits',
            }],
            'series': 'Couple Goals',
            'series_id': 'amzn1.dv.gti.56521d46-b040-4fd5-872e-3e70476a04b0',
            'season': 'Season 3',
            'season_number': 3,
            'season_id': 'amzn1.dv.gti.20331016-d9b9-4968-b991-c89fa4927a36',
            'episode': 'May I Kiss You?',
            'episode_number': 2,
            'episode_id': 'amzn1.dv.gti.75fe3a75-b8fe-4499-8100-5c9424344840',
        },
    }, {
        'url': 'https://www.amazon.in/minitv/tp/280d2564-584f-452f-9c98-7baf906e01ab?referrer=https%3A%2F%2Fwww.amazon.in%2Fminitv',
        'md5': '9a977bffd5d99c4dd2a32b360aee1863',
        'info_dict': {
            'id': 'amzn1.dv.gti.280d2564-584f-452f-9c98-7baf906e01ab',
            'ext': 'mp4',
            'title': 'Jahaan',
            'language': 'Hindi',
            'thumbnail': r're:^https?://.*\.jpg',
            'description': 'md5:05eb765a77bf703f322f120ec6867339',
            'release_timestamp': 1647475200,
            'release_date': '20220317',
            'duration': 783,
            'chapters': [],
        },
    }, {
        'url': 'https://www.amazon.in/minitv/tp/280d2564-584f-452f-9c98-7baf906e01ab',
        'only_matching': True,
    }, {
        'url': 'minitv:amzn1.dv.gti.280d2564-584f-452f-9c98-7baf906e01ab',
        'only_matching': True,
    }, {
        'url': 'minitv:280d2564-584f-452f-9c98-7baf906e01ab',
        'only_matching': True,
    }]

    def _call_api(self, asin, data=None, note=None):
        query = {}
        headers = copy(self._HEADERS)
        if data:
            name = 'graphql'
            data.update({
                'clientId': self._CLIENT_ID,
                'contentId': asin,
                'contentType': 'VOD',
                'deviceLocale': self._DEVICE_LOCALE,
                'sessionIdToken': self.session_id,
            })
            headers.update({'Content-Type': 'application/json'})
        else:
            name = 'prs'
            query.update({
                'clientId': self._CLIENT_ID,
                'deviceType': 'A1WMMUXPCUJL4N',
                'contentId': asin,
                'deviceLocale': self._DEVICE_LOCALE,
            })

        resp = self._download_json(
            f'https://www.amazon.in/minitv/api/web/{name}',
            asin,
            query=query,
            data=json.dumps(data).encode() if data else None,
            headers=headers,
            note=note)

        if 'errors' in resp:
            raise ExtractorError(f'MiniTV said: {resp["errors"][0]["message"]}')

        if data:
            resp = resp['data'][data['operationName']]
        return resp

    def _real_initialize(self):
        # Download webpage to get the required guest session cookies
        self._download_webpage(
            'https://www.amazon.in/minitv',
            None,
            headers=self._HEADERS,
            note='Downloading webpage')

        self.session_id = self._get_cookies('https://www.amazon.in')['session-id'].value

    def _real_extract(self, url):
        asin = f'amzn1.dv.gti.{self._match_id(url)}'

        title_info = self._call_api(
            asin,
            data={
                'operationName': 'content',
                'variables': {
                    'clientId': 'ATVIN',
                    'contentId': asin,
                    'contentType': 'VOD',
                    'deviceLocale': 'en_GB',
                    'sessionIdToken': self.session_id,
                },
                'query': '''
query content($sessionIdToken: String!, $deviceLocale: String, $contentId: ID!, $contentType: ContentType!, $clientId: String) {
  content(
    applicationContextInput: {deviceLocale: $deviceLocale, sessionIdToken: $sessionIdToken, clientId: $clientId}
    contentId: $contentId
    contentType: $contentType
  ) {
    __typename
    contentId
    name
    ... on Episode {
      contentId
      vodType
      name
      images
      description {
        synopsis
        contentLengthInSeconds
        __typename
      }
      discretionAdvice
      publicReleaseDateUTC
      studioNames
      contributorGroups
      genres
      regulatoryRating: localRegulatoryRating
      contentDescriptors
      audioTracks
      seasonId
      seriesId
      seriesName
      seasonNumber
      episodeNumber
      episodeImages
      timecode {
        endCreditsTime
        __typename
      }
      __typename
    }
    ... on MovieContent {
      contentId
      vodType
      name
      description {
        synopsis
        contentLengthInSeconds
        __typename
      }
      images
      discretionAdvice
      publicReleaseDateUTC
      studioNames
      contributorGroups
      genres
      regulatoryRating: localRegulatoryRating
      contentDescriptors
      audioTracks
      __typename
    }
  }
}''',
            },
            note='Downloading title info')

        prs = self._call_api(asin, note='Downloading playback info')

        formats = []
        for type_, asset in prs['playbackAssets'].items():
            if not isinstance(asset, dict):
                continue
            if type_ == 'hls':
                formats.extend(self._extract_m3u8_formats(
                    asset['manifestUrl'], asin, ext='mp4', entry_protocol='m3u8_native',
                    m3u8_id=type_, fatal=False))
            elif type_ == 'dash':
                formats.extend(self._extract_mpd_formats(
                    asset['manifestUrl'], asin, mpd_id=type_, fatal=False))
            else:
                pass
        self._sort_formats(formats)

        duration = traverse_obj(title_info, ('description', 'contentLengthInSeconds'))
        chapters = []
        credits_time = try_get(title_info, lambda x: x['timecode']['endCreditsTime'] / 1000)
        if credits_time is not None and duration is not None:
            chapters.append({
                'start_time': credits_time,
                'end_time': duration,
                'title': 'End Credits',
            })

        info = {
            'id': asin,
            'title': title_info['name'],
            'formats': formats,
            'language': traverse_obj(title_info, ('audioTracks', 0)),
            'thumbnails': [{
                'id': type_,
                'url': url,
            } for type_, url in title_info.get('images', {}).items()],
            'description': traverse_obj(title_info, ('description', 'synopsis')),
            'release_timestamp': int_or_none(try_get(title_info, lambda x: x['publicReleaseDateUTC'] / 1000)),
            'duration': duration,
            'chapters': chapters,
            'series': title_info.get('seriesName'),
            'series_id': title_info.get('seriesId'),
            'season_number': title_info.get('seasonNumber'),
            'season_id': title_info.get('seasonId'),
            'episode_number': title_info.get('episodeNumber'),
        }
        if title_info.get('vodType') == 'EPISODE':
            info.update({
                'episode': title_info['name'],
                'episode_id': asin,
            })

        return info


class MiniTVSeasonIE(MiniTVIE):
    IE_NAME = 'minitv:season'
    _VALID_URL = r'minitv:season:(?:amzn1\.dv\.gti\.)?(?P<id>[a-f0-9-]+)'
    _TESTS = [{
        'url': 'minitv:season:amzn1.dv.gti.0aa996eb-6a1b-4886-a342-387fbd2f1db0',
        'playlist_mincount': 6,
        'info_dict': {
            'id': 'amzn1.dv.gti.0aa996eb-6a1b-4886-a342-387fbd2f1db0',
        },
    }, {
        'url': 'minitv:season:0aa996eb-6a1b-4886-a342-387fbd2f1db0',
        'only_matching': True,
    }]

    def _entries(self, asin):
        season_info = self._call_api(
            asin,
            data={
                'operationName': 'getEpisodes',
                'variables': {
                    'sessionIdToken': self.session_id,
                    'clientId': 'ATVIN',
                    'episodeOrSeasonId': asin,
                    'deviceLocale': 'en_GB',
                },
                'query': '''
query getEpisodes($sessionIdToken: String!, $clientId: String, $episodeOrSeasonId: ID!, $deviceLocale: String) {
  getEpisodes(
    applicationContextInput: {sessionIdToken: $sessionIdToken, deviceLocale: $deviceLocale, clientId: $clientId}
    episodeOrSeasonId: $episodeOrSeasonId
  ) {
    episodes {
      ... on Episode {
        contentId
        name
        images
        seriesName
        seasonId
        seriesId
        seasonNumber
        episodeNumber
        watchedPercentage
        description {
          synopsis
          contentLengthInSeconds
          __typename
        }
        publicReleaseDateUTC
        __typename
      }
      __typename
    }
    __typename
  }
}
''',
            },
            note='Downloading season info')

        for episode in season_info['episodes']:
            yield self.url_result(f'minitv:{episode["contentId"]}', ie=MiniTVIE.ie_key())

    def _real_extract(self, url):
        asin = f'amzn1.dv.gti.{self._match_id(url)}'
        return self.playlist_result(self._entries(asin), playlist_id=asin)


class MiniTVSeriesIE(MiniTVIE):
    IE_NAME = 'minitv:series'
    _VALID_URL = r'minitv:series:(?:amzn1\.dv\.gti\.)?(?P<id>[a-f0-9-]+)'
    _TESTS = [{
        'url': 'minitv:series:amzn1.dv.gti.56521d46-b040-4fd5-872e-3e70476a04b0',
        'playlist_mincount': 3,
        'info_dict': {
            'id': 'amzn1.dv.gti.56521d46-b040-4fd5-872e-3e70476a04b0',
        },
    }, {
        'url': 'minitv:series:56521d46-b040-4fd5-872e-3e70476a04b0',
        'only_matching': True,
    }]

    def _entries(self, asin):
        season_info = self._call_api(
            asin,
            data={
                'operationName': 'getSeasons',
                'variables': {
                    'sessionIdToken': self.session_id,
                    'deviceLocale': 'en_GB',
                    'episodeOrSeasonOrSeriesId': asin,
                    'clientId': 'ATVIN',
                },
                'query': '''
query getSeasons($sessionIdToken: String!, $deviceLocale: String, $episodeOrSeasonOrSeriesId: ID!, $clientId: String) {
  getSeasons(
    applicationContextInput: {deviceLocale: $deviceLocale, sessionIdToken: $sessionIdToken, clientId: $clientId}
    episodeOrSeasonOrSeriesId: $episodeOrSeasonOrSeriesId
  ) {
    seasons {
      seasonId
      description {
        synopsis
        __typename
      }
      seasonNumber
      continueWatchingEpisodeId
      isScripted
      __typename
    }
    __typename
  }
}
''',
            },
            note='Downloading series info')

        for season in season_info['seasons']:
            yield self.url_result(f'minitv:season:{season["seasonId"]}', ie=MiniTVSeasonIE.ie_key())

    def _real_extract(self, url):
        asin = f'amzn1.dv.gti.{self._match_id(url)}'
        return self.playlist_result(self._entries(asin), playlist_id=asin)

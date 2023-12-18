from .common import InfoExtractor
from ..utils import format_field, parse_iso8601, traverse_obj, urljoin


class RinseFMIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?rinse\.fm/episodes/(?P<id>[^/?#]+)'
    _TESTS = [{
        'url': 'https://rinse.fm/episodes/club-glow-15-12-2023-2000/',
        'md5': '76ee0b719315617df42e15e710f46c7b',
        'info_dict': {
            'id': '1536535',
            'ext': 'mp3',
            'title': 'Club Glow - 15/12/2023 - 20:00',
            'thumbnail': r're:^https://.+\.(?:jpg|JPG)$',
            'release_timestamp': 1702598400,
            'release_date': '20231215'
        }
    }]

    def _real_extract(self, url):
        display_id = self._match_id(url)
        webpage = self._download_webpage(url, display_id)
        entry = self._search_nextjs_data(webpage, display_id)['props']['pageProps']['entry']

        return {
            'id': entry['id'],
            'title': entry.get('title'),
            'url': entry['fileUrl'],
            'vcodec': 'none',
            'release_timestamp': parse_iso8601(entry.get('episodeDate')),
            'thumbnail': format_field(
                entry, [('featuredImage', 0, 'filename')], 'https://rinse.imgix.net/media/%s', default=None),
        }


class RinseFMArtistPlaylistIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?rinse\.fm/shows/(?P<id>[^/?#]+)'
    _TESTS = [{
        'url': 'https://rinse.fm/shows/resources/',
        'md5': '76ee0b719315617df42e15e710f46c7b',
        'info_dict': {
            'id': 'resources',
            'title': '[re]sources',
            'description': '[re]sources est un label parisien piloté par le DJ et producteur Tommy Kid.'
        },
        'playlist_mincount': 40
    }, {
        'url': 'https://rinse.fm/shows/ivy/',
        'md5': '4b2e8c70530a89b8d905a2b572316eb8',
        'info_dict': {
            'id': 'ivy',
            'title': '[IVY]',
            'description': 'A dedicated space for DNB/Turbo House and 4x4.'
        },
        'playlist_mincount': 9
    }]

    def _entries(self, episodes):
        for episode in episodes:
            yield episode.get('slug')

    def _real_extract(self, url):
        playlist_id = self._match_id(url)
        webpage = self._download_webpage(url, playlist_id)
        title = self._og_search_title(webpage) or self._html_search_meta('title', webpage)
        description = self._og_search_description(webpage) or self._html_search_meta(
            'description', webpage)

        episodes = traverse_obj(self._search_nextjs_data(
            webpage, playlist_id), ('props', 'pageProps', 'episodes'))

        return self.playlist_from_matches(
            self._entries(episodes), playlist_id, title, description=description,
            ie=RinseFMIE, getter=lambda x: urljoin('https://rinse.fm/episodes/', x))

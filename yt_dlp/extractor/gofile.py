# coding: utf-8
from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    try_get
)


class GofileIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?gofile\.io/d/(?P<id>[^/]+)'
    _TESTS = [{
        'url': 'https://gofile.io/d/AMZyDw',
        'info_dict': {
            'id': 'AMZyDw',
        },
        'playlist_mincount': 2,
        'playlist': [{
            'info_dict': {
                'id': 'de571ac1-5edc-42e2-8ec2-bdac83ad4a31',
                'filesize': 928116,
                'ext': 'mp4',
                'title': 'nuuh'
            }
        }]
    }]
    _TOKEN = None


    def _real_initialize(self):
        token = self._get_cookies('https://gofile.io/').get('accountToken')
        if token:
            self._TOKEN = token.value
            return

        account_data = self._download_json(
            'https://api.gofile.io/createAccount', None, note='Getting a new guest account')
        self._TOKEN = accountdata['data']['token']
        self._set_cookie('gofile.io', 'accountToken', self._TOKEN)

    def _entries(self, file_id):
        files = self._download_json(
            f'https://api.gofile.io/getContent?contentId={file_id}&token={self._TOKEN}&websiteToken=websiteToken&cache=true',
            'Gofile', note='Getting filelist')

        status = files['status']
        if status != 'ok':
            raise ExtractorError('Received error from service, status: %s' % status, expected=True)

        found_files = False
        for file in (try_get(files, lambda x: x['data']['contents'], dict) or {}).values():
            file_type, file_format = file.get('mimetype').split('/', 1)
            if file_type not in ('video', 'audio') and file_format != 'vnd.mts':
                continue

            found_files = True
            yield {
                'id': file['id'],
                'title': file['name'].rsplit('.', 1)[0],
                'url': file['directLink'],
                'filesize': file.get('size'),
                'release_timestamp': file.get('createTime')
            }

        if not found_files:
            self.raise_no_formats('No video/audio found at provided URL.', expected=True)

    def _real_extract(self, url):
        file_id = self._match_id(url)
        return self.playlist_result(self._entries(file_id), playlist_id=file_id)

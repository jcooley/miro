# Miro - an RSS based video player application
# Copyright (C) 2012
# Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
#
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

"""miro.data.item -- Defines ItemInfo and ways to fetch them."""

import collections
import os

from miro import app
from miro import filetypes
from miro import fileutil
from miro import prefs
from miro import util
from miro.plat import resources

class _SelectColumn(object):
    """Describes a single column that we use in our SELECT statement."""
    def __init__(self, table, column, attr_name=None):
        if attr_name is None:
            attr_name = column
        self.table = table
        self.column = column
        self.attr_name = attr_name

_select_columns = [
    _SelectColumn('item', 'id'),
    _SelectColumn('item', 'new'),
    _SelectColumn('item', 'title'),
    _SelectColumn('item', 'feed_id'),
    _SelectColumn('item', 'parent_id'),
    _SelectColumn('item', 'downloader_id'),
    _SelectColumn('item', 'is_file_item'),
    _SelectColumn('item', 'pending_manual_download'),
    _SelectColumn('item', 'pending_reason'),
    _SelectColumn('item', 'expired'),
    _SelectColumn('item', 'keep'),
    _SelectColumn('item', 'downloaded_time'),
    _SelectColumn('item', 'watched_time'),
    _SelectColumn('item', 'last_watched'),
    _SelectColumn('item', 'subtitle_encoding'),
    _SelectColumn('item', 'is_container_item'),
    _SelectColumn('item', 'release_date'),
    _SelectColumn('item', 'duration'),
    _SelectColumn('item', 'screenshot'),
    _SelectColumn('item', 'resume_time'),
    _SelectColumn('item', 'license'),
    _SelectColumn('item', 'rss_id'),
    _SelectColumn('item', 'entry_description'),
    _SelectColumn('item', 'enclosure_type', 'mime_type'),
    _SelectColumn('item', 'enclosure_format'),
    _SelectColumn('item', 'enclosure_size'),
    _SelectColumn('item', 'link'),
    _SelectColumn('item', 'payment_link'),
    _SelectColumn('item', 'comments_link'),
    _SelectColumn('item', 'url'),
    _SelectColumn('item', 'was_downloaded'),
    _SelectColumn('item', 'filename'),
    _SelectColumn('item', 'play_count'),
    _SelectColumn('item', 'skip_count'),
    _SelectColumn('item', 'cover_art'),
    _SelectColumn('item', 'description'),
    _SelectColumn('item', 'album'),
    _SelectColumn('item', 'album_artist'),
    _SelectColumn('item', 'artist'),
    _SelectColumn('item', 'track'),
    _SelectColumn('item', 'album_tracks'),
    _SelectColumn('item', 'year'),
    _SelectColumn('item', 'genre'),
    _SelectColumn('item', 'rating'),
    _SelectColumn('item', 'file_type'),
    _SelectColumn('item', 'has_drm'),
    _SelectColumn('item', 'show'),
    _SelectColumn('item', 'episode_id'),
    _SelectColumn('item', 'episode_number'),
    _SelectColumn('item', 'season_number'),
    _SelectColumn('item', 'kind'),
    _SelectColumn('item', 'net_lookup_enabled'),
    _SelectColumn('item', 'eligible_for_autodownload'),
    _SelectColumn('feed', 'orig_url', 'feed_url'),
    _SelectColumn('feed', 'expire', 'feed_expire'),
    _SelectColumn('feed', 'expireTime', 'feed_expire_time'),
    _SelectColumn('feed', 'autoDownloadable', 'feed_auto_downloadable'),
    _SelectColumn('feed', 'getEverything', 'feed_get_everything'),
    _SelectColumn('icon_cache', 'filename', 'icon_cache_filename'),
    _SelectColumn('remote_downloader', 'content_type',
                  'downloader_content_type'),
    _SelectColumn('remote_downloader', 'state', 'downloader_state'),
    _SelectColumn('remote_downloader', 'reason_failed'),
    _SelectColumn('remote_downloader', 'short_reason_failed'),
    _SelectColumn('remote_downloader', 'type', 'downloader_type'),
    _SelectColumn('remote_downloader', 'retry_time'),
    _SelectColumn('dlstats', 'eta'),
    _SelectColumn('dlstats', 'rate'),
    _SelectColumn('dlstats', 'upload_rate'),
    _SelectColumn('dlstats', 'current_size', 'downloaded_size'),
    _SelectColumn('dlstats', 'total_size', 'downloader_size'),
    _SelectColumn('dlstats', 'upload_size'),
    _SelectColumn('dlstats', 'activity'),
    _SelectColumn('dlstats', 'seeders'),
    _SelectColumn('dlstats', 'leechers'),
    _SelectColumn('dlstats', 'connections'),
]

# ItemRow is the base class for item.
ItemRow = collections.namedtuple("ItemRow",
                                 [c.attr_name for c in _select_columns])

class ItemInfo(ItemRow):
    """ItemInfo represents a row in one of the item lists.

    This work similarly to the miro.item.Item class, except it's read-only.
    """
    html_stripper = util.HTMLStripper()

    source_type = 'database'

    # NOTE: The previous ItemInfo API was all attributes, so we use properties
    # to try to match that.

    @property
    def downloaded(self):
        return self.filename is None

    @property
    def is_playable(self):
        return self.filename is not None and self.file_type != u'other'

    @property
    def is_torrent(self):
        return self.downloader_type == u'bittorrent'

    @property
    def is_torrent_folder(self):
        return self.is_torrent and self.is_container_item

    def looks_like_torrent(self):
        return self.is_torrent or filetypes.is_torrent_filename(self.url)

    @property
    def description_stripped(self):
        if not hasattr(self, '_description_stripped'):
            self._description_stripped = ItemInfo.html_stripper.strip(
                self.description)
        return self._description_stripped

    @property
    def feed_name(self):
        # TODO: implement me
        return None

    @property
    def thumbnail(self):
        if self.cover_art and fileutil.exists(path):
            return self.cover_art
        if (self.icon_cache_filename and
            fileutil.exists(self.icon_cache_filename)):
            return self.icon_cache_filename
        if self.screenshot and fileutil.exists(self.screenshot):
            return self.screenshot
        if self.is_container_item:
            return resources.path("images/thumb-default-folder.png")
        else:
            # TODO: check for feed thumbnail here
            if self.file_type == u'audio':
                return resources.path("images/thumb-default-audio.png")
            else:
                return resources.path("images/thumb-default-video.png")

    @property
    def is_external(self):
        """Was this item downloaded by Miro, but not part of a feed?
        """
        if self.is_file_item:
            return self.parent_id is not None
        else:
            return self.feed_url == 'dtv:manualFeed'

    @property
    def size(self):
        """Get the size for an item.

        We try these methods in order to get the size:

        1. Physical size of a downloaded file
        2. HTTP content-length
        3. RSS enclosure tag value
        """
        if self.filename is not None:
            try:
                return os.path.getsize(self.filename)
            except OSError:
                return None
        elif self.is_download:
            return self.downloader_size
        else:
            return self.enclosure_size

    @property
    def file_format(self):
        """Returns string with the format of the video.
        """
        if self.looks_like_torrent():
            return u'.torrent'

        if self.enclosure_format is not None:
            return self.enclosure_format

        if (self.downloader_content_type is not None and
            "/" in self.downloader_content_type):
            mtype, subtype = self.downloader_content_type.split('/', 1)
            mtype = mtype.lower()
            if mtype in KNOWN_MIME_TYPES:
                format_ = subtype.split(';')[0].upper()
                if mtype == u'audio':
                    format_ += u' AUDIO'
                if format_.startswith(u'X-'):
                    format_ = format_[2:]
                return (u'.%s' %
                        MIME_SUBSITUTIONS.get(format_, format_).lower())

        return u""

    @property
    def expiration_date(self):
        """When will this item expire?

        :returns: a datetime.datetime object or None if it doesn't expire.
        """
        if self.watched_time is None or self.filename is None or self.keep:
            return None

        if feed_expire == u'never':
            return None
        elif feed_expire == u"feed":
            expire_time = feed_expire_time
        elif feed_expire == u"system":
            expire_time = timedelta(
                days=app.config.get(prefs.EXPIRE_AFTER_X_DAYS))
        else:
            raise AssertionError("Unknown expire value: %s" % feed_expire)
        if expire_time <= 0:
            return None
        return self.get_watched_time() + expire_time

    @property
    def is_download(self):
        return self.downloader_state in ('downloading', 'paused')

    @property
    def is_paused(self):
        return self.downloader_state == 'paused'

    @property
    def is_seeding(self):
        return self.downloader_state == 'uploading'

    @property
    def download_progress(self):
        """Calculate how for a download has progressed.

        :returns: [0.0, 1.0] depending on how much has been downloaded, or
        None if we don't have the info to make this calculation
        """
        if self.downloaded_size == 0:
            # if downloaded_size is 0, then this download probably hasn't
            # started.  Even if we don't know the total size, return 0.0
            return 0.0
        if self.downloaded_size is None or self.downloader_size is None:
            # unknown total size, return None
            return None
        return float(self.downloaded_size) / self.downloader_size

    @property
    def is_failed_download(self):
        return self.downloader_state == 'failed'

    @property
    def pending_auto_dl(self):
        return (self.feed_auto_downloadable and
                not self.was_downloaded and
                self.feed_auto_downloadable and
                (self.feed_get_everything or self.eligible_for_autodownload))

class ItemFetcher(object):
    """Fetches items from a database."""

    def __init__(self):
        self._prepare_sql()

    def _prepare_sql(self):
        """Get an SQL statement ready to fire when fetch() is called.

        The statement will be ready to go, except the WHERE clause will not be
        present, since we can't know that in advance.
        """
        columns = ['%s.%s' % (c.table, c.column) for c in _select_columns]
        sql_parts = []
        sql_parts.append("SELECT %s" % ', '.join(columns))
        sql_parts.append("FROM item")
        sql_parts.append("LEFT JOIN feed ON feed.id=item.feed_id")
        sql_parts.append("LEFT JOIN icon_cache ON feed.id=item.icon_cache_id")
        sql_parts.append("LEFT JOIN remote_downloader "
                         "ON remote_downloader.id=item.downloader_id")
        sql_parts.append("LEFT JOIN dlstats "
                         "ON dlstats.id=item.downloader_id")
        self._sql = ' '.join(sql_parts)

    def fetch(self, connection, id):
        """Create Item objects."""
        where = "WHERE item.id=?"
        sql = ' '.join((self._sql, where))
        cursor = connection.execute(sql, (id,))
        return ItemInfo(*cursor.fetchone())

    def fetch_many(self, connection, id_list):
        """Create Item objects."""
        where = "WHERE item.id in (%s)" % ', '.join(str(i) for i in id_list)
        sql = ' '.join((self._sql, where))
        cursor = connection.execute(sql)
        return [ItemInfo(*row) for row in cursor]

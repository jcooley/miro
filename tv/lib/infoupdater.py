# Miro - an RSS based video player application
# Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011
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

"""``miro.infoupdater`` -- The infoupdater module holds:

* :class:`InfoUpdater` -- tracks channel/item updates from the backend
  and sends the information to the frontend
* :class:`InfoUpdaterCallbackList` -- tracks the list of callbacks for
  info updater
"""
from miro import signals

class InfoUpdaterCallbackList(object):
    """Tracks the list of callbacks for InfoUpdater.
    """

    def __init__(self):
        self._callbacks = {}

    def add(self, type_, id_, callback):
        """Adds the callback to the list for ``type_`` ``id_``.

        :param type_: the type of the thing (feed, site, ...)
        :param id_: the id for the thing
        :param callback: the callback function to add
        """
        key = (type_, id_)
        self._callbacks.setdefault(key, set()).add(callback)

    def remove(self, type_, id_, callback):
        """Removes the callback from the list for ``type_`` ``id_``.

        :param type_: the type of the thing (feed, site, ...)
        :param id_: the id for the thing
        :param callback: the callback function to remove
        """
        key = (type_, id_)
        callback_set = self._callbacks[key]
        callback_set.remove(callback)
        if len(callback_set) == 0:
            del self._callbacks[key]

    def get(self, type_, id_):
        """Get the list of callbacks for ``type_``, ``id_``.

        :param type_: the type of the thing (feed, site, ...)
        :param id_: the id for the thing
        """
        key = (type_, id_)
        if key not in self._callbacks:
            return []
        else:
            # return a new list of callbacks, so that if we iterate over the
            # return value, we don't have to worry about callbacks being
            # removed midway.
            return list(self._callbacks[key])

class InfoUpdater(signals.SignalEmitter):
    """Track channel/item updates from the backend.

    To track item updates, use the item_list_callbacks and
    item_changed_callbacks attributes, both are instances of
    InfoUpdaterCallbackList.  To track tab updates, connect to one of the
    signals below.

    Signals:

    * feeds-added (self, info_list) -- New feeds were added
    * feeds-changed (self, info_list) -- Feeds were changed
    * feeds-removed (self, info_list) -- Feeds were removed
    * sites-added (self, info_list) -- New sites were added
    * sites-changed (self, info_list) -- Sites were changed
    * sites-removed (self, info_list) -- Sites were removed
    * playlists-added (self, info_list) -- New playlists were added
    * playlists-changed (self, info_list) -- Playlists were changed
    * playlists-removed (self, info_list) -- Playlists were removed
    """
    def __init__(self):
        signals.SignalEmitter.__init__(self)
        for prefix in ('feeds', 'sites', 'playlists'):
            self.create_signal('%s-added' % prefix)
            self.create_signal('%s-changed' % prefix)
            self.create_signal('%s-removed' % prefix)

        self.item_list_callbacks = InfoUpdaterCallbackList()
        self.item_changed_callbacks = InfoUpdaterCallbackList()

    def handle_items_changed(self, message):
        callback_list = self.item_changed_callbacks
        for callback in callback_list.get(message.type, message.id):
            callback(message)

    def handle_item_list(self, message):
        callback_list = self.item_list_callbacks
        for callback in callback_list.get(message.type, message.id):
            callback(message)

    def handle_tabs_changed(self, message):
        if message.type == 'feed':
            signal_start = 'feeds'
        elif message.type == 'site':
            signal_start = 'sites'
        elif message.type == 'playlist':
            signal_start = 'playlists'
        else:
            return
        if message.added:
            self.emit('%s-added' % signal_start, message.added)
        if message.changed:
            self.emit('%s-changed' % signal_start, message.changed)
        if message.removed:
            self.emit('%s-removed' % signal_start, message.removed)

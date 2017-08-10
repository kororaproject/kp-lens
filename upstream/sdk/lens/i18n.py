#
# Copyright 2012-2017 "Korora Project" <dev@kororaproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the temms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Lesser GNU General Public License for more details.
#
# You should have received a copy of the Lesser GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import gettext
import os

class Lang():
    def __init__(self, app):

        self._app = None
        self._languages = []
        self._locale_dir = None

        if app is not None:
            self.bind(app)

        self._translations = {'raw': {}}

    def bind(self, app):
        for ns in app.namespaces:
            path = os.path.join(ns, 'locales')

            if os.path.exists(path):
                self._locale_dir = path
                return

    def add_string(self, id, *args):
        self._translations['raw'][id] = list(args)

    def add_language(self, id):
        if id in self._translations:
            return

        self._translations[id] = {}
        self._languages.append(id)

    def get(self, id, lang='raw'):
        s = self._translations.get(lang, self._translations['raw']).get(id, '');

        return s

    def nget(self, id, count, lang='raw'):
        s = self._translations.get(lang, self._translations['raw']).get(id, '');

        return s

    def resolve(self):
        print('RESOLVING')

        for l in self._languages:
            print(l)
            ll = gettext.translation('sample-app-i18n', localedir=self._locale_dir, languages=[l])

            for k in self._translations['raw']:
                print("Key: {0}".format(k))

                self._translations[l][k] = [ll.gettext(v) for v in self._translations['raw'][k]]



        print(self._translations)



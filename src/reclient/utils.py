# -*- coding: utf-8 -*-
# Copyright © 2014 SEE AUTHORS FILE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from subprocess import call
import tempfile
import json
import logging
import difflib

out = logging.getLogger('reclient')

def temp_json_blob(data):
    """data is either a string or a hash. Function will 'do the right
thing' either way"""
    out.debug("tmp_json_blob received [%s]: %s" % (type(data), str(data)))
    if type(data) in [unicode, str]:
        data = json.loads(data)
    elif type(data) == dict or type(data) == list:
        pass
    else:
        raise ValueError("This isn't something I can work with")

    tmpfile = tempfile.NamedTemporaryFile(mode='w',
                                          suffix=".json",
                                          prefix="reclient-")
    json.dump(data, tmpfile, indent=4)
    tmpfile.flush()
    return tmpfile

# def differ(orig, new):
#     """Diff two documents and open in 'less'. 'orig' and 'new' should be
#     file pointers"""
#     d = difflib.Differ()

def edit_playbook(blob):
    """Edit the playbook object 'blob'.

If 'blob' is an unserialized string, then it is serialized and dumped
(with indenting) out to a temporary file.

If 'blob' is a serialized hash is is dumped out (with indenting) to a
temporary file.

If 'blob' is a file object (like you would get from 'temp_json_blob')
it is flush()'d.

Once all that is complete, an editor is opened pointing at the path to
the temporary file. After the editor is closed the original (or
instantiated) file handle is returned."""
    EDITOR = os.environ.get('EDITOR', 'emacs')
    callcmd = [EDITOR]
    tmpfile = blob

    if isinstance(blob, tempfile._TemporaryFileWrapper):
        blob.flush()
    else:
        tmpfile = temp_json_blob(blob)

    try:
        if EDITOR == "emacs":
            # Do not launch in graphical mode
            callcmd.extend(["-nw", tmpfile.name])
        else:
            callcmd.append(tmpfile.name)

        print "Going to launch editor with args: %s" % str(callcmd)

        call(callcmd)
    except OSError, e:
        callcmd.extend(tmpfile.name)
        call(callcmd)

    return tmpfile


def less_file(path):
    call(['less', path])

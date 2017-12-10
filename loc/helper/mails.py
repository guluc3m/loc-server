# -*- coding: utf-8 -*-
#
# League of Code server implementation
# https://github.com/guluc3m/loc-server
#
# The MIT License (MIT)
#
# Copyright (c) 2017 Grupo de Usuarios de Linux UC3M <http://gul.es>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Mails."""

from flask_babel import lazy_gettext as t


# Welcome
WELCOME_SUBJECT = t('Welcome to League of Code')
WELCOME_BODY = t(
    'Welcome to the League of Code, %(username)s!\n\n'
    'You can now login from %(link)s.\n\n'
    'Happy Hacking!'
)
WELCOME_HTML = t(
    'Welcome to the League of Code, %(username)s!<br/><br/>'
    'You can now login from <a href="%(link)s">the application</a>.<br/><br/>'
    'Happy Hacking!'
)

# Forgot password
FORGOT_PASSWORD_SUBJECT = t('League of Code - Reset your password')
FORGOT_PASSWORD_BODY = t(
    'Hello %(username)s,\n\n'
    'We have received a request to reset your password. If you have not done '
    'this, then it is safe to ignore this email.\n\n'
    'You can reset your password through the following link: %(link)s'
)
FORGOT_PASSWORD_HTML = t(
    'Hello %(username)s,<br/><br/>'
    'We have received a request to reset your password. If you have not done '
    'this, then it is safe to ignore this email.<br/><br/>'
    'You can reset your password through the <a href="%(link)s">following link</a>.'
)

# Kicked from party
KICKED_SUBJECT = t('League of Code - Kicked from party')
KICKED_BODY = t(
    'Hello %(username)s,\n\n'
    'This is a notification to let you know that you have been kicked from a '
    'party for the match: %(match)s.\n\n'
    'You are still signed up for the match, but are now alone in your own party.'
)
KICKED_HTML = (
    'Hello %(username)s,<br/><br/>'
    'This is a notification to let you know that you have been kicked from a '
    'party for the match: %(match)s.<br/><br/>'
    'You are still signed up for the match, but are now alone in your own party.'
)

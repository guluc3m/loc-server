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

"""Model definition."""

from loc import db
from sqlalchemy.ext.associationproxy import association_proxy


class Follower(db.Model):
    """User followers.

    Attributes:
        follower_id (int): Unique ID of user that is following.
        followee_id (int): Unique ID of user that is being followed
    """
    __tablename__ = 'followers'

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )
    followee_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )


class Match(db.Model):
    """Development matches.

    Attributes:
        id (int): Unique ID of the match.
        title (str): Title of the match.
        short_description (str): Short description with very basic information.
        long_description (str): Complete description with details and rules.
            Only shown once the match has started.
        start_date (date): Date in which the match starts. No party registrations
            can occur after this date.
        end_date (date): Date in which the match ends. No submissions are
            accepted after this date.
        min_members (int): Minimum number of users in a party.
        max_members (int): Maximum number of users in a party.
        leaderboard (str): Sorted comma-separated list of parties taking into
            account their position after finishing the match
        slug (str): Unique slug generated from the title of the match.
        is_visible (bool): Whether this match should be shown publicly.
        is_deleted (bool): Whether the record has been (soft) deleted.
        delete_date (date): Date in which the record was (soft) deleted.
    """
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    short_description = db.Column(db.String(255), nullable=False)
    long_description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    min_members = db.Column(db.Integer, nullable=False, default=1)
    max_members = db.Column(db.Integer, nullable=False, default=1)
    leaderboard = db.Column(db.Text)
    slug = db.Column(db.String(128), nullable=False, unique=True)
    is_visible = db.Column(db.Boolean, nullable=False, default=False)

    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    delete_date = db.Column(db.DateTime)


    def as_dict(self, include_long=False):
        """Get record fields as a dictionary.

        This is an utility method for use when creating a response.

        Args:
            include_long (bool): Include the long description (should be done
        o        only if the match has started).
        Returns:
            dict with all the public attributes.
        """
        return {
            'id': self.id,
            'title': self.title,
            'short-description': self.short_description,
            'long-description': self.long_description if include_long else '',
            'start-date': self.start_date.isoformat(),
            'end-date': self.end_date.isoformat(),
            'min-members': self.min_members,
            'max-members': self.max_members,
            'slug': self.slug
        }


class MatchParticipant(db.Model):
    """Match participants.

    Attributes:
        user_id (int): Unique ID of the participant.
        match_id (int): Match ID where the user is participating.
        party_owner_id (int): ID of the owner of the party the user is in.
        is_participating (bool): Whether the user is participating in the match.
    """
    __tablename__ = 'match_participants'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)

    party_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_participating = db.Column(db.Boolean, default=False)


class PartyToken(db.Model):
    """Party tokens used to join a party.

    Attributes:
        owner_id (int): ID of the owner of the party.
        match_id (int): ID of the match the party is participating in.
        token (str): Unique random token.
        is_public (bool): Whether the party can be publicly found.
    """
    __tablename__ = 'party_tokens'

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), primary_key=True)

    token = db.Column(db.String(32), unique=True)
    is_public = db.Column(db.Boolean, default=False)


class Role(db.Model):
    """Special roles used for some actions.

    The following roles are specified:
        admin: can perform special actions such as creation of matches

    Attributes:
        id (int): Unique ID of the role.
        name (str): Unique name of the role.
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    @classmethod
    def get_role(cls, name):
        """Obtain an already existing role by name.

        Args:
            name(str): Unique name of the role.

        Returns:
            `Role` instance or `None` if not found
        """
        return cls.query.filter_by(name=name).first()


class Submission(db.Model):
    """Project submission for a match.

    Attributes:
        id (int): Unique ID of the submission.
        title (str): Short title of the project.
        description (str): Long description of the project.
        url (str): URL from which the project can be downloaded.
        match_id (int): ID of the match this submission belongs to.
        party_owner_id (int): ID of the owner of the submitting party.
    """
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(512), nullable=False)

    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    party_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class User(db.Model):
    """Platform users.

    Attributes:
        id (int): ID of the user record.
        username (str): Unique username.
        name (str): (Optional) Real name of the user.
        email (str): Unique email used for communication and password reset.
        password (str): Encrypted password.
        points (int): Total score obtained by participating in matches.
        pasword_reset_token (str): Unique token for restoring password.
        token_expiration (date): Date in which the reset token stops being valid.
            Usually should be 24 hours after the creation of the token.
        is_deleted (bool): Whether the record has been (soft) deleted.
        delete_date (date): Date in which the record was (soft) deleted.
        _jwt_counter (int): Counter to invalidate old tokens.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(128), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False, default='')
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, nullable=False, default=0)

    password_reset_token = db.Column(db.String(64))
    token_expiration = db.Column(db.DateTime)

    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    delete_date = db.Column(db.DateTime)

    _jwt_counter = db.Column(db.Integer, nullable=False, default=0)

    # Relationships
    following = db.relationship(
        'User',
        secondary='followers',
        primaryjoin='User.id==Follower.follower_id',
        secondaryjoin='User.id==Follower.followee_id',
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    roles = db.relationship(
        'Role',
        secondary='user_roles',
        backref=db.backref('users', lazy='dynamic'),
        cascade='delete, save-update',
        collection_class=set
    )

    # Proxies
    role_names = association_proxy(
        'roles',
        'name',
        creator=lambda n: Role.get_role(n)
    )


class UserRole(db.Model):
    """Roles assigned to a specific user.

    Attributes:
        user_id (int): ID of the user.
        role_id (int): ID of the role.
    """
    __tablename__ = 'user_roles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

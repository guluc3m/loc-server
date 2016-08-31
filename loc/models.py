# -*- coding: utf-8 -*-

"""SQLalchemy model declarations."""

from loc import db
from sqlalchemy.ext.associationproxy import association_proxy

class Friend(db.Model):
    """Accepted friend requests.

    These records are bi-directional.

    Attributes:
        user_id1 (int): Unique ID of user 1.
        user_id2 (int): Unique ID of user 2.
    """
    __tablename__ = 'friends'

    user_id1 = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )
    user_id2 = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )


class FriendRequest(db.Model):
    """Pending friend invitations.

    Attributes:
        id (int): Unique ID of the record.
        sender_id (int): ID of the sender.
        receiver_id (int): ID of the receiver.
        token (str): Unique token used to accept the invitation.
    """
    __tablename__ = 'friend_requests'

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    token = db.Column(db.String(64), nullable=False, unique=True)

    # Constraints
    __table_args__ = (db.UniqueConstraint('sender_id', 'receiver_id'),)


class Match(db.Model):
    """Development matches.

    Attributes:
        id (int): Unique ID of the match.
        title (str): Title of the match.
        short_description (str): Short description with very basic information.
        long_description (str): Complete description with details and rules.
            Only shown once the match has started.
        start_date (date): Date in which the match starts. No team registrations
            can occur after this date.
        end_date (date): Date in which the match ends. No submissions are
            accepted after this date.
        min_team (int): Minimum number of users in a team.
        max_team (int): Maximum number of users in a team.
        is_visible (bool): Whether or not this match should be shown publicly.
        is_deleted (bool): Whether or not the record has been deleted.
        delete_date (date): Date in which the record was deleted.
    """
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(128), nullable=False)
    short_description = db.Column(db.String(255), nullable=False)
    long_description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    min_team = db.Column(db.Integer, nullable=False, default=1)
    max_team = db.Column(db.Integer, nullable=False, default=1)
    is_visible = db.Column(db.Boolean, nullable=False, default=False)

    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    delete_date = db.Column(db.DateTime)


class Role(db.Model):
    """Special roles recognized in the platform

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
    """Team submission for a specific match

    Attributes:
        id (int): Unique ID of the record.
        title (str): Title of the submitted project.
        description (str): Description of the submitted project.
        url (str): URL to a repository.
        team_id (int): ID of the team.
    """
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))


class Team(db.Model):
    """Team participating in a match.

    Attributes:
        id (int): Unique ID of the record.
        owner_id (int): ID of the user that created the team.
        match_id (int): ID of the match.
        num_members (int): Total number of members in the team.
        is_participating (bool): Whether all members have accepted or not.
        is_disqualified (bool): Whether the team is disqualified or not.
        is_winner (bool): Whether the team has won or not.
    """
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    num_members = db.Column(db.Integer, nullable=False, default=1)
    is_participating = db.Column(db.Boolean, nullable=False, default=False)
    is_disqualified = db.Column(db.Boolean, nullable=False, default=False)
    is_winner = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    submission = db.relationship('Submission', backref='team', lazy='dynamic')

    # Constraints
    __table_args__ = (db.UniqueConstraint('owner_id', 'match_id'), )


class TeamInvite(db.Model):
    """Pending team invitations.

    Attributes:
        id (int): Unique ID of the record.
        team_id (int): ID of the team.
        user_id (int): ID of the invited user.
        token (str): Unique token used to accept the invite.
    """
    __tablename__ = 'team_invites'

    id = db.Column(db.Integer, primary_key=True)

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    token = db.Column(db.String(64), nullable=False, unique=True)

    # Constraints
    __table_args__ = (db.UniqueConstraint('team_id', 'user_id'),)


class TeamMember(db.Model):
    """Member of a team.

    These records are only created when users accept team invitations.

    Attributes:
        team_id (int): ID of the team.
        user_id (int): ID of the user.
    """
    __tablename__ = 'team_members'

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)


class User(db.Model):
    """LoC users.

    Attributes:
        id (int): ID of the user record.
        username (str): Unique username.
        email (str): Unique email used for communication and password reset.
        password (str): Encrypted password.
        score (int): Total score.
        pasword_reset_token (str): Unique token for restoring password.
        token_expiration (date): Date in which the reset token stops being valid.
            Usually should be 24 hours after the creation of the token.
        is_deleted (bool): Whether or not the record has been deleted.
        delete_date (date): Date in which the record was deleted.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer)

    password_reset_token = db.Column(db.String(64))
    token_expiration = db.Column(db.DateTime)

    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    delete_date = db.Column(db.DateTime)

    # Relationships
    _friends_sent = db.relationship(
        'User',
        secondary='friends',
        primaryjoin='User.id==Friend.user_id1',
        secondaryjoin='User.id==Friend.user_id2',
        backref=db.backref('_friends_received', lazy='dynamic'),
        lazy='dynamic'
    )

    friend_requests_sent = db.relationship(
        'User',
        secondary='friend_requests',
        primaryjoin='User.id==FriendRequest.sender_id',
        secondaryjoin='User.id==FriendRequest.receiver_id',
        backref=db.backref('friends_requests_received', lazy='dynamic'),
        lazy='dynamic'
    )

    roles = db.relationship(
        'Role',
        secondary='user_roles',
        backref=db.backref('users', lazy='dynamic'),
        cascade='delete, save-update',
        collection_class=set
    )

    _teams = db.relationship(
        'Team',
        secondary='team_members',
        backref=db.backref('members', lazy='dynamic'),
        lazy='dynamic',
        collection_class=set
    )

    _teams_owner = db.relationship('Team', backref='owner', lazy='dynamic')

    team_invites = db.relationship(
        'Team',
        secondary='team_invites',
        backref=db.backref('invited_users', lazy='dynamic'),
        lazy='dynamic',
        collection_class=set
    )

    # Proxies
    role_names = association_proxy(
        'roles',
        'name',
        creator=lambda n: Role.get_role(n)
    )

    @property
    def friends(self):
        """Obtain friends (sent and received invitations)."""
        return self._friends_sent.union(self._friends_received)

    @property
    def teams(self):
        """Obtain teams of which the user is owner or member."""
        return self._teams.union(self._teams_owner)


class UserRole(db.Model):
    """Roles assigned to a specific user.

    Attributes:
        user_id (int): ID of the user
        role_id (int): ID of the role
    """
    __tablename__ = 'user_roles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

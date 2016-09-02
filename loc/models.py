# -*- coding: utf-8 -*-

"""SQLalchemy model declarations."""

from loc import db
from sqlalchemy.ext.associationproxy import association_proxy

class Follower(db.Model):
    """User followers.

    Attributes:
        follower_id (int): Unique ID of user that is following.
        following_id (int): Unique ID of user that is being followed
    """
    __tablename__ = 'followers'

    follower_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )
    following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True
    )


class Loadout(db.Model):
    """Team template.

    Loadouts are lists of users that can be used to automatically create a
    team for a specific match.

    Attributes:
        id (int): Unique ID of the record.
        name (str): Name of the loadout.
        owner_id (int): ID of the owner.
    """
    __tablename__ = 'loadouts'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Relationships
    members = db.relationship(
        'User',
        secondary='loadout_members',
        lazy='dynamic',
        collection_class=set
    )

    # Constraints
    __table_args__ = (db.UniqueConstraint('name', 'owner_id'),)


class LoadoutMember(db.Model):
    """Members in a specific loadout.

    Attributes:
        loadout_id (int): ID of the loadout.
        user_id (int): ID of the user/member.
    """
    __tablename__ = 'loadout_members'

    loadout_id = db.Column(
        db.Integer,
        db.ForeignKey('loadouts.id'),
        primary_key=True
    )

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)


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
        slug (str): Unique slug generated from the title of the match.
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
    slug = db.Column(db.String(128), nullable=False, unique=True)
    is_visible = db.Column(db.Boolean, nullable=False, default=False)

    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    delete_date = db.Column(db.DateTime)

    # Relationships
    teams = db.relationship('Team', backref='match', lazy='dynamic')


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
        invite_token (str): Unique token used to join the team.
        position (int): Position in which the team finished. When there is a
            value of -1, the match has not finished or the team has been
            disqualified.
        is_participating (bool): Whether all members have accepted or not.
        is_disqualified (bool): Whether the team is disqualified or not.
    """
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))
    invite_token = db.Column(db.String(64), nullable=False, unique=True)
    position = db.Column(db.Integer, nullable=False, default=-1)
    is_participating = db.Column(db.Boolean, nullable=False, default=False)
    is_disqualified = db.Column(db.Boolean, nullable=False, default=False)

    # Relationships
    submission = db.relationship('Submission', backref='team', lazy='dynamic')

    # Constraints
    __table_args__ = (db.UniqueConstraint('owner_id', 'match_id'), )


class TeamMember(db.Model):
    """Member of a team.

    These records created when users join teams through invitations.

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
    score = db.Column(db.Integer, nullable=False, default=0)

    password_reset_token = db.Column(db.String(64))
    token_expiration = db.Column(db.DateTime)

    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    delete_date = db.Column(db.DateTime)

    # Relationships
    following = db.relationship(
        'User',
        secondary='followers',
        primaryjoin='User.id==Follower.follower_id',
        secondaryjoin='User.id==Follower.following_id',
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    loadouts = db.relationship('Loadout', backref='owner', lazy='dynamic')

    roles = db.relationship(
        'Role',
        secondary='user_roles',
        backref=db.backref('users', lazy='dynamic'),
        cascade='delete, save-update',
        collection_class=set
    )

    teams = db.relationship(
        'Team',
        secondary='team_members',
        backref=db.backref('members', lazy='dynamic'),
        lazy='dynamic',
        collection_class=set
    )

    teams_owner = db.relationship('Team', backref='owner', lazy='dynamic')

    # Proxies
    role_names = association_proxy(
        'roles',
        'name',
        creator=lambda n: Role.get_role(n)
    )


class UserRole(db.Model):
    """Roles assigned to a specific user.

    Attributes:
        user_id (int): ID of the user
        role_id (int): ID of the role
    """
    __tablename__ = 'user_roles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)

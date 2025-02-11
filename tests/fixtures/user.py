""" Module to create fixture users. """

from functools import wraps
from datetime import date, datetime

import pytest

from collectives.models import User, Gender, db, Role, RoleIds, ActivityType

# pylint: disable=unused-argument,redefined-outer-name

PASSWORD = "fooBar2+!"
""" Default test password for non admin users.

:type: string
"""


def inject_fixture(name, someparam, names):
    """Create and add a new fixture user.

    :param string name: Fixture name.
    :param int someparam: A unique identifier number for this user. It is not the
        user id. It determines the user license number.
    :param "(string,string)" names: First and lastname of the user.
    """
    globals()[name] = generate_user(someparam, names)


def generate_user(identifier, names):
    """Generate fixture users.

    :param int id: An identifiying integer for the user
    :param (string,string) names: first and last names for the user
    :returns: the newly created user
    :rtype: :py:class:`collectives.models.user.User`"""

    @wraps(identifier)
    @wraps(names)
    @pytest.fixture
    def user(app):
        """A Standard user"""
        user = User()
        user.first_name = names[0]
        user.last_name = names[1]
        user.gender = Gender.Unknown
        user.mail = f"user{identifier}@example.org"
        user.is_test = True
        user.license = str(identifier + 990000000000)
        user.license_category = "XX"
        user.date_of_birth = date(2000, 1, identifier % 30)
        user.password = PASSWORD
        user.phone = "060102030{id:03}"
        user.emergency_contact_name = f"Emergency {identifier}"
        user.emergency_contact_phone = f"0699999{identifier:03}"
        user.legal_text_signature_date = datetime.now()
        user.legal_text_signed_version = 1

        db.session.add(user)
        db.session.commit()
        return user

    return user


USER_NAMES = [
    ("Jan", "Johnston"),
    ("Evan", "Walsh"),
    ("Kimberly", "Paterson"),
    ("Jake", "Marshall"),
    ("Boris", "Bailey"),
    ("Frank", "Morgan"),
    ("Chloe", "White"),
    ("Michael", "Davidson"),
    ("Theresa", "Bailey"),
    ("Jake", "Piper"),
]
""" Basic list of names.

:type: list()"""
for i, user_name in enumerate(USER_NAMES):
    inject_fixture(f"user{i}", i, user_name)


@pytest.fixture
def admin_user(app):
    """:returns: The admin user."""
    return User.query.get(1)


inject_fixture("prototype_leader_user", 999, ("Romeo", "Capo"))


@pytest.fixture
def leader_user(prototype_leader_user):
    """:returns: An Alpinisme leader user."""
    promote_to_leader(prototype_leader_user)
    db.session.add(prototype_leader_user)
    db.session.commit()
    return prototype_leader_user


@pytest.fixture
def leader_user_with_event(leader_user, event1):
    """:returns: A leader User which leads event1"""
    event1.leaders.append(leader_user)
    event1.main_leader = leader_user
    db.session.add(leader_user)
    db.session.commit()
    return leader_user


inject_fixture("prototype_leader2_user", 998, ("Evan", "Przewodnik"))


@pytest.fixture
def leader2_user(prototype_leader2_user):
    """:returns: An Alpinisme leader user."""
    promote_to_leader(prototype_leader2_user)
    db.session.add(prototype_leader2_user)
    db.session.commit()
    return prototype_leader2_user


@pytest.fixture
def leader2_user_with_event(leader2_user, event2):
    """:returns: A leader User which leads event2"""
    event2.leaders.append(leader2_user)
    event2.main_leader = leader2_user
    db.session.add(leader2_user)
    db.session.commit()
    return leader2_user


inject_fixture("prototype_president_user", 997, ("Russ", "Guevara"))


@pytest.fixture
def president_user(prototype_president_user):
    """:returns: A user with a president role."""
    promote_user(prototype_president_user, RoleIds.President, None)
    db.session.add(prototype_president_user)
    db.session.commit()
    return prototype_president_user


inject_fixture("prototype_supervisor_user", 996, ("Ted", "Fincher"))


@pytest.fixture
def supervisor_user(prototype_supervisor_user):
    """:returns: A user with an Alpinisme supervisor role."""
    promote_user(prototype_supervisor_user, RoleIds.ActivitySupervisor)
    db.session.add(prototype_supervisor_user)
    db.session.commit()
    return prototype_supervisor_user


def promote_to_leader(user, activity="Alpinisme"):
    """Add a leader role to a user.

    :param User user: the user to be promoted
    :param string activity: Activity name to which user will be promoted. Defaul Alpinisme
    """
    promote_user(user, RoleIds.EventLeader, activity)


def promote_user(
    user, role_id, activity_name="Alpinisme", confidentiality_agreement_signature=True
):
    """Manage to add a role to a user

    :param User user: the user to promote
    :param RoleIds role_id: the type of user to add
    :param string activity_name: The activity name for the role. Default Alpinisme
    :param bool confidentiality_agreement_signature: If method should sign the
        confidentiality agreement for the user.
    """
    role = Role()
    role.user_id = user.id
    role.role_id = role_id
    if activity_name:
        activity_type = ActivityType.query.filter_by(name=activity_name).first()
        role.activity_id = activity_type.id
    if confidentiality_agreement_signature:
        user.confidentiality_agreement_signature_date = datetime.now()
    db.session.add(role)

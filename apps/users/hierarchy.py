"""
Role hierarchy: admin > word_manager > word_checker > word_uploader.
Higher level users can manage (CRUD) lower level users.
"""
ROLE_LEVEL = {
    'admin': 4,
    'word_manager': 3,
    'word_checker': 2,
    'word_uploader': 1,
}


def get_role_level(role):
    """Return numeric level for a role (higher = more privilege)."""
    return ROLE_LEVEL.get(role, 0)


def can_manage(actor, target):
    """True if actor can manage target (actor's level > target's level)."""
    if not actor or not target:
        return False
    return get_role_level(actor.role) > get_role_level(target.role)


def can_assign_role(actor, role_to_assign):
    """True if actor can assign this role (only lower levels)."""
    return get_role_level(actor.role) > get_role_level(role_to_assign)


def assignable_roles(actor):
    """List of roles that actor can assign (lower level only)."""
    actor_level = get_role_level(actor.role)
    return [r for r, level in ROLE_LEVEL.items() if level < actor_level]

from .db import get_user_db
from .accounts import get_account_from_id


class User:
    def __init__(self, user_id, **kwargs) -> None:
        self.user_id = user_id

    def is_authenticated(self) -> bool:
        """This property should return True
        if the user is authenticated,
        i.e. they have provided valid credentials.
        (Only authenticated users will fulfill
        the criteria of login_required.)

        Returns
        -------
        bool
            _description_
        """
        return True

    def is_active(self) -> bool:
        """This property should return True
        if this is an active user -
        in addition to being authenticated,
        they also have activated their account,
        not been suspended, or any condition your
        application has for rejecting an account.
        Inactive accounts may not log in
        (without being forced of course).

        Returns
        -------
        bool
            _description_
        """
        return True

    def is_anonymous(self) -> bool:
        """This property should return True
        if this is an anonymous user.
        (Actual users should return False instead.)

        Returns
        -------
        bool
            _description_
        """

    def get_id(self) -> str:
        """This method must return a str
        that uniquely identifies this user,
        and can be used to load the user
        from the user_loader callback.
        Note that this must be a str -
        if the ID is natively an int
        or some other type,
        you will need to convert it to str.

        Returns
        -------
        str
            _description_
        """
        return str(self.user_id)

    def get(user_id: str) -> "User":
        conn = get_user_db()
        with conn.cursor() as cur:
            user_data = get_account_from_id(cur, user_id)
        if user_data is None:
            return None
        return User(**user_data)

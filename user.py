from flask_login import UserMixin

from db import get_db


class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic, age, nationality):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic
        self.age = age
        self.nationality = nationality

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3], age=user[4], nationality=user[5]
        )
        return user

    @staticmethod
    def create(id_, name, email, profile_pic, age, nationality):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic, age, nationality) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (id_, name, email, profile_pic, age, nationality),
        )
        db.commit()

# class ContributedPost:
#     def __init__(self,id,title,amount):
#         self.id = id
#         self.title = title
#         self.amount = title

#     @staticmethod
#     def get(post_id):
#         db = get_db()
#         post = db.execute(
#             "SELECT * FROM post WHERE id = ?", (post_id,)
#         ).fetchone()
#         if not post:
#             return None

#         post = ContributedPost(
#             id_=post[0], name=post[1], email=post[2], profile_pic=post[3]
#         )
#         return post

#     @staticmethod
#     def create(id_, name, email, profile_pic):
#         db = get_db()
#         db.execute(
#             "INSERT INTO post (id, name, email, profile_pic) "
#             "VALUES (?, ?, ?, ?)",
#             (id_, name, email, profile_pic),
#         )
#         db.commit()

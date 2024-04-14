from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
api = Api(app)
CORS(app)

class Post(Resource):
    def get(self, postid):
        #####################################################################################3
        #### Important -- This is the how the connection must be done for autograder to work
        ### But on your local machine, you may need to remove "host=..." part if this doesn't work
        #####################################################################################3
        conn = psycopg2.connect("host=127.0.0.1 dbname=stackexchange user=root password=root")
        cur = conn.cursor()

        cur.execute("select id, posttypeid, title, AcceptedAnswerID, creationdate from posts where id = %s" % (postid))
        ans = cur.fetchall()
        if len(ans) == 0:
            return "Post Not Found", 404
        else:
            ret = {"id": ans[0][0], "PostTypeID": ans[0][1], "Title": str(ans[0][2]), "AcceptedAnswerID": str(ans[0][3]), "CreationDate": str(ans[0][4])}
            return ret, 200


class Dashboard(Resource):
    # Return some sort of a summary of the data -- we will use the "name" attribute to decide which of the dashboards to return
    # 
    # Here the goal is to return the top 100 users using the reputation -- this will be returned as an array in increasing order of Rank
    # Use PostgreSQL default RANK function (that does sparse ranking), followed by a limit 100 to get the top 100 
    #
    # FORMAT: {"Top 100 Users by Reputation": [{"ID": "...", "DisplayName": "...", "Reputation": "...", "Rank": "..."}, {"ID": "...", "DisplayName": "...", "Reputation": "...", "Rank": "..."}, ]
    def get(self, name):
        if name == "top100users":
            conn = psycopg2.connect("host=127.0.0.1 dbname=stackexchange user=root password=root")
            curr = conn.cursor()
            curr.execute("SELECT id, displayname, reputation, RANK() OVER (ORDER BY reputation desc) FROM users LIMIT 100")
            ans = curr.fetchall()
            result = [{"ID": row[0], "DisplayName": row[1], "Reputation": row[2], "Rank": row[3]} for row in ans]
            return {"Top 100 Users by Reputation": result}, 200
        else:
            return "Unknown Dashboard Name", 404

class User(Resource):
    # Return all the info about a specific user, including the titles of the user's posts as an array
    # The titles array must be sorted in the increasing order by the title.
    # Remove NULL titles if any
    # FORMAT: {"ID": "...", "DisplayName": "...", "CreationDate": "...", "Reputation": "...", "PostTitles": ["posttitle1", "posttitle2", ...]}
    def get(self, userid):
        # Add your code to construct "ret" using the format shown below
        # Post Titles must be sorted in alphabetically increasing order
        # CreationDate should be of the format: "2007-02-04" (this is what Python str() will give you)

        # Add your code to check if the userid is already present in the database
        conn = psycopg2.connect("host=127.0.0.1 dbname=stackexchange user=root password=root")
        cur = conn.cursor()

        cur.execute("SELECT users.id, users.displayname, users.creationdate, users.reputation, array_remove(array_agg(posts.title), null) as arr" +
            " FROM users JOIN posts on users.id = posts.owneruserid " +
            "WHERE users.id = %s group by users.id, users.displayname, users.creationdate, users.reputation" % (userid))

        ans = cur.fetchall()
        exists_user = len(ans) > 0
        if not exists_user:
            return "User not found", 404
        else:
            ret = {"ID": ans[0][0], "DisplayName": ans[0][1], "CreationDate": str(ans[0][2]), "Reputation": ans[0][3], "PostTitles": sorted(ans[0][4])}
            return ret, 200

    # Add a new user into the database, using the information that's part of the POST request
    # We have provided the code to parse the POST payload
    # If the "id" is already present in the database, a FAILURE message should be returned
    def post(self, userid):
        parser = reqparse.RequestParser()
        parser.add_argument("reputation")
        parser.add_argument("creationdate")
        parser.add_argument("displayname")
        parser.add_argument("upvotes")
        parser.add_argument("downvotes")
        args = parser.parse_args()
        print("Data received for new user with id {}".format(userid))
        print(args)

        # Add your code to check if the userid is already present in the database
        conn = psycopg2.connect("host=127.0.0.1 dbname=stackexchange user=root password=root")
        curr = conn.cursor()

        curr.execute("SELECT * FROM users WHERE id = %s" % (userid))
        ans = curr.fetchall()
        exists_user = len(ans) > 0

        if exists_user:
            return "FAILURE -- Userid must be unique", 201
        else:
            # Add your code to insert the new tuple into the database
            curr.execute("INSERT INTO users (id, displayname, creationdate, reputation, upvotes, downvotes, views) VALUES (%s, %s, %s, %s, %s, %s, 0)", (userid, args["displayname"], args["creationdate"], args["reputation"], args["upvotes"], args["downvotes"]))
            conn.commit()
            return "SUCCESS", 201

    # Delete the user with the specific user id from the database
    def delete(self, userid):
        # Add your code to check if the userid is present in the database

        conn = psycopg2.connect("host=127.0.0.1 dbname=stackexchange user=root password=root")
        curr = conn.cursor()

        curr.execute("SELECT * FROM users WHERE id = %s" % (userid))
        ans = curr.fetchall()
        exists_user = len(ans) > 0

        if exists_user:
            # Add your code to delete the user from the user table
            # If there are corresponding entries in "badges" table for that userid, those should be deleted
            # For posts, comments, votes, set the appropriate userid fields to -1 (since that content should not be deleted)
            curr.execute("DELETE FROM badges WHERE userid = %s" % (userid))
            curr.execute("UPDATE posts SET owneruserid = -1 WHERE owneruserid = %s" % (userid))
            curr.execute("UPDATE posts SET lasteditoruserid = -1 WHERE lasteditoruserid = %s" % (userid))
            curr.execute("UPDATE comments SET userid = -1 WHERE userid = %s" % (userid))
            curr.execute("UPDATE votes SET userid = -1 WHERE userid = %s" % (userid))
            curr.execute("DELETE FROM users WHERE id = %s" % (userid))
            conn.commit()
            return "SUCCESS", 201
        else:
            return "FAILURE -- Unknown Userid", 404
      
api.add_resource(User, "/user/<int:userid>")
api.add_resource(Post, "/post/<int:postid>")
api.add_resource(Dashboard, "/dashboard/<string:name>")

app.run(debug=True, host="0.0.0.0", port=5000)

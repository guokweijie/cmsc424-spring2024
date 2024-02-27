queries = ["" for i in range(0, 17)]

### 0. List all the users who have at least 1000 UpVotes.
### Output columns and order: Id, Reputation, CreationDate, DisplayName
### Order by Id ascending
queries[0] = """
select Id, Reputation, CreationDate,  DisplayName
from users
where UpVotes >= 1000
order by Id asc;
"""

### 1. Write a query to find all Posts who satisfy one of the following conditions:
###        - the post title contains 'postgres' and the number of views is at least 50000
###        - the post title contains 'mongodb' and the number of views is at least 25000
### The match should be case insensitive
###
### Output columns: Id, Title, ViewCount
### Order by: Id ascending
queries[1] = """
select Id, Title, ViewCount
from posts
where (Title ILIKE '%postgres%' and ViewCount >= 50000) or (Title ILIKE '%mongodb%' and ViewCount >= 25000);
"""

### 2. Count the number of the Badges for the user with DisplayName 'JHFB'.
###
### Output columns: Num_Badges
queries[2] = """
select count(*) as Num_Badges
from users join badges on (users.id = badges.userid)
where DisplayName = 'JHFB';
"""

### 3. Find the Users who have received a "Guru" badge, but not a "Curious" badge.
### Only report a user once even if they have received multiple badges with the above names.
###
### Hint: Use Except (set operation).
###
### Output columns: UserId
### Order by: UserId ascending
queries[3] = """
select UserId
from badges
WHERE Name = 'Guru'
EXCEPT
select UserId
from badges
where Name = 'Curious'
ORDER BY UserId ASC;
"""

### 4. "Tags" field in Posts lists out the tags associated with the post in the format "<tag1><tag2>..<tagn>".
### Find the Posts with at least 4 tags, with one of the tags being sql-server-2008 (exact match).
### Hint: use "string_to_array" and "cardinality" functions.
### Output columns: Id, Title, Tags
### Order by Id
queries[4] = """
select Id, Title, Tags
from posts
where cardinality(string_to_array(tags, '><')) >= 4 and tags ILIKE '%<sql-server-2008>%'
order by Id;
"""

### 5. SQL "with" clause can be used to simplify queries. It essentially allows
### specifying temporary tables to be used during the rest of the query. See Section
### 3.8.6 (6th Edition) for some examples.
###
### Write a query to find the name(s) of the user(s) with the largest number of badges. 
### We have provided a part of the query to build a temporary table.
###
### Output columns: Id, DisplayName, Num_Badges
### Order by Id ascending (there may be more than one answer)
queries[5] = """
with temp as (
        select Users.Id, DisplayName, count(*) as num_badges 
        from users join badges on (users.id = badges.userid)
        group by users.id, users.displayname)
select *
from temp
where num_badges = (select max(num_badges) from temp)
order by id asc;
"""

### 6. "With" clauses can be chained together to simplify complex queries. 
###
### Write a query to associate with each user the number of posts they own as well as the
### number of badges they have received, assuming they have at least one post and
### one badge. We have provided a part of the query to build two temporary tables.
###
### Restrict the output to users with id less than 100.
###
### Output columns: Id, DisplayName, Num_Posts, Num_Badges
### Order by Id ascending
queries[6] = """
with temp1 as (
        select owneruserid, count(*) as num_posts
        from posts
        group by owneruserid),
temp2 as (
        select userid, count(*) as num_badges
        from badges
        group by userid)
select users.id, displayname, num_posts, num_badges
from users, temp1, temp2
where temp1.owneruserid = users.id and temp2.userid = users.id and users.id < 100
order by users.id asc;
"""

### 7. A problem with the above query is that it may not include users who have no posts or no badges.
### Use "left outer join" to include all users in the output.
###
### Feel free to modify the "with" clauses to simplify the query if you like.
###
### Output columns: Id, DisplayName, Num_Posts, Num_Badges
### Order by Id ascending
queries[7] = """
with temp1 as (
        select owneruserid, count(*) as num_posts
        from posts
        group by owneruserid),
temp2 as (
        select userid, count(*) as num_badges
        from badges
        group by userid)
select users.id, users.displayname as DisplayName, coalesce(num_posts, 0) as num_posts, coalesce(num_badges, 0) as num_badges
from users left outer join temp1 on (users.id = temp1.owneruserid) left outer join temp2 on (users.id = temp2.userid)
where users.id < 100
order by users.id asc;
"""

### 8. List the users who have made a post in 2009.
### Hint: Use "in".
###
### Output Columns: Id, DisplayName
### Order by Id ascending
queries[8] = """
select id, displayname
from users where id in (select owneruserid from posts where extract(year from creationdate) = 2009)
order by id asc;
"""

### 9. Find the users who have made a post in 2009 (between 1/1/2009 and 12/31/2009)
### and have received a badge in 2011 (between 1/1/2011 and 12/31/2011).
### Hint: Use "intersect" and "in".
###
### Output Columns: Id, DisplayName
### Order by Id ascending
queries[9] = """
select id, displayname
from users where id in (select owneruserid from posts where extract(year from creationdate) = 2009)
intersect
select id, displayname
from users where id in (select userid from badges
where extract(year from date) = 2011)
order by id asc;
"""

### 10. Write a query to output a list of posts with comments, such that PostType = 'Moderator nomination' 
### and the comment has score of at least 10. So there may be multiple rows with the same post
### in the output.
###
### This query requires joining three tables: Posts, Comments, and PostTypes.
###
### Output: Id (Posts), Title, Text (Comments)
### Order by: Id ascending
queries[10] = """
select posts.id, title, comments.text
from posts, comments, posttypes
where posts.id = comments.postid and posts.posttypeid = posttypes.posttypeid and posttypes.description = 'Moderator nomination' and comments.score >= 10
order by posts.id asc;
"""


### 11. For the users who have received at least 200 badges in total, find the
### number of badges they have received in each year. This can be used, e.g., to 
### create a plot of the number of badges received in each year for the most active users.
###
### There should be an entry for a user for every year in which badges were given out.
###
### We have provided some WITH clauses to help you get started. You may wish to 
### add more (or modify these).
###
### Output columns: Id, DisplayName, Year, Num_Badges
### Order by Id ascending, Year ascending
queries[11] = """
with years as (
        select distinct extract(year from date) as year 
        from badges),
     temp1 as (
        select id, displayname, year
        from users, years
        where id in (select userid from badges group by userid having count(*) >= 200)
     )
select temp1.id, displayname, year, count(badges.id) as num_badges
from temp1 left outer join badges on temp1.id = badges.userid and extract(year from date) = temp1.year
group by temp1.id, displayname, year
order by id asc, year asc;
"""

### 12. Find the post(s) that took the longest to answer, i.e., the gap between its creation date
### and the creation date of the first answer to it (in number of days). Ignore the posts with no
### answers. Keep in mind that "AcceptedAnswerId" is the id of the post that was marked
### as the answer to the question -- joining on "parentid" is not the correct way to find the answer.
###
### Hint: Use with to create an appropriate table first.
###
### Output columns: Id, Title, Gap
queries[12] = """
with temp as (
        select p1.id, p1.title, (p2.creationdate - p1.creationdate) as gap
        from posts p1 join posts p2 on p1.acceptedanswerid = p2.id
        )
select *
from temp
where gap = (select max(gap) from temp);
"""


### 13. Write a query to find the posts with at least 7 children, i.e., at
### least 7 other posts have that post as the parent
###
### Output columns: Id, Title
### Order by: Id ascending
queries[13] = """
select p1.id, p1.title
from posts p1 join posts p2 on p1.id = p2.parentid
group by p1.id
having count(*) >= 7
order by p1.id asc;
"""

### 14. Find posts such that, between the post and its children (i.e., answers
### to that post), there are a total of 100 or more votes
###
### HINT: Use "union all" to create an appropriate temp table using WITH
###
### Output columns: Id, Title
### Order by: Id ascending
queries[14] = """
with temp as (
        select posts.id, count(*) as num_votes
        from posts join votes on posts.id = votes.postid
        group by posts.id
        union all
        select p1.id, count(*) as num_votes
        from posts p1 join posts p2 on p1.id = p2.parentid join votes on p2.id = votes.postid
        group by p1.id
        )
select posts.id, posts.title 
from posts join temp on posts.id = temp.id 
group by posts.id, posts.title
having sum(num_votes) >= 100
order by id asc;
"""

### 15. Let's see if there is a correlation between the length of a post and the score it gets.
### We don't have posts in the database, so we will do this on title instead.
### Write a query to find the average score of posts for each of the following ranges of post title length:
### 0-9 (inclusive), 10-19, ...
###
### We will ignore the posts with no title.
###
### HINT: Use the "floor" function to create the ranges.
###
### Output columns: Range_Start, Range_End, Avg_Score
### Order by: Range ascending
queries[15] = """
with temp as (
        select floor(length(title)/10)*10 as range_start, floor(length(title)/10)*10 + 9 as range_end, avg(score) as avg_score
        from posts
        where title != '' and title is not null
        group by range_start, range_end
        )
select * from temp
order by range_start;
"""


### 16. Write a query to generate a table: 
### (VoteTypeDescription, Day_of_Week, Num_Votes)
### where we count the number of votes corresponding to each combination
### of vote type and Day_of_Week (obtained by extract "dow" on CreationDate).
### So Day_of_Week will take values from 0 to 6 (Sunday to Saturday resp.)
###
### Don't worry if a particular combination of Description and Day of Week has 
### no votes -- there should be no row in the output for that combination.
###
### Output column order: VoteTypeDescription, Day_of_Week, Num_Votes
### Order by VoteTypeDescription asc, Day_of_Week asc
queries[16] = """
select description as votetypedescription, extract(dow from creationdate) as day_of_week, count(*) as num_votes
from votes join votetypes on votes.votetypeid = votetypes.votetypeid
group by votetypedescription, day_of_week
order by votetypedescription asc, day_of_week asc;
"""

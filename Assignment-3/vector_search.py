import spacy
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import psycopg2

# Example code showing how to use spaCy to generate a vector for a string
def example_code():
    # Load the spaCy model
    nlp = spacy.load("en_core_web_sm")

    phrases = ["Hello, world!", "Welcome to spaCy.", "This is an NLP library.", "Embedding phrases with spaCy."]

    for p in phrases:
        n = nlp(p)
        print("Vector for {} is:".format(p))
        print(n.vector) # this gives you the vector for the entire string

# Complete this code to find the top k closest titles to q using vector search
# Use psycopg2 to retrieve the relevant data from the database 
#
# The return format is shown with an example
#
# Note: do not put anything outside this function ... e.g., spacy model should be loaded inside it
# We will be import this function and test it using another python program
#
def find_topk(q, k):
    nlp = spacy.load("en_core_web_sm")
    q_vector = nlp(q).vector
    conn = psycopg2.connect("host=127.0.0.1 dbname=stackexchange user=root password=root")
    curr = conn.cursor()

    curr.execute("select id, title from posts")
    ans = curr.fetchall()
    result = []
    for row in ans:
        post_id, title = row[0], row[1]
        if title is not None:
            vector = nlp(title).vector
            cosine_sim = cosine_similarity([q_vector], [vector])[0][0]
            result.append((post_id, title, cosine_sim))
    result.sort(key=lambda x: x[2], reverse=True)

    return [(post[0], post[1]) for post in result[:k]]

if __name__ == '__main__':
    # comment this out once you have confirmed it works 
   # example_code()

    print(find_topk('what is the best relational database?', 5))

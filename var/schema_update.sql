DROP TABLE if EXISTS posts;

CREATE TABLE posts (
  post_id TEXT UNIQUE,
  related_subreddit_id TEXT,
  related_subreddit_name TEXT,
  related_user_id TEXT,
  post_type TEXT,
  post_title TEXT,
  url_friendly_title TEXT,
  post_link TEXT,
  post_textarea TEXT,
  post_timestamp TEXT,
  post_votes TEXT,
  upvoted_by_user TEXT,
  downvoted_by_user TEXT
);

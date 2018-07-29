from urllib.request import urlopen
import json
from datetime import datetime
from collections import defaultdict
import pandas as pd

def get_recent_article(result=[],article_id=None,sort_key=None,date_span=7):
    # api url
    if not(article_id) and not(sort_key):
        article_api   = "https://alis.to/api/articles/recent?limit=100"
    else:
        article_api   = "https://alis.to/api/articles/recent?limit=100&article_id=%s&sort_key=%s" % (article_id,sort_key)
    # データ取得
    raw_article_data  = urlopen(article_api).read().decode("utf-8")
    json_article_data = json.loads(raw_article_data)
    articles_data     = json_article_data["Items"]
    result.extend(articles_data)
    # ループ終了のチェック
    today             = datetime.now()
    last_data_date    = datetime.fromtimestamp(int(result[-1]["published_at"]))
    if (today-last_data_date).days >= (date_span+1):
        # ループ終了
        return result
    else:
        # ループ継続
        # 次のデータ取得用パラメータ
        LastEvaluatedKey  = json_article_data["LastEvaluatedKey"]
        article_id        = LastEvaluatedKey["article_id"]
        sort_key          = LastEvaluatedKey["sort_key"]
        return get_recent_article(result,article_id,sort_key,date_span=date_span)

def get_like_count(article_id):
    likes_api      = "https://alis.to/api/articles/%s/likes"
    raw_like_data  = urlopen(likes_api % article_id).read().decode("utf-8")
    json_like_data = json.loads(raw_like_data)
    like_count     = json_like_data["count"]
    return like_count

def get_user_name(user_id):
    user_api      = "https://alis.to/api/users/%s/info"
    raw_user_data = urlopen(user_api % user_id).read().decode("utf-8")
    user_data     = json.loads(raw_user_data)
    name          = user_data["user_display_name"]
    return name

def make_data(articles):
    data = []
    for article in articles:
        title      = article["title"]
        user_id    = article["user_id"]
        article_id = article["article_id"]
        user_name  = get_user_name(user_id)
        like_count = get_like_count(article_id)
        date       = datetime.fromtimestamp(int(article["published_at"]))
        url        = "https://alis.to/%s/articles/%s" % (user_id,article_id)
        data.append([title,url,user_name,like_count,date])
    return data

def make_rankig(data):
    ranking = pd.DataFrame(data,columns=["title","url","autehr","like","date"])
    not_old = ranking["date"].map(lambda x:x.day) != ranking["date"].min().day
    not_new = ranking["date"].map(lambda x:x.day) != ranking["date"].max().day
    ranking = ranking[not_old & not_new]
    ranking = ranking.sort_values("like",ascending=False)
    ranking = ranking.reset_index(drop=True)
    ranking.index += 1
    return ranking


def get_ranking(date_span=7):
    articles = get_recent_article(date_span=date_span)
    data     = make_data(articles)
    ranking  = make_rankig(data)
    return ranking

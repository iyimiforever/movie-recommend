import os
import random

from create_item_item_mat import Ready
import pandas as pd
import numpy as np

class Recommend(object):
    def __init__(self):
        # 加载电影与电影的相关性信息
        self.item_item_mat=pd.read_csv('item_item_mat.csv',
                                       header=0,
                                       index_col=0,
                                       sep=r',\s*',
                                       engine='python',
                                       encoding='utf-8')
        # 加载用户电影评分  movie_id    user_id  score
        self.user_score=pd.read_csv('u_score.csv',
                                    names=['movie_id', 'user_id', 'score'],
                                    usecols=(0,1,2),
                                    engine='python',
                                    encoding='utf-8')

    def first_recommend(self):
        movies=self.user_score[self.user_score['score']==5]['movie_id'].ravel()
        movies=list(set(movies))
        result=random.sample(movies, 10)
        # print(result)
        return result


    def item_item_recommend(self,user_id):
        total_movie_list=self.item_item_mat.index
        user_score=np.array(self.user_score)
        movie_array=user_score[user_score[:,1]==user_id]
        # print(movie_array)
        movie_array=np.delete(movie_array,1,axis=1)  # 删除用户列
        target_movie_dict={}
        if not movie_array.tolist():
            return self.first_recommend()
        else:
            for movie, score in movie_array:
                for new_movie in total_movie_list:
                    if new_movie in target_movie_dict:
                        if target_movie_dict[new_movie] >= self.item_item_mat[str(movie)][new_movie]*score:
                            continue
                        target_movie_dict[new_movie]=self.item_item_mat[str(movie)][new_movie]*score
                    else:
                        if movie!=new_movie:
                            target_movie_dict[new_movie] = self.item_item_mat[str(movie)][new_movie] * score
        for movie,score in movie_array:
            if movie in target_movie_dict:
                target_movie_dict.pop(movie)
        target_movie_dict_order=sorted(target_movie_dict.items(),key=lambda x:x[1],reverse=True)[:10]
        result=[x[0] for x in target_movie_dict_order]
        print(result)
        return result


if __name__ == '__main__':
    if not os.path.exists('item_item_mat.csv'):
        ready=Ready()
    r=Recommend()
    # r.item_item_recommend('130012755')
    r.first_recommend()
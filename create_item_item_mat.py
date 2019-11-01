"""
准备
item-item矩阵
item-user矩阵
"""

import numpy as np
import pandas as pd
import time


class Ready(object):
    def __init__(self):
        self.movie_data=self.load_movie_data()
        self.user_score=self.load_user_score()
        self.user_item_mat=self.init_user_item_mat()
        self.item_ids=self.user_item_mat.columns
        self.unique_movie_vec_columns=self.get_unique_movie_vec_columns()
        self.item_item_mat = self.init_item_item_simmat()
        self.merge_finally()

    def load_movie_data(self):
        """加载电影基本信息"""
        data=pd.read_csv('m_all_info.csv',
                         names=['movie_id', 'title', 'director', 'scriptwriter', 'actors', 'genres', 'place', 'languages', 'time', 'duration', 'other_names', '_'],
                         sep=r',\s*',
                         engine='python',
                         encoding='utf-8')
        return data


    def load_user_score(self):
        """加载用户电影评分"""
        data=pd.read_csv('u_score.csv',
                         names=['movie_id', 'user_id', 'score'],
                         usecols=(0,1,2),
                         engine='python',
                         encoding='utf-8')
        return data


    def init_user_item_mat(self):
        """
        初始化user对item的评分矩阵，并储存
        """
        unique_movie_id=self.movie_data['movie_id'].unique()  # ndarray
        unique_user_id=self.user_score['user_id'].unique()  # ndarray
        user_item_mat=pd.DataFrame(0,index=unique_user_id,columns=unique_movie_id)
        for i in range(len(self.user_score)):
            movie_id,user_id,score=self.user_score.iloc[i]
            try:
                user_item_mat[movie_id][user_id]=score
            except:
                pass
        user_item_mat.to_csv('user_item_mat.csv',encoding='utf-8')
        return user_item_mat

    def get_unique_movie_vec_columns(self):
        # 整理用于描述电影的特征向量字段名列表，并存储
        # 不重复的导演
        director_series=self.movie_data['director']
        directors=[]
        for names in director_series.values:
            directors+=names.split(' / ')
        unique_directors = pd.Series(directors).unique()
        # 不重复的演员
        actor_series = self.movie_data['actors']
        actors = []
        for names in actor_series.values:
            actors = actors + names.split(' / ')
        unique_actors = pd.Series(actors).unique()
        # 不重复的电影类型
        genres_series = self.movie_data['genres']
        genres = []
        for names in genres_series.values:
            genres = genres + names.split(' / ')
        unique_genres = pd.Series(genres).unique()
        # 不重复的语言
        languages_series = self.movie_data['languages']
        languages = []
        for names in languages_series.values:
            languages = languages + names.split(' / ')
        unique_languages = pd.Series(languages).unique()

        movie_vec_columns=np.hstack((unique_directors, unique_actors, unique_genres, unique_languages))
        # user item的id可能会重复，去重
        unique_movie_vec_columns=pd.Series(movie_vec_columns).unique()
        return unique_movie_vec_columns

    def init_vec_by_item_id(self,movie_id):
        """
        返回itemId电影的特征向量
        导演       演员              电影类型         语言
        000001000 0000000101010111 00111011001110  101110
        """
        movie=self.movie_data[self.movie_data['movie_id']==movie_id][:1]
        # 整理用于描述电影的特征向量
        vec = np.zeros(len(self.unique_movie_vec_columns), dtype='i4')
        features=[]
        # [a,b,[c,d]] -> [a,b,c,d]
        for val in movie.values.ravel():
            features+=str(val).split(' / ')
        vec[pd.Index(pd.unique(features)).get_indexer(self.unique_movie_vec_columns) >= 0] = 1
        return vec

    def init_item_item_simmat(self):
        """
        通过导演、演员、电影类型、语言、时间整理item与item的相似度矩阵
        """
        item_item_simmat = pd.DataFrame(0, index=self.item_ids, columns=self.item_ids, dtype='f8')
        for i,itemA in enumerate(self.item_ids):
            vecA=self.init_vec_by_item_id(itemA)
            col=pd.Series(0,index=self.item_ids,dtype='f8')
            for itemB in self.item_ids[i:]:
                vecB = self.init_vec_by_item_id(itemB)
                # 计算两部电影向量的欧式距离
                sim_score = 1 / (1 + np.sqrt(((vecA - vecB) ** 2)).sum())
                col.loc[itemB] = sim_score
            item_item_simmat[itemA]=col
            print('完成%d条信息处理'%(i+1))
            item_item_simmat.to_csv('my_work.csv')
        return item_item_simmat

    def merge_finally(self):
        A = pd.read_csv('my_work.csv', delimiter=',', index_col=0)
        B = A.T
        A = np.array(A)
        B = np.array(B)
        data = A + B
        data = pd.DataFrame(data, index=self.item_ids, columns=self.item_ids)
        data.to_csv('item_item_mat.csv', encoding='utf-8')

if __name__ == '__main__':
    print('creating item_item_mat ...')
    a=time.time()
    ready=Ready()
    print('create item_item_mat lasting %d seconds'% (time.time()-a))
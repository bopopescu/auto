# -*- coding: utf-8 -*-

# @Time    : 2018/5/9 17:03
# @Author  : songq001
# @Comment :

import numpy as np
import pandas as pd

df = pd.DataFrame({"id":[1001,1002,1003,1004,1005,1006],
 "date":pd.date_range('20130102', periods=6),
  "city":['Beijing ', 'SH', ' guangzhou ', 'Shenzhen', 'shanghai', 'BEIJING '],
 "age":[23,44,54,32,34,32],
 "category":['100-A','100-B','110-A','110-C','210-A','130-F'],
  "price":[1200,np.nan,2133,5433,np.nan,4432]},
  columns =['id','date','city','category','age','price'],
  # index=['a', 'b', 'c', 'd', 'e', 'f']
                  )

print df

# 创建DataFrame对象
df1 = pd.DataFrame([1, 2, 3, 4, 5], columns=['cols1'], index=['a','b','c','d','e'])
print df1

# 创建DataFrame对象
df2 = pd.DataFrame([['Alex', 10], ['Bob', 12], ['Clarke', 13]], columns=['cols1', 'cols2'], index=['a', 'b', 'c'])
print df2



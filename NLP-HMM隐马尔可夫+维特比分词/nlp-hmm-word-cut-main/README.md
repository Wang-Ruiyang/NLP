# 代码解析

## 代码1

```py
def text_to_state(file="all_train_text.txt"):
    # ...
	all_data = open(file, "r", encoding="utf-8").read().split("\n") 
    # ...
    for d_index, data in tqdm(enumerate(all_data)):
    # ...
    for w in data.split(" "):
    # ...
    
```

### 测试代码1

`open()`返回的是文件的指针地址，`.read()`返回的是字符串，`.split()`返回的是列表，列表后接`[]`表示切片操作

```py
all_data = open("all_train_text.txt", "r", encoding="utf-8")
```

![image-20220915113103482](pic/image-20220915113103482.png)

```py
all_data = open("all_train_text.txt", "r", encoding="utf-8").read()
```

![image-20220915113132572](pic/image-20220915113132572.png)

```py
all_data = open("all_train_text.txt", "r", encoding="utf-8").read().split("\n")
```

![image-20220915113159259](pic/image-20220915113159259.png)

```py
print(type(all_data))
```

![image-20220915113259227](pic/image-20220915113259227.png)

### 测试代码2

`enumerate()`函数用于将一个可遍历的数据对象（如列表、元组或字符串）组合为一个索引序列，同时列出数据和数据下标，一般用在 for 循环当中。

```py
seasons = ['Spring', 'Summer', 'Fall', 'Winter']
print(list(enumerate(seasons)))    
#输出：[(0, 'Spring'), (1, 'Summer'), (2, 'Fall'), (3, 'Winter')]
print(list(enumerate(seasons, start=1)))  
#输出：[(1, 'Spring'), (2, 'Summer'), (3, 'Fall'), (4, 'Winter')]
```

```py
print(list(enumerate(all_data)))
```

![image-20220915114134514](pic/image-20220915114134514.png)

### 测试代码3

`split()`通过指定分隔符对字符串进行切片，如果参数 num 有指定值，则分隔 num+1 个子字符串

```py
str = "Line1-abcdef \nLine2-abc \nLine4-abcd";
print str.split( );       # 以空格为分隔符，包含 \n
# ['Line1-abcdef', 'Line2-abc', 'Line4-abcd']
print str.split(' ', 1 ); # 以空格为分隔符，分隔成两个
# ['Line1-abcdef', '\nLine2-abc \nLine4-abcd']
```

## 代码2

```py
def cal_transfer_matrix(self, states):
    # ...
    for s1, s2 in zip(sta1, sta2):   # 同时遍历 s1,s2，zip()将sta1和sta2每对字符组合
    # ...
```

### 测试代码1

`zip()`函数用于将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，然后返回由这些元组组成的列表。

```py
a = [1,2,3]
c = [4,5,6,7,8]
zip(a,c)         # 元素个数与最短的列表一致，输出[(1, 4), (2, 5), (3, 6)]
zip(*zip(a,c))   # 与 zip 相反，*zip(a,c)可理解为解压，返回二维矩阵式，输出[(1, 2, 3), (4, 5, 6)]
```

## 代码3

```py
def cal_emit_matrix(self, words, states):
    # ...
        self.emit_matrix[state][word] = self.emit_matrix[state].get(word,0) + 1
    # ...
```

### 测试代码1

`get()` 函数返回指定键的值。`dict.get(key[, value]) `

- key -- 字典中要查找的键。
- value -- 可选，如果指定键的值不存在时，返回该默认值。

## 代码4

```py
def normalize(self):
    # ...
    self.transfer_matrix = self.transfer_matrix/np.sum(self.transfer_matrix,axis = 1,keepdims = True)
    self.emit_matrix = {state:{word:t/word_times["total"]*1000 for word,t in word_times.items() if word != "total"} for state,word_times in self.emit_matrix.items()}
```

### 测试代码1

```py
numpy.sum(a, [axis]=None, dtype=None, out=None, keepdims=np._NoValue)
```

- `a`是要进行加法运算的向量/数组/矩阵

- `axis`的值可以为None，也可以为整数和元组

  1. `axis=None`（默认）：即将数组/矩阵中的元素全部加起来，得到一个和。

  2. `axis=0`，即将每一列的元素相加，是压缩行，将矩阵压缩为一行。
     `axis=1`，即将每一行的元素相加，是压缩列，将矩阵压缩为一列。

  3. ……

  4. 当axis取负数的时候，对于二维矩阵，只能取-1和-2（不可超过矩阵的维度）。

     当`axis=-1`时，相当于`axis=1`的效果；

     当`axis=-2`时，相当于`axis=0`的效果。

- `keepdims = True`参数是为了保持结果的维度与原始array相同

### 测试代码2

典型的**列表表达式**

```py
self.emit_matrix = {state:{word:t/word_times["total"]*1000 for word,t in word_times.items() if word != "total"} for state,word_times in self.emit_matrix.items()}
```

可以分解为：

```py
for state, word_times in self.emit_matrix.items():
    for word, t in word_times.items():
        if word != "total":
            result = t / word_times["total"] * 1000
            self.emit_matrix[state][word] = result
```








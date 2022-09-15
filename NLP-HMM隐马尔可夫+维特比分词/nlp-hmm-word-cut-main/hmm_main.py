import pickle
from tqdm import tqdm        #进度条库
import numpy as np
import os

# 根据语料库all_train_text的每一词语填充all_train_state的标识
def make_label(text_str):    # 从单词到label的转换, 如: 今天 ----> BE  麻辣肥牛: ---> BMME  的 ---> S
    text_len = len(text_str)
    if text_len == 1:        # 对单个字符，直接设置为s
        return "S"
    return "B" + "M" * (text_len - 2) + "E"  # 除了开头是 B, 结尾是 E，中间都是Ｍ

# 填充all_train_state的主要函数
def text_to_state(file="all_train_text.txt"):  # 将原始的语料库转换为 对应的状态文件
    if os.path.exists("all_train_state.txt"):  # 如果存在该文件, 就直接退出（因为在本代码中，创建完后直接就会对其进行填充，因此如果有此文件，则一定是有内容的）
        return

    # 如果没有此文件
    all_data = open(file, "r", encoding="utf-8").read().split("\n")  # 打开all_train_text.txt文件并按行切分到  all_data 中 , all_data  是一个list

    with open("all_train_state.txt", "w", encoding="utf-8") as f:    #  打开写入的文件
        for d_index, data in tqdm(enumerate(all_data)):              # 逐行 遍历 , tqdm 是进度条提示 , data 是一篇文章, 有可能为空
            # 每次传入的data是一句话
            if data:                                                 #  如果 data 不为空
                state_ = ""
                for w in data.split(" "):                            # 当前 文章按照空格切分, w是文章中的一个词语
                    if w:                                            # 如果 w 不为空
                        state_ = state_ + make_label(w) + " "        # 制作单个词语的label
                if d_index != len(all_data) - 1:                     # 用d_index定位当前句子是不是最后一句
                    state_ = state_.strip() + "\n"                   # 每一行都去掉 最后的空格，除了最后一行其他行都加 "\n"
                f.write(state_)                                      # 将字符串写入文件，因为有\n，所以会自动换行


# 定义 HMM类, 其实最关键的就是三大矩阵
class HMM:
    def __init__(self,file_text = "all_train_text.txt",file_state = "all_train_state.txt"):
        self.all_states = open(file_state, "r", encoding="utf-8").read().split("\n")[:200]   # 以\n为分割，按行获取所有的状态，[:200]表示对split生成的列表进行切片
        self.all_texts = open(file_text, "r", encoding="utf-8").read().split("\n")[:200]     # 按行获取所有的文本
        self.states_to_index = {"B": 0, "M": 1, "S": 2, "E": 3}                        # 给每个状态定义一个索引, 以后可以根据状态获取索引
        self.index_to_states = ["B", "M", "S", "E"]                                    # 根据索引获取对应状态
        self.len_states = len(self.states_to_index)                                    # 状态长度 : 这里是4


        # 最重要的三行代码
        self.init_matrix = np.zeros((self.len_states))                                 # 初始矩阵 : 1 * 4 , 对应的是 BMSE
        self.transfer_matrix = np.zeros((self.len_states, self.len_states))            # BMSE共四种状态，因此转移状态矩阵:  4 * 4 ,

        # 发射矩阵, 使用的 2级 字典嵌套
        # # 注意这里初始化了一个  total 键 , 存储当前状态出现的总次数, 为了后面的归一化使用
        self.emit_matrix = {"B":{"total":0}, "M":{"total":0}, "S":{"total":0}, "E":{"total":0}}     #双重字典，可以用矩阵实现。注意每个状态都设置了一个total键,存储当前状态出现的总次数,为了后面的归一化使用

    # 计算 初始矩阵（计算每行的第一个字是什么状态）
    def cal_init_matrix(self, state):
        # init_matrix 初始矩阵: 1 * 4, 对应的是 BMSE（事实上M和E对应的不可能有值，如果有，代码有问题）
        self.init_matrix[self.states_to_index[state[0]]] += 1  #state[0]表示是每一行文字的第一个字，states_to_index[]表示通过第一个字所对于的BMSE，在初始矩阵中对于位置+1

    # 计算转移矩阵（当前状态到下一状态的概率，看每相邻的两个字符之间的状态变化）
    def cal_transfer_matrix(self, states):
        # transfer_matrix，转移状态矩阵:4 * 4
        sta_join = "".join(states)        # 状态转移 从当前状态转移到后一状态, 即 从 sta1 每一元素转移到 sta2 中
        sta1 = sta_join[:-1]    #选取一行文字的全部内容
        sta2 = sta_join[1:]     #选取一行文字的第二个字符开始的全部内容
        for s1, s2 in zip(sta1, sta2):   # 同时遍历 s1,s2，zip()将sta1和sta2每对字符组合
            self.transfer_matrix[self.states_to_index[s1],self.states_to_index[s2]] += 1

    # 计算发射矩阵（统计某种状态下，所有字出现的次数（概率））
    def cal_emit_matrix(self, words, states):
        for word, state in zip("".join(words), "".join(states)):  #将words列表和states列表各拼接为字符串，再将对应的字符对应（及字符与状态之间的对应）
            self.emit_matrix[state][word] = self.emit_matrix[state].get(word,0) + 1   #对于BMSE四种状态而言，用get方法搜索word出现的次数再+1；如果没有则输入0再+1。
            self.emit_matrix[state]["total"] += 1         #将总出现次数total+1

    # 将矩阵归一化（将矩阵中的次数转为出现的概率）
    def normalize(self):
        self.init_matrix = self.init_matrix/np.sum(self.init_matrix)     #axis=None时，np.sum即为求出整个矩阵的和
        self.transfer_matrix = self.transfer_matrix/np.sum(self.transfer_matrix,axis = 1,keepdims = True)     #原矩阵表示行标->列标的次数，因此每一行的概率和应该为1
        self.emit_matrix = {state:{word:t/word_times["total"]*1000 for word,t in word_times.items() if word != "total"} for state,word_times in self.emit_matrix.items()}
        # for state, word_times in self.emit_matrix.items():
        #         for word, t in word_times.items():
        #             if word != "total":
        #                 result = t / word_times["total"] * 1000
        #                 self.emit_matrix[state][word] = result

    # 训练开始, 其实就是3个矩阵的求解过程
    def train(self):
        if os.path.exists("three_matrix.pkl"):  # 如果已经存在参数了 就不训练了
                self.init_matrix, self.transfer_matrix, self.emit_matrix =  pickle.load(open("three_matrix.pkl","rb"))    #pickle.load()用于将二进制对象文件转换成 Python 对象
                return
        # 如果不存在 three_matrix.pkl
        # 按行读取文件, 调用3个矩阵的求解函数。
        for words, states in tqdm(zip(self.all_texts, self.all_states)):  # zip()函数用于将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，然后返回由这些元组组成的列表。
            words = words.split(" ")            # 在文件中 都是按照空格切分的
            states = states.split(" ")

            self.cal_init_matrix(states[0])     # 计算三大矩阵
            self.cal_transfer_matrix(states)
            self.cal_emit_matrix(words, states)
        self.normalize()      # 矩阵求完之后进行归一化
        pickle.dump([self.init_matrix, self.transfer_matrix, self.emit_matrix], open("three_matrix.pkl", "wb")) # 保存参数，方便以后使用，pickle.dump()用于将二进制对象文件转换成Python对象，open("three_matrix.pkl", "wb")返回的是文件的f

# 预测
def viterbi_t(text, hmm):
    states = hmm.index_to_states     #四种状态
    emit_p = hmm.emit_matrix         #发射矩阵
    trans_p = hmm.transfer_matrix    #状态转移矩阵
    start_p = hmm.init_matrix        #初始矩阵
    V = [{}]     #到当前字符的四个状态的最大概率
    path = {}
    # 设置开头
    for y in states:
        # hmm.states_to_index[y]表示y状态对应的下标，start_p[]表示再y状态下作为一行开头的概率；emit_p[y]表示由y状态转移出去的那一行，.get(text[0], 0)表示搜索传入文本第一个字的概率，如果没有就设置为0
        V[0][y] = start_p[hmm.states_to_index[y]] * emit_p[y].get(text[0], 0)
        path[y] = [y]
    # 填充正文内容
    for t in range(1, len(text)):
        V.append({})
        newpath = {}

        # 检验训练的发射概率矩阵中是否有该字，结果为true或false
        neverSeen = text[t] not in emit_p['S'].keys() and \
                    text[t] not in emit_p['M'].keys() and \
                    text[t] not in emit_p['E'].keys() and \
                    text[t] not in emit_p['B'].keys()
        for y in states:
            emitP = emit_p[y].get(text[t], 0) if not neverSeen else 1.0  # 如果文字再发射矩阵中，那么get出来，反之，赋值1。设置未知字单独成词
            temp = []
            for y0 in states:    #当前字的四个状态
                if V[t - 1][y0] > 0:
                    temp.append((V[t - 1][y0] * trans_p[hmm.states_to_index[y0],hmm.states_to_index[y]] * emitP, y0))
            (prob, state) = max(temp)
            # (prob, state) = max([(V[t - 1][y0] * trans_p[hmm.states_to_index[y0],hmm.states_to_index[y]] * emitP, y0)  for y0 in states if V[t - 1][y0] > 0])
            V[t][y] = prob
            newpath[y] = path[state] + [y]
        path = newpath


    (prob, state) = max([(V[len(text) - 1][y], y) for y in states])  # 求最大概念的路径

    result = "" # 拼接结果
    for t,s in zip(text,path[state]):
        result += t
        if s == "S" or s == "E" :  # 如果是 S 或者 E 就在后面添加空格
            result += " "
    return result


if __name__ == "__main__":
    text_to_state()
    text = "虽然一路上队伍里肃静无声"

    hmm = HMM()
    hmm.train()
    result = viterbi_t(text,hmm)

    print(result)





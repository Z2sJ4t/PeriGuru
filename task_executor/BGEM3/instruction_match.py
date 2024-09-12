import json
import heapq
import numpy as np

from FlagEmbedding import BGEM3FlagModel

SAME_APP_FACTOR = 1.25

class InsMatch:
    def __init__(self, dict_path='./asset/instruction_dict/dict.json'):
        self.model = BGEM3FlagModel('./third_party/bge-m3',  
                use_fp16=True)
        self.batch_size = 12
        self.max_length = 128
        #self.threshold = 0.8
        
        with open(dict_path, 'r') as file:
            self.origin_dict = json.load(file)
        self.vec_dict = {}
        self.build_vec_dict()

    def build_vec_dict(self):
        for key, value in self.origin_dict.items():
            sentences = []
            for instr in value:
                sentences.append(instr['instruction'])
            self.vec_dict[key] = self.model.encode(sentences, 
                batch_size=self.batch_size, 
                max_length=self.max_length)['dense_vecs'].T

    def K_similar(self, instr, APPname, K=1, same_APP_only=False):
        instr_embedding = self.model.encode([instr],
            batch_size=self.batch_size, 
            max_length=self.max_length)['dense_vecs']

        res = []
        
        # Prioritize searching within the same APP
        if(APPname in self.vec_dict):
            dist = instr_embedding @ self.vec_dict[APPname]
            for i, value in enumerate(dist[0]):
                if(len(res) < K):
                    # heapq use the first element of tuple as key
                    heapq.heappush(res, (-value * SAME_APP_FACTOR, 
                        self.origin_dict[APPname][i]['file']))
                elif(value * SAME_APP_FACTOR > -res[0][0]):
                    heapq.heappop(res)
                    heapq.heappush(res, (-value * SAME_APP_FACTOR, 
                        self.origin_dict[APPname][i]['file']))

        if(same_APP_only):
            return [r[1] for r in res]

        # Other similar instructions
        for key, value in self.vec_dict.items():
            if(key == APPname):
                continue
            dist = np.array(instr_embedding @ value)
            max_value = np.max(dist)
            max_idx = np.argmax(dist)
            if(len(res) < K):
                heapq.heappush(res, (-max_value, self.origin_dict[key][max_idx]['file']))
            elif(max_value > -res[0][0]):
                heapq.heappop(res)
                heapq.heappush(res, (-max_value, self.origin_dict[key][max_idx]['file']))

        return [r[1] for r in res]
LINE1 = 0.227160
LINE2 = 0.4
LINE3 = 0.572839
LINE4 = 0.745679

LINE1_st = 0.052892
LINE2_st = 0.105785
LINE3_st = 0.201653

INTER = 0.099173

def keyboard_calc_char(c):
    if(c == ' '):
        return True, 0.537190, LINE4
    line1_char = 'qwertyuiop'
    index = line1_char.find(c)
    if(index != -1):
        return True, LINE1_st + INTER * index, LINE1
    line2_char = 'asdfghjkl'
    index = line2_char.find(c)
    if(index != -1):
        return True, LINE2_st + INTER * index, LINE2
    line3_char = 'zxcvbnm'
    index = line3_char.find(c)
    if(index != -1):
        return True, LINE3_st + INTER * index, LINE3

    return False, -1, -1

def keyboard_calc_enter():
    return 0.925620, LINE4
import random
import numpy as np
import math

## BIG DATA
P = 870044  # 人口
H = 359673  # 家庭數
W = 34671   # 工作地點
E = 673488  # 工作人口
N = 100598  # 非工作地點
P_E = 196556# 非工作人口

## SMALL DATA
# P = 870  # 人口
# H = 359  # 家庭數
# W = 34   # 工作地點
# E = 674  # 工作人口
# N = 100  # 非工作地點
# P_E = 196# 非工作人口


X = 999 # 房子的Max X
Y = 999 # 房子的Max Y

house_info = { house_id : {'x':0 , 'y':0, 'persons':[], 'reside':False } for house_id in range(H)}
work_info = { work_id : { 'persons':[] } for work_id in range(W)}
not_work_info = { not_work_id : { 'persons':[]} for not_work_id in range(N)}
person_info = { person_id : {'h_id':-1,
                             'work':False,
                             'work_id': -1,
                             'not_work_id':-1
                            } for person_id in range(P)}

def init_house_location():
    # init the house location
    print("Init the house location.")
    grid_x = X
    grid_y = Y
    for h_id in range(H):
        # random x & y
        x = random.randint(0, grid_x )
        y = random.randint(0, grid_y )
        # assign value
        house_info[h_id]['x'] = x
        house_info[h_id]['y'] = y


def assign_person():
    print("Assign person.")
    count_e = E
    not_reside = [house_id for house_id in range(H)]
    for p_id in range(P):
        if p_id % 2000 == 0:
            print('{}/{}'.format(p_id,P))
        # find the null house
        if len(not_reside) > 0 :
            # random house_id
            h_id = random.choice(not_reside)
            # assign person in house
            house_info[h_id]['persons'].append(p_id)
            # modify reside = True
            house_info[h_id]['reside'] = True
            # assign house_id to person
            person_info[p_id]['h_id'] = h_id
            # pop the h_id
            not_reside.remove(h_id)
        else:
            h_id = random.randint(0, H - 1)
            house_info[h_id]['persons'].append(p_id)
            person_info[p_id]['h_id'] = h_id



        # determine work or not
        work_prob = random.randint(1,100)

        # work
        if work_prob >50:
            # check E
            if count_e > 0 :
                person_info[p_id]['work'] = True
                # minus 1 from E
                count_e -= 1
                # assign person in work location
                w_id = random.randint(0, W - 1)
                work_info[w_id]['persons'].append(p_id)
                # assign work id to person
                person_info[p_id]['work_id'] = w_id

        # not work
        if person_info[p_id]['work'] == False :
            # assign person in not work location
            nw_id = random.randint(0, N - 1)
            not_work_info[nw_id]['persons'].append(p_id)
            #assign not work id to person
            person_info[p_id]['not_work_id'] = nw_id


def generate_graph():
    T = [1,10]
    ##----Node----##
    R = 0.55
    CT = 0.57
    S = 0.13
    CR = 0.02
    HI = 0.03
    HA = 0.02
    HT = 0.02
    D = 0.01
    a_v_mode = 1 # 0 : uniform_distribution / 1 : normal_distribution
    mean = 0.5
    var = 0.05

    ##---Groups---##
    groups = 100
    basic_num = 100
    limit_users = 1000
    lv = 3
    remove_groups_less_than_setted_num = -1

    #------------Implement-------------#
    for t in T:
        print("Generating graph_",str(t))
        random.seed(10)
        np.random.seed(10)


        ### Node
        with open('./graph_SF'+ '_T=' + str(t) +'.txt','w') as f:
            print('Writing nodes...')
            for p in range(P):
                node_type = random.randint(0,3)
                if a_v_mode:
                    prob = round(np.random.normal(mean,scale=var),4)
                else:
                    prob = round(random.uniform(0,1),4)
                f.write('{} {},{},{},{},{},{},{},{},{},{},{}\n'.format('n',p, node_type, R, CT, S, CR, HI, HA, HT, D, prob))
        f.close()

        ### Edge
        count_e = 0
        with open('./graph_SF'+ '_T=' + str(t) +'.txt','a') as f:
            print('Writing edges...')
            for p in range(P):
                h_id = person_info[p]['h_id']
                family = house_info[h_id]['persons']

                work = person_info[p]['work']
                if work:
                    work_id = person_info[p]['work_id']
                    coworker = work_info[work_id]['persons']
                    touch_people_list = sorted(family + coworker)
                else:
                    not_work_id = person_info[p]['not_work_id']
                    nobody = not_work_info[not_work_id]['persons']
                    touch_people_list = sorted(family + nobody)

                for tp in touch_people_list:
                    #只記錄比自己大的node
                    if tp <= p :
                        continue
                    # family
                    if tp in family:
                        prob = random.uniform(0.7,0.9)
                        f.write('{} {},{},{}\n'.format('e',p,tp,round(prob,3)))
                        count_e += 1
                        continue

                    # coworker or nobody
                    # determine edge or not
                    edge_prob = random.randint(1,100)

                    if edge_prob > 50:
                        prob = random.uniform(0.1,0.5)
                        f.write('{} {},{},{}\n'.format('e',p,tp,round(prob,3)))
                        count_e += 1

        f.close()

        ### Groups
        count_x = 0
        with open('./graph_SF'+ '_T=' + str(t) +'.txt','a') as f:
            print('Writing groups...')

            group_list = [[] for _ in range(groups)]
            for g_idx in range(groups):
                # random the radius
                radius = np.random.normal(300,100)
                # random the center
                h_id = random.randint(0, H - 1)
                center_x = house_info[h_id]['x']
                center_y = house_info[h_id]['y']
                # meet the criteria h_id
                res = [house_id for house_id in range(H) \
                    if ((house_info[house_id]['x'] - center_x)**2 + \
                        (house_info[house_id]['y'] - center_y)**2)**0.5 < radius ]
                # get the person
                p = []
                for house_id in res:
                    p += house_info[house_id]['persons']
                    if len(p) >= limit_users:
                        break
                p = sorted(p)
                group_list[g_idx] = p


            for _t in range(t):
                for g_idx in range(groups):
                    cost = math.ceil(len(group_list[g_idx]) / basic_num)
                    eta = -1
                    if remove_groups_less_than_setted_num > 0:
                        if len(group_list[g_idx]) > remove_groups_less_than_setted_num:
                            for l in range(lv):
                                f.write('{} {}_{}_{}_{}_{}\n'.format('X', _t, cost, l+1, eta, ",".join(str(i) for i in group_list[g_idx])))
                                count_x += 1
                    else:
                        for l in range(lv):
                            f.write('{} {}_{}_{}_{}_{}\n'.format('X', _t, cost, l+1, eta, ",".join(str(i) for i in group_list[g_idx])))
                            count_x += 1

        f.close()

        # TODO: 補在檔案開頭 要有edge數量
        ### Graph.txt
        with open('./graph_SF'+ '_T=' + str(t) +'.txt','r+') as f:
            content = f.read()
            f.seek(0,0)
            f.write('{} {},{},{}\n{}'.format('g', P, count_e, count_x, content))
        f.close()

def generate_RLgrapgh():
    RL_T = 10
    RL_lv = 3 # graph lv {1:0.2 ,2:0.8, 3:1}
    budget = 100
    level_convert = {1:0.2 ,2:0.8, 3:1}

    print("Generate RLgraph...")

    ## 處理graph 讀資料進來，存到structure
    with open('./graph_SF_T=1.txt','r') as f:
        lines = f.readlines()
    f.close()

    node_data = {}
    Record_X = []
    Queue = []
    D_cost = []
    X_count = 0
    file_name = './RLgraph_SF_T='+ str(RL_T) + '_lv='+ str(RL_lv) + '_b='+ str(budget) +'.txt'
    node_num = 0
    edge_num = 0
    with open(file_name,'w') as f:
        for i in lines:
            data_type = i.split(' ')[0]
            data = i.split(' ')[1]
            if data_type == 'g':
                DATA = data.split(',')
                node_num = int(DATA[0])
                edge_num = int(DATA[1])
            if data_type == 'n':
                DATA = data.split(',')
                no = int(DATA[0])
                a_v = float(DATA[10][:-2])
                node_data[no] = {'a_v':a_v}
            if data_type == 'e':
                f.write(i)
            if data_type == 'X':
                DATA = data.split('_')
                day = int(DATA[0])
                cost = int(DATA[1])
                _lv = int(DATA[2])
                if day > 0:
                    break
                if _lv == RL_lv:
                    Record_X.append(i)
                    users = DATA[4].split(',')
                    # Calculate the sum of a_v
                    I = 0
                    for u in users:
                        a_v = node_data[int(u)]['a_v']
                        I += a_v
                    Queue.append((X_count,round(I,4)))
                    D_cost.append( cost * level_convert[RL_lv] )
                    X_count += 1
    f.close()


    # Sorted by I
    Queue.sort(key=lambda tup: tup[1],reverse = True)
    q = math.ceil(RL_T/2)
    b1 = budget / q

    if (b1 < 0.2 and RL_lv == 1) or (b1 < 0.8 and RL_lv == 2) or (b1 < 1 and RL_lv ==3):
        b1 = budget
        X1 = []
        while b1 > 0 and Queue != []:
            Dtop = Queue[0]
            Dtop_cost = D_cost[Dtop[0]]
            while Dtop_cost > b1 and Queue != []:
                Queue.remove(Queue[0])
                if Queue != []:
                    Dtop = Queue[0]
                    Dtop_cost = D_cost[Dtop[0]]
                else:
                    break
            if Dtop_cost > b1:
                break
            if Queue == []:
                break
            X1.append(Record_X[Dtop[0]])
            b1 -= Dtop_cost
            Queue.remove(Queue[0])

        with open(file_name,'a') as f:
            for x in X1:
                f.write(x[:2] + str(0) + x[3:])

        f.close()

        groups_num = len(X1)
        f = open(file_name, "r")
        contents = f.readlines()
        f.close()

        contents.insert(0, 'g {},{},{}\n'.format(node_num,edge_num,groups_num))

        f = open(file_name, "w")
        contents = "".join(contents)
        f.write(contents)
        f.close()
        print("Done.")

    else:
        X1 = []
        while b1 > 0 and Queue != []:
            Dtop = Queue[0]
            Dtop_cost = D_cost[Dtop[0]]
            while Dtop_cost > b1 and Queue != []:
                Queue.remove(Queue[0])
                if Queue != []:
                    Dtop = Queue[0]
                    Dtop_cost = D_cost[Dtop[0]]
                else:
                    break
            if Dtop_cost > b1:
                break
            if Queue == []:
                break
            X1.append(Record_X[Dtop[0]])
            b1 -= Dtop_cost
            Queue.remove(Queue[0])

        _groups_num = len(X1)
        groups_num = 0
        with open(file_name,'a') as f:
            for t in range(0,RL_T,2):
                for x in X1:
                    f.write(x[:2] + str(t) + x[3:])
                groups_num += _groups_num
        f.close()

        f = open(file_name, "r")
        contents = f.readlines()
        f.close()

        contents.insert(0, 'g {},{},{}\n'.format(node_num,edge_num,groups_num))

        f = open(file_name, "w")
        contents = "".join(contents)
        f.write(contents)
        f.close()


        print("Done.")

def generate_OSgraph():
    OS_T = 10
    OS_lv = 2
    OS_budget = 1000
    OS_R = 100

    node_av = []
    node_neighbor = {}
    Record_D = []
    D_cost = []

    def RIP(root,S,OS_T):
        RR = []
        v = root
        met = False
        t_end = OS_T - 1
        for t in range(OS_T):
            N = []
            for u in node_neighbor[v].keys():
                p = random.uniform(0,1)
                if p <= node_neighbor[v][u]:
                    N.append(u)
            if N == []:
                break
            _u_idx = random.randint(0,len(N) - 1)
            _u = N[_u_idx]
            if _u in S:
                met = True
                t_end = t
                break
            else:
                RR.append((_u,t))
                v = _u
        if met == True:
            for idx in range(len(RR)):
                RR[idx] = (RR[idx][0], t_end - RR[idx][1])

        else:
            RR = []

        return RR

    def cover(M,U):
        count_list = []
        for u_idx in range(len(U)):
            count = 0
            nodes = [ int(n) for n in U[u_idx].split(' ')[1].split('_')[4][:-1].split(',')]
            for m in M:
                if m != []:
                    for tup in m:
                        if tup[0] in nodes:
                            count += 1
                            break
            count_list.append((u_idx,count))

        return count_list

    print("Generate OSgraph...")

    ## 處理graph 讀資料進來，存到structure
    with open('./graph_SF_T=1.txt','r') as f:
        lines = f.readlines()
    f.close()

    file_name = './OSgraph_SF_T='+ str(OS_T) + '_lv='+ str(OS_lv) + '_b='+ str(OS_budget)+ '_R='+ str(OS_R) +'.txt'


    with open(file_name,'w') as f:
        for i in lines:
            data_type = i.split(' ')[0]
            data = i.split(' ')[1]
            if data_type != 'X':
                f.write(i)
            if data_type == 'n':
                DATA = data.split(',')
                no = int(DATA[0])
                a_v = float(DATA[10][:-2])
                node_av.append(a_v)
                # init node_neighbor
                node_neighbor[no] = {}
            if data_type == 'e':
                DATA = data.split(',')
                n1 = int(DATA[0])
                n2 = int(DATA[1])
                prob = float(DATA[2][:-2])
                node_neighbor[n1][n2] = prob
            if data_type == 'X':
                DATA = data.split('_')
                day = int(DATA[0])
                cost = int(DATA[1])
                _lv = int(DATA[2])
                if _lv == OS_lv:
                    Record_D.append(i)
                    users = DATA[4].split(',')
                    D_cost.append(cost)

    ## OS-IP
    M = []
    for r in range(OS_R):
        root = random.randint(0,len(node_av) - 1)
        S = []
        for v in range(len(node_av)):
            p = random.uniform(0,1)
            if p <= node_av[v]:
                S.append(v)
        RIP_result = RIP(root,S,OS_T)
        M.append(RIP_result)

    U = []
    u_cost = []
    for t in range(OS_T):
        u_cost += D_cost
        for d in Record_D:
            U.append(d[:2] + str(t) + d[3:])

    count_list = cover(M,U)
    count_list.sort(key=lambda tup:tup[1], reverse = True)

    S = []
    while OS_budget > 0 and count_list != []:
        Dtop = count_list[0]
        Dtop_cost = u_cost[Dtop[0]]
        while Dtop_cost > OS_budget and U != []:
            count_list.remove(count_list[0])
            if count_list != []:
                Dtop = count_list[0]
                Dtop_cost = u_cost[Dtop[0]]
            else:
                break
        if Dtop_cost > OS_budget :
            break
        if count_list == []:
            break
        S.append(U[Dtop[0]])
        OS_budget -= Dtop_cost
        count_list.remove(count_list[0])

    with open(file_name,'a') as f:
        for s in S:
            f.write(s)

    f = open(file_name, "r")
    contents = f.readlines()
    f.close()

    tmp = contents[0].split(',')

    contents[0] = tmp[0] + "," + tmp[1] + "," + str(len(S)) + '\n'

    f = open(file_name, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()
    print('Done')



if __name__ == '__main__':
    init_house_location()
    assign_person()
    generate_graph()
    generate_RLgrapgh()
    generate_OSgraph()


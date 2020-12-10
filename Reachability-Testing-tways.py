t_way=2

#RECEIVE_SHEET_NAME='SYN-res.csv'
#SEND_SHEET_NAME='SYN-snd.csv'

RECEIVE_SHEET_NAME='res.csv'
SEND_SHEET_NAME='sen.csv'


#RECEIVE_SHEET_NAME='SYN-sequence-receive.csv'
#SEND_SHEET_NAME='SYN-sequence-send.csv'

import pandas as pd
import numpy as np
from tqdm import tqdm
import re
from IPython.display import display
import warnings
from allpairspy import AllPairs
from collections import OrderedDict
import time
import pprint
warnings.simplefilter('ignore')

def cstruct(event,results):
    global Q
    global Qs
    global Qr
    global check_digit
    
    if check_digit==0:
        magic=0
    else:
        magic=1
    
    thread=event['Thread']
    index=event['Index']
       
    if index==1:
        return ''
    for i in range(index-1,0,-1):
        try:
            temp=Qr[number+magic][(Qr[number+magic].Thread == thread) & (Qr[number+magic].Index==i)].iloc[0]
        except:
            temp=Qs[number+magic][(Qs[number+magic].Thread == thread) & (Qs[number+magic].Index==i)].iloc[0]
        if temp['Event']=='send':
            results.append(temp['ID'])
            event=temp
            results.extend(cstruct(event,results))
        else:
            results.append(temp['ID'])
            send=Qs[number+magic].iloc[temp.name]
            results.append(send['ID'])
            results.extend(cstruct(send,results))
    return list(set(results))

## raceの重複判定のためのc-struct


    
def no_index(start,finish,t,event,R):
    #if type(event)==int:
    #    event=Qr[(Qr.ID==R[finish])].iloc[0]
    for l in range(start,finish):
        if t[l]>0 and R[l] in cstruct(event,[]):
            return True
        else:
            continue
    return False


## =======race作成のための関数==========
def str_to_list(string):
    l=string.split(',')
    list=[]
    for i in range(len(l)):
        if i==0:
            if len(l)==1:
                list.append(l[i][1:len(l[i])-1])
            else:
                list.append(l[i][1:])
        elif i==len(l)-1:
            list.append(l[i][:len(l[i])-1])
        else:
            list.append(l[i])
    return list


def creating_race_set(race_set):
    global Qr
    global Qs
    # race_set の初期化
    for i in range(len(Qr[0])):

        race_set[Qr[0].iloc[i].ID]=[]
        
    # sでループ
    for i in range(len(Qs[0])):
        #sでループ

        number=Qs[0].iloc[i].name
        ID=Qs[0].iloc[i].ID
        thread=Qs[0].iloc[i].Thread
        port=Qs[0].iloc[i].Port
        
        pair_event=Qr[0].iloc[number]

        try: #rの次のイベントがrかどうか判定
            next_event=Qr[0][(Qr[0].Index==pair_event.Index+1) & (Qr[0].Thread==pair_event.Thread)].iloc[0]
            race=Qs[0].iloc[next_event.name]
        except Exception as e:
            next_event=[]
            continue
        
        #これ以降はrの次がrだったとき

        if str_to_list(port)[0] in str_to_list(next_event.Port):#ポートが一致    
            # race_setについか
            race_set[pair_event.ID].append(race.ID) 
    return race_set

## =======race作成のための関数==========

## =======race削除のための関数==========

def remove_race(race1,race2): #race_set(r,Q)=race_set(r,Q)-race_set(r,V)
    for key1 in race1.keys():
        try:
            dup=list(set(race1[key1] + race2[key1]))

            for index in range(len(dup)):
                race1[key1].remove(dup[index])
        except Exception as e:

            continue
    return race1

## =======race削除のための関数==========

def construct_race_table(Q,Qs,Qr,race_set):
    global t_way
    R=[] #create race_set
    D=[] #number of race_set
    heading=[] #{r1,r2,....r}

    R.append('')
    D.append('')
    heading.append('dummy')
    count=0
    for key in race_set.keys():
        if len(race_set[key])>0 and Q[Q['ID']==key].iloc[0].coler=='white':
            R.append(key) # raceのあるイベントを追加
            D.append(len(race_set[key])) #raceの数を追加
            heading.append(key) # r
            count=count+1
            if count>=t_way and t_way>1:
                break
    table=pd.DataFrame([],columns=heading)

    t=np.zeros(len(R)) #raceの数分の配列 #t[0]はダミー

    while True:

        results=[]

        max_index=''
        for i in range(len(t)-1,0,-1):
            if t[i]<D[i] and t[i]!=-1:
                max_index=i
                break
        if max_index=='':
            break
        t[i]+=1

        if t[i]==1: #just changed t[i] from 0 to 1

            for j in range(i+1,len(R)):
                if t[j]!=-1 and (Qr[Qr.ID==R[i]].iloc[0].ID in cstruct(Qr[Qr.ID==R[j]].iloc[0],[])):

                    t[j]=-1

        for j in range(i+1,len(R)):
            if(t[j]==D[j]):
                t[j]=0 #just change t[j] from dj to 0

                for k in range(j+1,len(R)):
                    if t[k]==-1 and Qr[Qr.ID==R[j]].iloc[0].ID in cstruct(Qr[Qr.ID==R[k]].iloc[0],[]) and no_index(1,k,t,Qr[(Qr.ID==R[k])].iloc[0],R):
                        t[k]=0
        #let s be the t[i] sending event in race_set(ri)
        s= race_set[R[i]][int(t[i])-1] 


        if no_index(1,len(R)-1,t,Qs[(Qs.ID==s)].iloc[0],R)==False:
            table=table.append(pd.Series(t,index=table.columns),ignore_index=True)
    return table.drop('dummy',axis=1)

def expand_table(table):
    global Qr
    global t_way
    global race_set
    
    for way in tqdm(range(t_way,len(Qr[0]))): #1列ずつ足していくためのループ
        new_event=Qr[0].iloc[way]

        if (len(race_set[Qr[0].iloc[way].ID]))>0: #raceがあるかどうか確認

            ## 横方向の拡張

            pi=[]
            heading=table.columns
            for i in range(len(heading)):
                pi.append(pd.DataFrame({heading[i]:[],new_event.ID:[]}))
                heading2=pi[i].columns
                for j in range(len(heading2)):              
                    new_row=pd.Series([])
                    parameters_dict={}
                    heading=table.columns.values
                    for i2 in range(len(heading)):
                        parameters_dict[heading[i2]]=[]
                        for j2 in range(len(race_set[heading[i2]])+1):
                            parameters_dict[heading[i2]].append(j2)
                    parameters=OrderedDict(parameters_dict)
                    for k, pairs in enumerate(AllPairs(parameters)):
                        new_row[len(new_row)]=pairs[j]
                    pi[i][heading2[j]]=new_row
                pi[i]=pi[i][pi[i].sum(axis=1)!=0]
                pi[i]=pi[i].reset_index(drop=True)

            table[new_event.ID]=''
            for index in range(len(table)):#tableのループ
                match_count_array=[]
                for race_num in range(len(race_set[Qr[0].iloc[way].ID])+1): #raceの数だけループ
                    match_count_array.append(0)
                    check_array=table.iloc[index]
                    check_array[new_event.ID]=race_num
                    for i in range(len(pi)):#piごとにループ
                        check_array_edit=check_array[pi[i].columns]
                        for j in range(len(pi[i])):
                            if (check_array_edit==pi[i].iloc[j]).all():
                                match_count_array[race_num]+=1
                max_value=max(match_count_array) #raceの中からカバーできる最大値を取得
                max_index=match_count_array.index(max_value)
                table.at[index,new_event.ID]=max_index #tableに新しいデータを追加
                    #ついかした組み合わせがあるものを削除
                delete_array=table.iloc[index]
                for i in range(len(pi)):
                    delete_array_edit=delete_array[pi[i].columns]
                    for j in range(len(pi[i])):
                        if (delete_array_edit==pi[i].loc[j]).all():
                            pi[i].drop(j,inplace=True)
                    pi[i]=pi[i].reset_index(drop=True)
            ## 縦方向の拡張
            for i in range(len(pi)):
                for j in range(len(pi[i])):
                    table=table.append(pi[i].iloc[j])# 最終行を挿入
                    table=table.reset_index(drop=True)
                    last_data=table.iloc[len(table)-1]#最終行を取得
                    #これ以降は最終行の欠損地を埋めていく処理
                    for k in range(len(last_data)):
                        if last_data.isna()[k]:#欠損地のとき
                            # 制御構造に入っているか確認
                            #一個前に値がなければnot-1
                            for l in range(k,0,-1):
                                if last_data[l-1]==1:
                                    if Qr[0][Qr[0].ID==list(table.columns)[l-1]].iloc[0].ID in cstruct(Qr[0][Qr[0].ID==list(table.columns)[k]].iloc[0],[]):
                                        table.at[len(table)-1,list(table.columns)[k]]=-1
                                        break
                                        #制御構造構造
                        ##-1は既に埋まっている
                        table=table.fillna(0)
    return table


#ペアワイズのための関数


#============ここから定義============

number=0 # 実験の回数
heading_res=('Thread','Port','Event','Index')
heading_snd=('Thread','Port','Event','Index')

Qs=[pd.DataFrame({})]
Qr=[pd.DataFrame({})]


#Q is SYN-sequence
Qr[0]=pd.read_csv(RECEIVE_SHEET_NAME,names=heading_res)
Qs[0]=pd.read_csv(SEND_SHEET_NAME,names=heading_snd)

Qr[0]['Thread']=Qr[0]['Thread'].map(lambda x:'T'+str(x))
Qs[0]['Thread']=Qs[0]['Thread'].map(lambda x:'T'+str(x))


r_list=list(range(1,len(Qr[0])+1))
r_list=list(map(lambda x:'r'+str(x),r_list)) #['r1', 'r2', 'r3', 'r4']
s_list=list(range(1,len(Qs[0])+1))
s_list=list(map(lambda x:'s'+str(x),s_list)) #['s1', 's2', 's3', 's4']

Qr[0].insert(0,'ID',r_list) #attach the name of event
Qs[0].insert(0,'ID',s_list) #attach the name of event

## raceの作成
race_set={}

start = time.time()

race_set=creating_race_set(race_set)
elapsed_time = time.time() - start
print ("Creating race set took:{:.4g}".format(elapsed_time) + "[sec]")
pprint.pprint((race_set))
Qr[0]['coler']='white'

Q=[pd.DataFrame({})] #Q is SYN-sequence
Q[0]=pd.merge(Qr[0],Qs[0],how='outer')


r_list=[]
s_list=[]
check_digit=0

for i in range(0,len(Qr[0])):
    r_list.append(cstruct(Qr[0].iloc[i],[]))
    s_list.append(cstruct(Qs[0].iloc[i],[]))
#r_list.extend(s_list)
Q_unique=pd.DataFrame({})
Qr_unique=Qr[0].copy()
Qs_unique=Qs[0].copy()
Qr_unique.insert(len(Qr_unique.columns),'cstruct',r_list)
Qs_unique.insert(len(Qs_unique.columns),'cstruct',s_list)
#Q_unique=pd.merge(Qr_unique,Qs_unique,how='outer')
#Q_unique.insert(len(Qs_unique.columns),'cstruct',r_list) #保存するようのテーブル

r_last_index=len(Qr_unique)+1 #それぞれの新しいインデックスを付与するための変数→初期化
s_last_index=len(Qs_unique)+1 #+1で新しいindexをそのまま付与

#============ここまで定義============



#====メイン関数====
start = time.time()
table=construct_race_table(Q[0],Qs[0],Qr[0],race_set)


if t_way>1:
    table=expand_table(table)
elapsed_time = time.time() - start
print ("Creating race table took:{:.4g}".format(elapsed_time) + "[sec]")

table=table.astype('int64')
columns=list(table.columns)
check_digit=1

start = time.time()
for number in tqdm(range(0,len(table))):
    Q.append(pd.DataFrame({})) #新しいテーブルを作成
    Qs.append(pd.DataFrame({}))
    Qr.append(pd.DataFrame({}))
    Q[number+1]=Q[0].copy()
    Qs[number+1]=Qs[0].copy()
    Qr[number+1]=Qr[0].copy()
    for key in range(0,len(columns)): # 列方向のループr1→r3
        if table.iloc[number][columns[key]]>0: #race_set の交換

            #Q[i+1]のテーブルを修正
            change_event=Qr[number+1][Qr[number+1]['ID']==columns[key]].iloc[0].ID # receiveの交換するやつr3
            change_event_number=Qr[number+1][Qr[number+1]['ID']==columns[key]].iloc[0].name #r3の行番号→2
            new_partner=race_set[Q[number+1][Q[number+1]['ID']==columns[key]].iloc[0].ID][int(table.iloc[number][columns[key]])-1] #sendの新しいパートナー s4
            new_partner_number=Qs[number+1][Qs[number+1]['ID']==new_partner].iloc[0].name #s4の行番号→3
            
            
            ## QSのindexを振りなおす処理
            new_index=[]
            for j in range(0,len(Qr[number+1])):
                if j==change_event_number:
                    new_index.append(new_partner_number)
                elif j==new_partner_number:
                    new_index.append(change_event_number)
                else:
                    new_index.append(j)

            Qs[number+1]['new_index']=new_index
            Qs[number+1]=Qs[number+1].set_index('new_index')
            Qs[number+1].sort_index(inplace=True)
            
            Q[number+1]=pd.merge(Qr[number+1],Qs[number+1],how='outer')
            
            #==========Qrの重複追加作業=================
            
            for index,row in Qr[number+1].iterrows():
                results=cstruct(Qr[number+1].iloc[index],[])
                judge=False
                if results: #空だったらnot 
                    for index2,row2 in Qr_unique.iterrows():
                        if results==Qr_unique.at[index2,'cstruct']:
                            new_index=index2
                            judge=True
                            break
                    if not judge: #Falseだったら判定
                        Qr[number+1].at[index,'ID']='r'+str(r_last_index)
                        #Qr[number+1].at[index,'cstruct']=results
                        r_last_index+=1
                        temp=list(Qr[number+1].iloc[index])
                        temp.append(results)
                        temp=pd.Series(temp,index=Qr_unique.columns,name=len(Qr_unique))
                        #temp=pd.DataFrame(,columns=Qr_unique.columns)
                        #Qr_unique.append(temp,ignore_index=False)
                        #pd.concat([Qr_unique,temp],axis=0)
                        Qr_unique.loc[len(Qr_unique)]=temp
                    else:
                        Qr[number+1].iloc[index]=Qr_unique.iloc[new_index]
                else:
                    pass
            
            #==========Qsの重複追加作業=================
            
            
            for index,row in Qs[number+1].iterrows():
                results=cstruct(Qs[number+1].iloc[index],[])
                judge=False
                if results: #空だったらnot 
                    for index2,row2 in Qs_unique.iterrows():
                        if results==Qs_unique.at[index2,'cstruct']:
                            new_index=index2
                            judge=True
                            break
                    if not judge: #Falseだったら判定
                        Qs[number+1].at[index,'ID']='s'+str(s_last_index)
                        #Qr[number+1].at[index,'cstruct']=results
                        s_last_index+=1
                        temp=list(Qs[number+1].iloc[index])
                        temp.append(results)
                        temp=pd.Series(temp,index=Qs_unique.columns,name=len(Qs_unique))
                        #temp=pd.DataFrame(,columns=Qr_unique.columns)
                        #Qr_unique.append(temp,ignore_index=False)
                        #pd.concat([Qr_unique,temp],axis=0)
                        Qs_unique.loc[len(Qs_unique)]=temp
                    else:
                        Qs[number+1].iloc[index]=Qs_unique.iloc[new_index]
                else:
                    pass
                 
                
            #Qr_unique.append(cstruct_results[0],ignore_index=True) # 戻り値を既存の表に追加
            #Qs_unique.append(cstruct_results[1],ignore_index=True)
            
            Q[number+1]=pd.merge(Qr[number+1],Qs[number+1],how='outer')
            Q[number+1]=Q[number+1].drop('coler',axis=1)
Q[0]=Q[0].drop('coler',axis=1)
elapsed_time = time.time() - start
print ("Creating test case took:{:.4g}".format(elapsed_time) + "[sec]")
print('The number of Test Case is {}.'.format(len(Q)))


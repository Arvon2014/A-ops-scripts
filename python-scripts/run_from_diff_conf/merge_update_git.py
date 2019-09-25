
import csv
import os
import re
import commands

def update_etcd(merge_conf):
    new_rel=[]
    for each_shard in merge_conf['MergeShards'].split('-'):
        with open(os.path.join(git_path,'etcd-config','prod',str(gid),each_shard),'rb') as f:
            new_rel += re.search('merge_rel=.*', f.read()).group().split('=')[1].split(',')
    with open(os.path.join(git_path,'etcd-config','prod',str(gid),merge_conf['MergeShards'].split('-')[0]),'rb') as f1:
        new_data=''
        for each_line in f1.readlines():
            if 'merge_rel=' in each_line:
                each_line = re.sub('merge_rel=.*', 'merge_rel=%s' % str.join(',',new_rel), each_line)
            elif re.match('redis=.*', each_line):
                each_line = re.sub('redis=.*', 'redis=%s' % merge_conf['TredisDB'], each_line)
            elif re.match('redis_db=.*', each_line):
                each_line = re.sub('redis_db=\d+', 'redis_db=%s' % merge_conf['TredisNum'], each_line)
            elif re.search('rank_redis=', each_line):
                each_line = re.sub('rank_redis=.*', 'rank_redis=%s' % merge_conf['TrankDB'], each_line)
            elif re.search('rank_redis_db=', each_line):
                each_line = re.sub('rank_redis_db=.*', 'rank_redis_db=%s' % merge_conf['TrankNum'], each_line)
            new_data += each_line
    with open(os.path.join(git_path,'etcd-config','prod',str(gid),merge_conf['MergeShards'].split('-')[0]),'w') as f2:
        f2.write(new_data)

def delete_etcd(merge_conf):
    for del_shard in merge_conf['MergeShards'].split('-')[1:]:
        del_file = os.path.join(git_path, 'etcd-config', 'prod', str(gid), del_shard)
        if os.path.exists(del_file):
            os.remove(del_file)
            print 'Delete etcd config %s' % del_shard
        else:
            print 'The file %s not exist, Please check' % del_shard


def update_facts(merge_conf):
    if gid == 210:
        facts_file = os.path.join(git_path, 'ansible-deploy-code', 'inventory','all_210_row')
    elif gid == 211:
        facts_file = os.path.join(git_path, 'ansible-deploy-code', 'inventory','all_211_eu')
    elif gid == 212:
        facts_file = os.path.join(git_path, 'ansible-deploy-code', 'inventory','all_212_ya')
    for del_shard in merge_conf['MergeShards'].split('-')[1:]:
        print 'sed -i  "" "s/%s//g;s/||/|/g;s/|\'//g;s/=\'|/=\'/g" %s' % (del_shard,facts_file)
        status, output = commands.getstatusoutput('sed -i "" "s/%s//g;s/||/|/g;s/|\'//g;s/=\'|/=\'/g" %s' % (del_shard,facts_file))
    if 'status' in dir() and 'output' in dir():
        print status, output


if __name__ == '__main__':
    git_path = '/Users/arvon/Documents/Tai_gitlab/ops-oversea-ansible/'
    gid = 211
    with open('merge_plan.csv_211', 'rb') as f1:
        reader = csv.reader(f1, delimiter=',')
        fieldnames = next(reader)
        reader = csv.DictReader(f1, fieldnames=fieldnames,delimiter=',')
        for row in reader:
            rst = {}
            #print '%s-%s' % (row['Ashards'],row['Bshards'])
            rst['MergeShards'] = '%s-%s' % (row['Ashards'],row['Bshards'])
            rst['TredisDB'] = row['TredisDB']
            rst['TredisNum'] = row['TredisNum']
            rst['TrankDB'] = row['TrankDB']
            rst['TrankNum'] = row['TrankNum']
            print rst
            print rst['MergeShards'],'now update etcd ...'
            update_etcd(rst)
            delete_etcd(rst)
            print rst['MergeShards'], 'now update facts ...'
            update_facts(rst)

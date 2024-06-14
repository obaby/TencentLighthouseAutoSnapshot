# -*-coding:UTF-8-*-

"""
腾讯云轻量云自动进行快照备份
轻量云免费提供2个快照，所以该脚本只备份两个快照
更新 by： obaby
https://oba.by
https://h4ck.org.cn
"""

import json
import os
import time
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.lighthouse.v20200324 import lighthouse_client, models



def main(SecretId, SecretKey, region, InstanceIds, Instanceidx=1, KeepPolicy=2):
    """
    GOGO
    :param SecretId: str 腾讯云账号SecretId
    :param SecretKey: str 腾讯云账号SecretKey
    :param region: str 实例地域
    :param InstanceIds: str 实例ID
    param Instanceidx: int 0:删除最新的保留最早的备份，这样可以有一个固定备份，1:删除最早
    """
    get_rest = get_info(SecretId, SecretKey, region, InstanceIds)
    if get_rest != False:
        TotalCount = get_rest['TotalCount']
        # 快照数
        if TotalCount < 2:
            # 直接备份
            CreateInstanceSnapshot(SecretId, SecretKey, region, InstanceIds)
        elif TotalCount == 2:
            if KeepPolicy ==1:
                # 删除之前较早一个备份,就是列表里的第二个,状态需要正常才能删除
                SnapshotState = (get_rest['SnapshotSet'][Instanceidx]['SnapshotState'])
                if SnapshotState == 'NORMAL':
                    SnapshotId = (get_rest['SnapshotSet'][Instanceidx]['SnapshotId'])
                    DeleteSnapshots_re = DeleteSnapshots(SecretId, SecretKey, SnapshotId, region)
                    if DeleteSnapshots_re != False:
                        # 删除之前一个后，再进行备份
                        print('已经删除完成快照ID为{0}的快照，现在准备开始备份实例'.format(SnapshotId))
                        CreateInstanceSnapshot(SecretId, SecretKey, region, InstanceIds)
            else:
                # 使用其他保留策略 备份名称中包含 keep 或者 保留 字样的快照保留 如果都保留，按照 0 1 策略删除
                snapshots = get_rest['SnapshotSet']
                snapshot_id = None
                for s in snapshots:
                    if 'keep' in  s['SnapshotName'] or u'保留' in  s['SnapshotName']:
                        continue
                    else:
                        snapshot_id = s['SnapshotId']
                if snapshot_id is not None:
                    print('准备删除快照ID为{0}的快照'.format(snapshot_id))
                    DeleteSnapshots_re = DeleteSnapshots(SecretId, SecretKey, snapshot_id, region)
                    if DeleteSnapshots_re != False:
                        # 删除之前一个后，再进行备份
                        print('已经删除完成快照ID为{0}的快照，现在准备开始备份实例'.format(snapshot_id))
                        CreateInstanceSnapshot(SecretId, SecretKey, region, InstanceIds)
                else:
                    print('多个快照都被设置为长期保存，根据删除策略进行快照删除')
                    SnapshotState = (get_rest['SnapshotSet'][Instanceidx]['SnapshotState'])
                    if SnapshotState == 'NORMAL':
                        SnapshotId = (get_rest['SnapshotSet'][Instanceidx]['SnapshotId'])
                        DeleteSnapshots_re = DeleteSnapshots(SecretId, SecretKey, SnapshotId, region)
                        if DeleteSnapshots_re != False:
                            # 删除之前一个后，再进行备份
                            print('已经删除完成快照ID为{0}的快照，现在准备开始备份实例'.format(SnapshotId))
                            CreateInstanceSnapshot(SecretId, SecretKey, region, InstanceIds)
        else:
            print('当前快照数量存在问题，请登录腾讯云后台检查并删除多余的快照后操作')
            time.sleep(5)
            exit()


def CreateInstanceSnapshot(SecretId, SecretKey, region, InstanceIds):
    """
    创建快照
    """
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "lighthouse.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = lighthouse_client.LighthouseClient(cred, region, clientProfile)
        req = models.CreateInstanceSnapshotRequest()
        params = {
            "InstanceId": InstanceIds
        }
        req.from_json_string(json.dumps(params))
        resp = client.CreateInstanceSnapshot(req)
        resp_re = json.loads(resp.to_json_string())
        SnapshotId = resp_re['SnapshotId']
        print('轻量云快照备份完成，快照ID为：{0},程序在5秒钟后关闭'.format(SnapshotId))
        time.sleep(5)
        #exit()

    except TencentCloudSDKException as err:
        print(err)
        return False


def DeleteSnapshots(SecretId, SecretKey, SnapshotId, region):
    """
    删除快照
    """
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "lighthouse.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = lighthouse_client.LighthouseClient(cred, region, clientProfile)

        req = models.DeleteSnapshotsRequest()
        params = {
            "SnapshotIds": [SnapshotId]
        }
        req.from_json_string(json.dumps(params))
        resp = client.DeleteSnapshots(req)
        return json.loads(resp.to_json_string())

    except TencentCloudSDKException as err:
        print(err)
        return False


def get_info(SecretId, SecretKey, region, InstanceIds):
    """
    获取快照信息
    :param SecretId: str 腾讯云账号SecretId
    :param SecretKey: str 腾讯云账号SecretKey
    :param region: str 实例地域
    :param InstanceIds: str 实例ID
    :return: json 腾讯云实例流量情况
    """
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "lighthouse.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = lighthouse_client.LighthouseClient(cred, region, clientProfile)
        req = models.DescribeSnapshotsRequest()
        params = {
            "Filters": [
                {
                    "Name": "instance-id",
                    "Values": [ InstanceIds ]
                }
                ]
        }
        req.from_json_string(json.dumps(params))
        resp = client.DescribeSnapshots(req)
        return json.loads((resp.to_json_string()))
    except TencentCloudSDKException as err:
        print(err)
        return False
    

def main_handler(event, context):
    """
    腾讯云API库安装
    pip install -i https://mirrors.tencent.com/pypi/simple/ --upgrade tencentcloud-sdk-python
    腾讯云账号ID获取地址
    https://console.cloud.tencent.com/cam/capi
    实例地域
    "ap-beijing", "ap-chengdu", "ap-guangzhou", "ap-hongkong", "ap-nanjing", "ap-shanghai", "ap-singapore", "ap-tokyo", "eu-moscow", "na-siliconvalley"
    """
    # SecretId
    SecretId = os.environ.get('SecretId')
    # SecretKey
    SecretKey = os.environ.get('SecretKey')
    # 【格式】实例地域1:轻量云实例ID1,轻量云实例ID2;实例地域2:轻量云实例ID3,轻量云实例ID4
    Regions_InstanceIds = os.environ.get('Regions_InstanceIds')

    # 0: 删除最新的保留最早的备份，这样可以有一个固定备份，1: 删除最早,默认 1
    Instanceidx = os.environ.get('Instanceidx')
    # 快照保留策略 1：默认删除逻辑 根据上述删除策略进行快照删除 2：保留特定扩展名的快照，如果都包含按照上述删除策略删除快照
    KeepPolicy = os.environ.get('KeepPolicy')

    # 执行
    nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print('---------' + str(nowtime) + ' 程序开始执行------------')
    for r in Regions_InstanceIds.split(";"):
        Region = r.split(":")[0]
        InstanceIds = r.split(":")[1]
        for id in InstanceIds.split(","):
            print('Region: '+Region+'InstanceId: '+id+'\n')
            main(SecretId, SecretKey, Region, id, int(Instanceidx), int(KeepPolicy))
    return True
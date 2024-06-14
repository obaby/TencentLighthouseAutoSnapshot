腾讯轻量云自动快照脚本
-----

所需参数：  
```python
:param SecretId: str 腾讯云账号SecretId
    :param SecretKey: str 腾讯云账号SecretKey
    :param region: str 实例地域
    :param InstanceIds: str 实例ID
    :param Instanceidx: int 0:删除最新的保留最早的备份，这样可以有一个固定备份，1:删除最早
:param KeepPolicy: int 快照保留策略 1：默认删除逻辑 根据上述删除策略进行快照删除 2：保留特定扩展名的快照，如果都包含按照上述删除策略删除快照
```  

教程地址：
[https://h4ck.org.cn/2024/06/17331](https://h4ck.org.cn/2024/06/17331)

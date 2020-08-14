#Load Balancer
##API
<code>/action</code>: receive action requests from clients <br/>
format:
```
{
    'action': <action_name>,
    'params': <parameters>
}
```
---
<code>/redirect</code>: receive redirect requests from server nodes
data format:
```
{
    server_node(ip_address):[{
        'name': <action_name>,
        'packages': [
            'p1': 'default',
            'p2': 'v1'
        ]}, {
        ...}, ...
    ]
}
```


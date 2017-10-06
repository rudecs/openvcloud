# Private Images

By default images are public, available to all accounts.

In order to make an image private, only available to a specific account, you need to use the OSIS client available in JumpScale:
```python
lc = j.clients.osis.getNamespace('cloudbroker')
```

Let's check the first available image:
```python
lc.image.get(1)
```

Here's the output:
```python
{
  "UNCPath": "",
  "_ckey": "",
  "_meta": [
    "osismodel",
    "cloudbroker",
    "image",
    1
  ],
  "accountId": 0,
  "acl": [],
  "description": "",
  "gid": 109,
  "guid": 1,
  "id": 1,
  "name": "Ubuntu 16.04 x64",
  "password": "",
  "provider_name": "libvirt",
  "referenceId": "827888fb-7eaa-41bc-b934-f3687e29bc47",
  "size": 10,
  "status": "CREATED",
  "type": "Linux",
  "username": null
}
```

Let's change the value of `accountId`, make this image only available to account with ID 59:
```python
image = lc.image.get(1)
image.accountId = 59
lc.image.set(image)
```

Output will be:
```python
[1, False, True]
```

Checking the result:
```python
image
```

Output:
```python
{
  "UNCPath": "",
  "_ckey": "",
  "_meta": [
    "osismodel",
    "cloudbroker",
    "image",
    1
  ],
  "accountId": 59,
  "acl": [],
  "description": "",
  "gid": 109,
  "guid": 1,
  "id": 1,
  "name": "Ubuntu 16.04 x64",
  "password": "",
  "provider_name": "libvirt",
  "referenceId": "827888fb-7eaa-41bc-b934-f3687e29bc47",
  "size": 10,
  "status": "CREATED",
  "type": "Linux",
  "username": null
}
```

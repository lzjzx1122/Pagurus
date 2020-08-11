## Avoiding padding errors with Python's base64 encoding

```
>>> import base64
>>> data = '{"u": "test"}'
>>> code = base64.b64encode(data)
>>> code
'eyJ1IjogInRlc3QifQ=='
```

Note the trailing `==` to make len a multiple of 4. This decodes properly

```
>>> len(code)
20
>>> base64.b64decode(code)
'{"u": "test"}'
>>> base64.b64decode(code) == data
True
```

*without* the == padding (this is how many things are encoded for e.g. access tokens)
```
>>> base64.b64decode(code[0:18]) == data
...
TypeError: Incorrect padding 
```

However, you can add back the padding
```
>>> base64.b64decode(code + "==") == data
True
```

Or add an arbitrary amount of padding (it will ignore extraneous padding)

```
>>> base64.b64decode(code + "========") == data
True
```

This last property of python's base64 decoding ensures that the following code
adding 3 padding `=` will never succumb to the TypeError and will always produce the same result.
```
>>> base64.b64decode(code + "===") == data
True
```

It's clumsy but effective method to deal with strings from different implementations of base64 encoders
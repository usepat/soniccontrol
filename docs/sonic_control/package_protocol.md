@defgroup PackageProtocol
@ingroup SonicControl
@addtogroup PackageProtocol
@{

# Package Protocol {#PackageProtocol}

## Brief Description

The Package Protocol is a rudimentary implementation of a simple transport layer protocol.

## Use Cases

In Future there will be Worker and Postman devices. The Workers have the actual transducer and the postmans control them. Because of that we need to specify somehow if a command is for a postman or for the worker connected to the postman. Also it is possible, that we have multiple workers on one postman, so we have kind of a network of devices.

The devices should return logs, if logging is activated.

There was a wish for a more flexible way to read responses, because some responses where multiple line (They were multiple line for better readability).

When receiving answers we want to know which answer is for which request.

## Specification

The package protocol wraps each answer into a package.

| Attribute | Description | Value Min | Value Max |
|-----------|-------------|-----------|-----------|
| DEST      | The destination contains the receiver of the sender | N/A       | N/A       |
| SRC       | The source contains the address of the sender         | N/A       | N/A       |
| ID        | Is an ID for this package                             | 0         | $2^{16}-1$|
| LEN       | Is the length of the content of the package           | 0         | 512 (I do not remember, check this) |
| CONTENT   | Content of the package                                |           |           |

The package has the following format:
```
<[DEST]#[SRC]#[ID]#[LEN]#CONTENT>
```

The package can contain logs and they are in this format:
```
LOG=[LOG-LEVEL]:[LOG-MESSAGE]\n
```

@}
[![progress-banner](https://backend.codecrafters.io/progress/redis/f0493a36-5fcd-4a1f-ad72-44c9d538c026)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

This is a starting point for
"Build Your Own Redis" 

## Why did I build a redis clone?
I built this project to get a complete understanding of Redis right from the socket calls of selectors at the OS level which Redis uses for asynchronous communication to the high level structuring and design best practices for writing a full fledged python project along with testing and and logging. Distributed systems is something that I am absoultely in love with and this project was made to take me one step closer to my goal of becoming a great backend developer.


## 📖 Usage

Available Commands:

* 'PING' - Ping the server
* 'ECHO' - Echo a message to the server
* 'GET' - get value stored in the Database associated with a given key
* 'SET' - set value stored in the Database for a given key
* 'CONFIGGET' - get the directory or the file name for the given RDB snapshot file
* 'KEYS' - Read keys from the rdb file based on the regex provided
* 'INFO' - Gives the info of the specified parameter (works for "--replication" for now)

## Examples

Get the rdb file's directory

```bash
CONFIGGET --dir
```

Get key valeus from the rdb file

```bash
KEYS *
```
## 🤝 Contributing

### Clone the repo

```bash
git clone https://github.com/shreyasganesh0/Redis-clone
cd Redis-clone
```


### Run the project

```bash
./your_program.sh
```

### Run the tests

local testing to be implmented once the project is stable

```bash
codecrafter test
```

### Submit a pull request

If you'd like to contribute, please fork the repository and open a pull request to the `main` branch.

# Troubleshooting

## module `socket` has no attribute `create_server`

When running your server locally, you might see an error like this:

```
Traceback (most recent call last):
  File "/.../python3.7/runpy.py", line 193, in _run_module_as_main
    "__main__", mod_spec)
  File "/.../python3.7/runpy.py", line 85, in _run_code
    exec(code, run_globals)
  File "/app/app/main.py", line 11, in <module>
    main()
  File "/app/app/main.py", line 6, in main
    s = socket.create_server(("localhost", 6379), reuse_port=True)
AttributeError: module 'socket' has no attribute 'create_server'
```

This is because `socket.create_server` was introduced in Python 3.8, and you
might be running an older version.

You can fix this by installing Python 3.8 locally and using that.

Adding link to the live document in which all learnings were updated as I coded this. ["Implementation detailed doc"](https://docs.google.com/document/d/e/2PACX-1vSqUDVC1HJPQDn1d9Vd936IpVp22T86iKh8bRbKiO4wUDwb1szyqD5fInpLv-6snrxo7TCcuKNbKudf/pub)

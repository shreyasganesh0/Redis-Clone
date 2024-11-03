[![progress-banner](https://backend.codecrafters.io/progress/redis/f0493a36-5fcd-4a1f-ad72-44c9d538c026)](https://app.codecrafters.io/users/codecrafters-bot?r=2qF)

This is a starting point for
"Build Your Own Redis" 

## Why did I build a redis clone?
I built this project to get a complete understanding of Redis right from the socket calls of selectors at the OS level which Redis uses for asynchronous communication to the high level structuring and design best practices for writing a full fledged python project along with testing and and logging. Distributed systems is something that I am absoultely in love with and this project was made to take me one step closer to my goal of becoming a great backend developer.

# Requirements

1. Ensure you have `python (3.x)` installed locally
1. Run `./your_program.sh` to run the Redis server, which is implemented in
   `app/main.py`.

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

# Interop
our interop code, not theirs

[Interop Docs](https://auvsi-suas-competition-interoperability-system.readthedocs.org/en/latest/integration/hints.html)

###Client Program checklist:

- [X] allow mission planner integration

- [ ] tested for 1Hz update rate

- [X] catches server failures

- [ ] re-logins if necessary
- No cookie found, tried restarting server and it didn't require a re login

- [X] multi-threaded

- [X] mission planner client program

- [ ] Nagle's Algorithm
- Wait until testing to see if it is necessary. This is NOT an "easy" option to change for some reason. It may also already be off.

- [ ] After dropping a certain amount of data, ask to reenter server address and/or relogin. Alternatively, allow a user to stop the constant dropping manually at any point (possibly multithread?)

- [ ] Cover the concurrency and requests errors.

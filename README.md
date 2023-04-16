[![Test](https://github.com/why-not-try-calmer/pop-bot/actions/workflows/test.yml/badge.svg)](https://github.com/why-not-try-calmer/pop-bot/actions/workflows/test.yml) [![Publish](https://github.com/why-not-try-calmer/pop-bot/actions/workflows/publish.yml/badge.svg)](https://github.com/why-not-try-calmer/pop-bot/actions/workflows/publish.yml)

## About
This repository implements a minimal [Telegram bot](https://t.me/pop_os_bot). It is an experiment for providing users with a concrete point of reference when supporting them over Telegram.

Since the bot has access to an out-of-the-box installment of Pop!, it can help them find meaningful differences with their configuration. It can also be used to demo commands and illustrate answers to technical questions.

To be sure, there is nothing special about this bot or the code in here; the only original thing is that it uses a custom docker image of [Pop!_OS](https://pop.system76.com). The image uses [an image](https://hub.docker.com/repository/docker/nycticoracs/pop_os) made for this purpose as a base.

## Tests
Test with

    python3 -m pytest test -v -s

Tests will run as-is if you happen to run them on Ubuntu. Else remove those whose requirements you cannot meet.

## Profile while testing
Profile while testing with:

    python3 -m cProfile -o profile -m pytest test -s

Then `cd` to `scripts` an analyse with

    python3 analyse.py profile
.

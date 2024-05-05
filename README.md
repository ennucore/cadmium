# Cadmium

[![GitHub Repo stars](https://img.shields.io/github/stars/ennucore/cadmium?style=social)](https://github.com/ennucore/cadmium)
[![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/ennucore/cadmium)](https://github.com/ennucore/cadmium/issues)
[![Twitter Follow](https://img.shields.io/twitter/follow/ennucore?style=social)](https://twitter.com/ennucore)

_CAD models at the speed of thought (or, you know, GPT-4)_


## Getting Started
```bash
$ git clone git@github.com:ennucore/cadmium.git
$ cd cadmium
$ conda env create -f environment.yml -n cadmium
$ conda activate cadmium
$ cp .env.example .env
```

After that, edit `.env` to include your [OpenRouter](https://openrouter.ai/) key. That key is sufficient.

You can also use an OpenAI key, but this is less tested.

Then, to run (if you have conda activated):
```bash
$ python cadmium
Enter a prompt for the agent: 
```

You might need to use `conda run --no-capture-output python cadmium` if you don't have conda properly activated.

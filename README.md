# ReCaptcha Breaker

Humanising bots for Google ReCaptcha

Get selenium installed

```sh
pip install -r requirements.txt
```

Get the geckodriver from [the official release](https://github.com/mozilla/geckodriver/releases) (32 bit or 64 bit depending on your system)

Update your firefox install if your selenium install is not compatible with it  
Make sure to close firefox before updating

```sh
sudo apt-get update
sudo apt-get install firefox
```

If you are unsure which driver version is compatible with selenium check the [selenium changelog](https://github.com/SeleniumHQ/selenium/blob/master/dotnet/CHANGELOG)

Semantic textual similarity is calculated by querying the UMBC Semantic Similarity service

The following [paper](http://ebiquity.umbc.edu/_file_directory_/papers/674.pdf) describes the approach

>Lushan Han, Abhay L. Kashyap, Tim Finin, James Mayfield and Johnathan Weese, UMBC_EBIQUITY-CORE: Semantic Textual Similarity Systems, Proc. 2nd Joint Conf. on Lexical and Computational Semantics, Association for Computational Linguistics, June 2013

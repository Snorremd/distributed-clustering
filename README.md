# distributed-clustering

A project implementing a distributed form of clustering for the compact trie clustering algorithm.

## General description
The project consists of three main parts: a corpus processor, a server and a client. The corpus processor
implements functionality for reading corpus files and generating an xml file where all snippets are encoded
as elements with appropriate tags. The server implements the genetic algorithm which is used to generate chromosomes
that act as the compact trie clustering algorithm parameters. The server send these chromosomes to clients which
implements the compact trie clustering algorithm itself.

### Corpus Processor

### Server

### Client

## Dependencies
 * Python 2.7 - The code has been coded to work with Python 2.7. Older versions are untested. Python 3 is not supported.
 * LXML - The lxml library is an alternative to the xml package. If not included in your Python distribution it can be
          installed by using pip install lxml (if you do not have pip, see http://lxml.de/installation.html).

# License

The MIT License (MIT)

Copyright (c) 2014 Snorre Magnus Davøen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

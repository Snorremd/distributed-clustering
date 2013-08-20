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

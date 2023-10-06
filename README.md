# Amaranth stuff by Sporniket

> [WARNING] Please read carefully this note before using this project. It contains important facts.

Content

1. What is **Amaranth stuff by Sporniket**, and when to use it ?
2. What should you know before using **Amaranth stuff by Sporniket** ?
3. How to use **Amaranth stuff by Sporniket** ?
4. Known issues
5. Miscellanous

## 1. What is **Amaranth stuff by Sporniket**, and when to use it ?

**Amaranth stuff by Sporniket** is my collection of essential code written using the **Amaranth hdl**.

[Amaranth HDL, previously nMigen](https://github.com/amaranth-lang/amaranth) is a python library to generate an abstract syntax tree of an hardware design, in order to e.g. configure a supported FPGA.

**Amaranth stuff by Sporniket** aims at :

* Providing some reusable basic design to build more complex systems.
* Providing a helper library to —hopefully— write formal verification tests more easily.
* Serves as dependency manager toward the mains amaranth libraries (`amaranth` and `amaranth-boards`) by the way of transitive dependencies.


### Licence
 **Amaranth stuff by Sporniket** is free software: you can redistribute it and/or modify it under the terms of the
 GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
 option) any later version.

 **Amaranth stuff by Sporniket** is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
 even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for
 more details.

 You should have received a copy of the GNU Lesser General Public License along with **Amaranth stuff by Sporniket**.
 If not, see http://www.gnu.org/licenses/ .


## 2. What should you know before using **Amaranth stuff by Sporniket** ?

**Amaranth stuff by Sporniket** requires a set of tools to work :

* **Python 3.9 or 3.10, pip and pdm**.

* Amaranth main libraries.
  * [amaranth](https://github.com/amaranth-lang/amaranth).
  * [amaranth-boards](https://github.com/amaranth-lang/amaranth-boards).

> Do not use **Amaranth stuff by Sporniket** if this project is not suitable for your project

## 3. How to use **Amaranth stuff by Sporniket** ?

### As a dependency in your python project

> It is expected that a compatible version of python is used

In your project descriptor (`pyproject.toml` file), add a dependency pointing to this repository, optionnally with a specific hash (better for build stability, requires manual updating), e.g.

    'amaranth-stuff-by-sporniket @ git+https://github.com/sporniket/amaranth-stuff@a738ace61839390dfdaa8ef06baa17d32482d771',

A build tool like [pdm](https://pdm.fming.dev) can be used to manage dependencies in a normalized manner.

### Working on the sources

> It is expected that a compatible version of python is used, and that pip and pdm are also installed.

	git clone https://github.com/sporniket/amaranth-stuff.git
	cd amaranth-stuff
    python3 -m pdm sync
    python3 -m pdm ci

## 4. Known issues
See the [project issues](https://github.com/sporniket/amaranth-stuff/issues) page.

## 5. Miscellanous

### Report issues
Use the [project issues](https://github.com/sporniket/amaranth-stuff/issues) page.

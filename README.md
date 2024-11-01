File Factory is a utility library for easily and safely opening resources without needing to know their absolute path.

Internally it relies on importlib's `as_files` and `files` methods. It converts them to pathlib `Paths` before operating on them.

FileFactory's name sake comes from the factory objects which provide configurable `__call__` methods. This allows the user to create the
link to specific locations and file formats once and then re-use it over and over in their applications.

Use any of this code without attribution, but a shout-out would be appreciated!
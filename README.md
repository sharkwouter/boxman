# Boxman

Boxman is a WIP package manager compatible with pacman repositories which works with relative paths. Install Boxman into your project and it will be able to manage packages for you there and only there. It made for managing libraries in development kits.

**Note: Boxman is still very much WIP! Use at your own risk!**

## Usage

Boxman supports the following commands:

```bash
boxman install package1 package2  # Install packages
boxman update  # Update all installed packages or add package names to update specific ones
boxman remove package1 package2  # Remove packages
boxman search package  # Search for packages with a specific string in their name
boxman show package  # Print information about a package
boxman list  # Print a list of available packages
boxman installed  # Print a list of installed packages
boxman files  # Print a list of installed file_list
boxman config  # Print the configuration
```

## Configuration

Boxman expects the configuration to be in `etc/boxman.conf` (relative where it's installed) and uses a similar format to pacman.

Example for the PSPDEV repository:
```ini
[options]
RootDir     = $PSPDEV
DBPath      = var/lib/pacman
CacheDir    = var/cache/pacman

[pspdev]
Server = https://github.com/pspdev/psp-packages/releases/latest/download/
```

By default `RootDir` is not set, `DBPATH` is set to `var/lib/boxman` and `CacheDir` is set to `var/cache/boxman/pkg`. Absolute paths are not supported.

For repositories the repository name is put in brackets with the server url below it with `Server = url`. Multiple repositories can be addded.

## Dependencies

Boxman only requires Python 3.7 or newer.

Boxman should work on any current computer operating system.

## Installation

Currently, boxman does not have an installation method yet.

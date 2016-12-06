from first import first
import click
import re

VALID_TEXT = re.compile('^[0-9A-Za-z\-\.]$')


class SemVer(object):

  __slots__ = [
    'major',
    'minor',
    'patch',
    'pre',
    'build',
  ]

  def __init__(self, **kwargs):
    for n in self.__slots__:
      setattr(self, n, kwargs.get(n))

  def __repr__(self):
    return "<SemVer {}>".format(
      ", ".join([
        "{}={}".format(n, getattr(self, n))
        for n in self.__slots__
      ]))

  def __str__(self):
    version_string = ".".join(map(str,
      [self.major, self.minor, self.patch]))
    if self.pre:
      version_string += "-" + self.pre
    if self.build:
      version_string += "+" + self.build
    return version_string

  @classmethod
  def parse(cls, version):
    major = minor = patch = 0
    build = pre = None
    build_split = version.split('+')
    if len(build_split) > 1:
      version, build = build_split
    pre_split = version.split('-', 1)
    if len(pre_split) > 1:
      version, pre = pre_split
    major_split = version.split('.', 1)
    if len(major_split) > 1:
      major, version = major_split
      minor_split = version.split(b'.', 1)
      if len(minor_split) > 1:
        minor, version = minor_split
        if version:
          patch = version
      else:
        minor = version
    else:
      major = version
    return cls(
      major=int(major),
      minor=int(minor),
      patch=int(patch),
      pre=pre,
      build=build,
    )

  def bump(self, major, minor, patch, pre=None, build=None, **kwargs):
    if major:
      self.major += 1
    elif minor:
      self.minor += 1
    elif patch:
      self.patch += 1
    self.pre = pre
    self.build = build


@click.command()
@click.option('--major', '-M', 'major', flag_value=True,
              help="Bump major number", default=False)
@click.option('--minor', '-m', 'minor', flag_value=True,
              help="Bump minor number", default=False)
@click.option('--patch', '-p', 'patch', flag_value=True,
              help="Bump patch number", default=True)
@click.option('--pre', help="Set pre-release identifier")
@click.option('--build', help="Set build metadata")
@click.argument('input', type=click.File('rb'), default="setup.py")
@click.argument('output', type=click.File('wb'), default="setup.py")
def main(input, output, **kwargs):
  contents = input.read()
  pattern = r'(\n__version__ ?= ?[\'"])(.+?)([\'"]\n)'
  version_string = first(re.findall(pattern, contents))[1]
  version = SemVer.parse(version_string)
  version.bump(**kwargs)
  click.echo(version)


if __name__ == '__main__':
  main()

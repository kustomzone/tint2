#!/usr/bin/env python
import optparse
import os
import pprint
import re
import shlex
import subprocess
import sys

CC = os.environ.get('CC', 'cc')

root_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(root_dir, '..', 'libraries', 'node', 'tools', 'gyp', 'pylib'))
from gyp.common import GetFlavor

# parse our options
parser = optparse.OptionParser()

parser.add_option("--debug",
    action="store_true",
    dest="debug",
    help="Also build debug build")


parser.add_option("--subsystem",
    action="store",
    dest="subsystem",
    help="The subsystemf or windows to use, either console or windows.")

parser.add_option("--prefix",
    action="store",
    dest="prefix",
    help="Select the install prefix (defaults to /usr/local)")

parser.add_option("--without-npm",
    action="store_true",
    dest="without_npm",
    help="Don\'t install the bundled npm package manager")

parser.add_option("--without-ssl",
    action="store_true",
    dest="without_ssl",
    help="Build without SSL")

parser.add_option("--without-snapshot",
    action="store_true",
    dest="without_snapshot",
    help="Build without snapshotting V8 libraries. You might want to set"
         " this for cross-compiling. [Default: False]")

parser.add_option("--shared-v8",
    action="store_true",
    dest="shared_v8",
    help="Link to a shared V8 DLL instead of static linking")

parser.add_option("--shared-v8-includes",
    action="store",
    dest="shared_v8_includes",
    help="Directory containing V8 header files")

parser.add_option("--shared-v8-libpath",
    action="store",
    dest="shared_v8_libpath",
    help="A directory to search for the shared V8 DLL")

parser.add_option("--shared-v8-libname",
    action="store",
    dest="shared_v8_libname",
    help="Alternative lib name to link to (default: 'v8')")

parser.add_option("--shared-openssl",
    action="store_true",
    dest="shared_openssl",
    help="Link to a shared OpenSSl DLL instead of static linking")

parser.add_option("--shared-openssl-includes",
    action="store",
    dest="shared_openssl_includes",
    help="Directory containing OpenSSL header files")

parser.add_option("--shared-openssl-libpath",
    action="store",
    dest="shared_openssl_libpath",
    help="A directory to search for the shared OpenSSL DLLs")

parser.add_option("--shared-openssl-libname",
    action="store",
    dest="shared_openssl_libname",
    help="Alternative lib name to link to (default: 'crypto,ssl')")

# deprecated
parser.add_option("--openssl-use-sys",
    action="store_true",
    dest="shared_openssl",
    help=optparse.SUPPRESS_HELP)

# deprecated
parser.add_option("--openssl-includes",
    action="store",
    dest="shared_openssl_includes",
    help=optparse.SUPPRESS_HELP)

# deprecated
parser.add_option("--openssl-libpath",
    action="store",
    dest="shared_openssl_libpath",
    help=optparse.SUPPRESS_HELP)

# TODO document when we've decided on what the tracing API and its options will
# look like
parser.add_option("--systemtap-includes",
    action="store",
    dest="systemtap_includes",
    help=optparse.SUPPRESS_HELP)

parser.add_option("--no-ssl2",
    action="store_true",
    dest="no_ssl2",
    help="Disable OpenSSL v2")

parser.add_option("--shared-zlib",
    action="store_true",
    dest="shared_zlib",
    help="Link to a shared zlib DLL instead of static linking")

parser.add_option("--shared-zlib-includes",
    action="store",
    dest="shared_zlib_includes",
    help="Directory containing zlib header files")

parser.add_option("--shared-zlib-libpath",
    action="store",
    dest="shared_zlib_libpath",
    help="A directory to search for the shared zlib DLL")

parser.add_option("--shared-zlib-libname",
    action="store",
    dest="shared_zlib_libname",
    help="Alternative lib name to link to (default: 'z')")

parser.add_option("--shared-http-parser",
    action="store_true",
    dest="shared_http_parser",
    help="Link to a shared http_parser DLL instead of static linking")

parser.add_option("--shared-http-parser-includes",
    action="store",
    dest="shared_http_parser_includes",
    help="Directory containing http_parser header files")

parser.add_option("--shared-http-parser-libpath",
    action="store",
    dest="shared_http_parser_libpath",
    help="A directory to search for the shared http_parser DLL")

parser.add_option("--shared-http-parser-libname",
    action="store",
    dest="shared_http_parser_libname",
    help="Alternative lib name to link to (default: 'http_parser')")

parser.add_option("--shared-cares",
    action="store_true",
    dest="shared_cares",
    help="Link to a shared cares DLL instead of static linking")

parser.add_option("--shared-cares-includes",
    action="store",
    dest="shared_cares_includes",
    help="Directory containing cares header files")

parser.add_option("--shared-cares-libpath",
    action="store",
    dest="shared_cares_libpath",
    help="A directory to search for the shared cares DLL")

parser.add_option("--shared-cares-libname",
    action="store",
    dest="shared_cares_libname",
    help="Alternative lib name to link to (default: 'cares')")

parser.add_option("--shared-libuv",
    action="store_true",
    dest="shared_libuv",
    help="Link to a shared libuv DLL instead of static linking")

parser.add_option("--shared-libuv-includes",
    action="store",
    dest="shared_libuv_includes",
    help="Directory containing libuv header files")

parser.add_option("--shared-libuv-libpath",
    action="store",
    dest="shared_libuv_libpath",
    help="A directory to search for the shared libuv DLL")

parser.add_option("--shared-libuv-libname",
    action="store",
    dest="shared_libuv_libname",
    help="Alternative lib name to link to (default: 'uv')")

parser.add_option("--with-dtrace",
    action="store_true",
    dest="with_dtrace",
    help="Build with DTrace (default is true on sunos)")

parser.add_option("--without-dtrace",
    action="store_true",
    dest="without_dtrace",
    help="Build without DTrace")

parser.add_option("--with-etw",
    action="store_true",
    dest="with_etw",
    help="Build with ETW (default is true on Windows)")

parser.add_option("--without-etw",
    action="store_true",
    dest="without_etw",
    help="Build without ETW")

parser.add_option("--with-perfctr",
    action="store_true",
    dest="with_perfctr",
    help="Build with performance counters (default is true on Windows)")

parser.add_option("--without-perfctr",
    action="store_true",
    dest="without_perfctr",
    help="Build without performance counters")

# CHECKME does this still work with recent releases of V8?
parser.add_option("--gdb",
    action="store_true",
    dest="gdb",
    help="add gdb support")

parser.add_option("--dest-cpu",
    action="store",
    dest="dest_cpu",
    help="CPU architecture to build for. Valid values are: arm, ia32, x64")

parser.add_option("--dest-os",
    action="store",
    dest="dest_os",
    help="Operating system to build for. Valid values are: "
         "win, mac, solaris, freebsd, openbsd, linux")

parser.add_option("--no-ifaddrs",
    action="store_true",
    dest="no_ifaddrs",
    help="Use on deprecated SunOS systems that do not support ifaddrs.h")

parser.add_option("--with-arm-float-abi",
    action="store",
    dest="arm_float_abi",
    help="Specifies which floating-point ABI to use. Valid values are: "
         "soft, softfp, hard")

parser.add_option("--with-mips-float-abi",
    action="store",
    dest="mips_float_abi",
    help="Specifies which floating-point ABI to use. Valid values are: "
         "soft, hard")

parser.add_option("--ninja",
    action="store_true",
    dest="use_ninja",
    help="Generate files for the ninja build system")

# Using --unsafe-optimizations voids your warranty.
parser.add_option("--unsafe-optimizations",
    action="store_true",
    dest="unsafe_optimizations",
    help=optparse.SUPPRESS_HELP)

parser.add_option("--xcode",
    action="store_true",
    dest="use_xcode",
    help="Generate build files for use with xcode")

parser.add_option("--tag",
    action="store",
    dest="tag",
    help="Custom build tag")

(options, args) = parser.parse_args()


def b(value):
  """Returns the string 'true' if value is truthy, 'false' otherwise."""
  if value:
    return 'true'
  else:
    return 'false'


def pkg_config(pkg):
  cmd = os.popen('pkg-config --libs %s' % pkg, 'r')
  libs = cmd.readline().strip()
  ret = cmd.close()
  if (ret): return None

  cmd = os.popen('pkg-config --cflags %s' % pkg, 'r')
  cflags = cmd.readline().strip()
  ret = cmd.close()
  if (ret): return None

  return (libs, cflags)


def cc_macros():
  """Checks predefined macros using the CC command."""

  try:
    p = subprocess.Popen(shlex.split(CC) + ['-dM', '-E', '-'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
  except OSError:
    print '''Node.js configure error: No acceptable C compiler found!

        Please make sure you have a C compiler installed on your system and/or
        consider adjusting the CC environment variable if you installed
        it in a non-standard prefix.
        '''
    sys.exit()

  p.stdin.write('\n')
  out = p.communicate()[0]

  out = str(out).split('\n')

  k = {}
  for line in out:
    lst = shlex.split(line)
    if len(lst) > 2:
      key = lst[1]
      val = lst[2]
      k[key] = val
  return k


def is_arch_armv7():
  """Check for ARMv7 instructions"""
  cc_macros_cache = cc_macros()
  return ('__ARM_ARCH_7__' in cc_macros_cache or
          '__ARM_ARCH_7A__' in cc_macros_cache or
          '__ARM_ARCH_7R__' in cc_macros_cache or
          '__ARM_ARCH_7M__' in cc_macros_cache)


def is_arm_neon():
  """Check for ARM NEON support"""
  return '__ARM_NEON__' in cc_macros()


def arm_hard_float_abi():
  """Check for hardfloat or softfloat eabi on ARM"""
  # GCC versions 4.6 and above define __ARM_PCS or __ARM_PCS_VFP to specify
  # the Floating Point ABI used (PCS stands for Procedure Call Standard).
  # We use these as well as a couple of other defines to statically determine
  # what FP ABI used.
  # GCC versions 4.4 and below don't support hard-fp.
  # GCC versions 4.5 may support hard-fp without defining __ARM_PCS or
  # __ARM_PCS_VFP.

  if compiler_version() >= (4, 6, 0):
    return '__ARM_PCS_VFP' in cc_macros()
  elif compiler_version() < (4, 5, 0):
    return False
  elif '__ARM_PCS_VFP' in cc_macros():
    return True
  elif ('__ARM_PCS' in cc_macros() or
        '__SOFTFP' in cc_macros() or
        not '__VFP_FP__' in cc_macros()):
    return False
  else:
    print '''Node.js configure error: Your version of GCC does not report
      the Floating-Point ABI to compile for your hardware

      Please manually specify which floating-point ABI to use with the
      --with-arm-float-abi option.
      '''
    sys.exit()


def host_arch_cc():
  """Host architecture check using the CC command."""

  k = cc_macros()

  matchup = {
    '__x86_64__'  : 'x64',
    '__i386__'    : 'x64',
    '__arm__'     : 'arm',
    '__mips__'    : 'mips',
  }

  rtn = 'ia32' # default

  for i in matchup:
    if i in k and k[i] != '0':
      rtn = matchup[i]
      break

  return rtn


def host_arch_win():
  """Host architecture check using environ vars (better way to do this?)"""

  arch = os.environ.get('PROCESSOR_ARCHITECTURE', 'x86')
  print('found arch: '+arch);
  matchup = {
    'AMD64'  : 'x64',
    'x86'    : 'x64',
    'arm'    : 'arm',
    'mips'   : 'mips',
  }

  return matchup.get(arch, 'x64')


def compiler_version():
  try:
    proc = subprocess.Popen(shlex.split(CC) + ['--version'], stdout=subprocess.PIPE)
  except WindowsError:
    return (0, False)

  is_clang = 'clang' in proc.communicate()[0].split('\n')[0]

  proc = subprocess.Popen(shlex.split(CC) + ['-dumpversion'], stdout=subprocess.PIPE)
  version = tuple(map(int, proc.communicate()[0].split('.')))

  return (version, is_clang)


def configure_arm(o):
  # V8 on ARM requires that armv7 is set. CPU Model detected by
  # the presence of __ARM_ARCH_7__ and the like defines in compiler
  if options.arm_float_abi:
    hard_float = options.arm_float_abi == 'hard'
  else:
    hard_float = arm_hard_float_abi()

  armv7 = is_arch_armv7()
  # CHECKME VFPv3 implies ARMv7+ but is the reverse true as well?
  fpu = 'vfpv3' if armv7 else 'vfpv2'

  o['variables']['armv7'] = int(armv7)
  o['variables']['arm_fpu'] = fpu
  o['variables']['arm_neon'] = int(is_arm_neon())
  o['variables']['v8_use_arm_eabi_hardfloat'] = b(hard_float)


def configure_mips(o):
  if options.mips_float_abi:
    if options.mips_float_abi in ('soft', 'hard'):
      o['variables']['v8_use_mips_abi_hardfloat'] = b(
          options.mips_float_abi == 'hard')
    else:
      raise Exception(
          'Invalid mips-float-abi value. Valid values are: soft, hard')


def configure_node(o):
  o['variables']['v8_enable_gdbjit'] = 1 if options.gdb else 0
  o['variables']['v8_no_strict_aliasing'] = 1 # work around compiler bugs
  o['variables']['node_prefix'] = os.path.expanduser(options.prefix or '')
  o['variables']['node_install_npm'] = b(not options.without_npm)
  o['variables']['node_unsafe_optimizations'] = (
    1 if options.unsafe_optimizations else 0)
  o['default_configuration'] = 'Debug' if options.debug else 'Release'
  print(' os.name is: '+os.name);
  host_arch = host_arch_win() if os.name == 'nt' else host_arch_cc()
  target_arch = options.dest_cpu or host_arch
  o['variables']['host_arch'] = host_arch
  o['variables']['target_arch'] = target_arch

  if target_arch == 'arm':
    configure_arm(o)
  elif target_arch in ('mips', 'mipsel'):
    configure_mips(o)

  cc_version, is_clang = compiler_version()
  o['variables']['clang'] = 1 if is_clang else 0

  if not is_clang and cc_version != 0:
    o['variables']['gcc_version'] = 10 * cc_version[0] + cc_version[1]

  # clang has always supported -fvisibility=hidden, right?
  if not is_clang and cc_version < (4,0,0):
    o['variables']['visibility'] = ''

  # By default, enable DTrace on SunOS systems. Don't allow it on other
  # systems, since it won't work.  (The MacOS build process is different than
  # SunOS, and we haven't implemented it.)
  if flavor in ('solaris', 'mac'):
    o['variables']['node_use_dtrace'] = b(not options.without_dtrace)
  elif flavor == 'linux':
    o['variables']['node_use_dtrace'] = 'false'
    o['variables']['node_use_systemtap'] = b(options.with_dtrace)
    if options.systemtap_includes:
      o['include_dirs'] += [options.systemtap_includes]
  elif options.with_dtrace:
    raise Exception(
       'DTrace is currently only supported on SunOS, MacOS or Linux systems.')
  else:
    o['variables']['node_use_dtrace'] = 'false'
    o['variables']['node_use_systemtap'] = 'false'

  if options.no_ifaddrs:
    o['defines'] += ['SUNOS_NO_IFADDRS']

  # By default, enable ETW on Windows.
  if flavor == 'win':
    o['variables']['node_use_etw'] = b(not options.without_etw);
  elif options.with_etw:
    raise Exception('ETW is only supported on Windows.')
  else:
    o['variables']['node_use_etw'] = 'false'

  # By default, enable Performance counters on Windows.
  if flavor == 'win':
    o['variables']['node_use_perfctr'] = b(not options.without_perfctr);
  elif options.with_perfctr:
    raise Exception('Performance counter is only supported on Windows.')
  else:
    o['variables']['node_use_perfctr'] = 'false'

  if options.tag:
    o['variables']['node_tag'] = '-' + options.tag
  else:
    o['variables']['node_tag'] = ''


def configure_libz(o):
  o['variables']['node_shared_zlib'] = b(options.shared_zlib)

  # assume shared_zlib if one of these is set?
  if options.shared_zlib_libpath:
    o['libraries'] += ['-L%s' % options.shared_zlib_libpath]
  if options.shared_zlib_libname:
    o['libraries'] += ['-l%s' % options.shared_zlib_libname]
  elif options.shared_zlib:
    o['libraries'] += ['-lz']
  if options.shared_zlib_includes:
    o['include_dirs'] += [options.shared_zlib_includes]


def configure_http_parser(o):
    o['variables']['node_shared_http_parser'] = b(options.shared_http_parser)

    # assume shared http_parser if one of these is set?
    if options.shared_http_parser_libpath:
        o['libraries'] += ['-L%s' % options.shared_http_parser_libpath]
    if options.shared_http_parser_libname:
        o['libraries'] += ['-l%s' % options.shared_http_parser_libname]
    elif options.shared_http_parser:
        o['libraries'] += ['-lhttp_parser']
    if options.shared_http_parser_includes:
        o['include_dirs'] += [options.shared_http_parser_includes]


def configure_cares(o):
    o['variables']['node_shared_cares'] = b(options.shared_cares)

    # assume shared cares if one of these is set?
    if options.shared_cares_libpath:
        o['libraries'] += ['-L%s' % options.shared_cares_libpath]
    if options.shared_cares_libname:
        o['libraries'] += ['-l%s' % options.shared_cares_libname]
    elif options.shared_cares:
        o['libraries'] += ['-lcares']
    if options.shared_cares_includes:
        o['include_dirs'] += [options.shared_cares_includes]


def configure_libuv(o):
  o['variables']['node_shared_libuv'] = b(options.shared_libuv)

  # assume shared libuv if one of these is set?
  if options.shared_libuv_libpath:
    o['libraries'] += ['-L%s' % options.shared_libuv_libpath]
  if options.shared_libuv_libname:
    o['libraries'] += ['-l%s' % options.shared_libuv_libname]
  elif options.shared_libuv:
    o['libraries'] += ['-luv']
  if options.shared_libuv_includes:
    o['include_dirs'] += [options.shared_libuv_includes]


def configure_v8(o):
  o['variables']['v8_use_snapshot'] = b(not options.without_snapshot)
  o['variables']['node_shared_v8'] = b(options.shared_v8)

  # assume shared_v8 if one of these is set?
  if options.shared_v8_libpath:
    o['libraries'] += ['-L%s' % options.shared_v8_libpath]
  if options.shared_v8_libname:
    o['libraries'] += ['-l%s' % options.shared_v8_libname]
  elif options.shared_v8:
    o['libraries'] += ['-lv8']
  if options.shared_v8_includes:
    o['include_dirs'] += [options.shared_v8_includes]


def configure_openssl(o):
  o['variables']['node_use_openssl'] = b(not options.without_ssl)
  o['variables']['node_shared_openssl'] = b(options.shared_openssl)

  if options.without_ssl:
    return

  if options.no_ssl2:
    o['defines'] += ['OPENSSL_NO_SSL2=1']

  if options.shared_openssl:
    (libs, cflags) = pkg_config('openssl') or ('-lssl -lcrypto', '')

    if options.shared_openssl_libpath:
      o['libraries'] += ['-L%s' % options.shared_openssl_libpath]

    if options.shared_openssl_libname:
      libnames = options.shared_openssl_libname.split(',')
      o['libraries'] += ['-l%s' % s for s in libnames]
    else:
      o['libraries'] += libs.split()

    if options.shared_openssl_includes:
      o['include_dirs'] += [options.shared_openssl_includes]
    else:
      o['cflags'] += cflags.split()


def configure_winsdk(o):
  if flavor != 'win':
    return

  winsdk_dir = os.environ.get("WindowsSdkDir")

  if winsdk_dir and os.path.isfile(winsdk_dir + '\\bin\\ctrpp.exe'):
    print "Found ctrpp in WinSDK--will build generated files into tools/msvs/genfiles."
    o['variables']['node_has_winsdk'] = 'true'
    return

  print "ctrpp not found in WinSDK path--using pre-gen files from tools/msvs/genfiles."


# determine the "flavor" (operating system) we're building for,
# leveraging gyp's GetFlavor function
flavor_params = {};
if (options.dest_os):
  flavor_params['flavor'] = options.dest_os;
flavor = GetFlavor(flavor_params);

output = {
  'variables': { 'python': sys.executable, 'win_subsystem': options.subsystem },
  'include_dirs': [],
  'libraries': [],
  'defines': [],
  'cflags': [],
}

configure_node(output)
configure_libz(output)
configure_http_parser(output)
configure_cares(output)
configure_libuv(output)
configure_v8(output)
configure_openssl(output)
configure_winsdk(output)

# variables should be a root level element,
# move everything else to target_defaults
variables = output['variables']
del output['variables']
output = {
  'variables': variables,
  'target_defaults': output
}
pprint.pprint(output, indent=2)

def write(filename, data):
  filename = os.path.join(root_dir, filename)
  print "creating ", filename
  f = open(filename, 'w+')
  f.write(data)

write('../libraries/node/config.gypi', "# Do not edit. Generated by the configure script.\n" +
  pprint.pformat(output, indent=2) + "\n")

config = {
  'BUILDTYPE': 'Debug' if options.debug else 'Release',
  'USE_NINJA': str(int(options.use_ninja or 0)),
  'USE_XCODE': str(int(options.use_xcode or 0)),
  'PYTHON': sys.executable,
}
config = '\n'.join(map('='.join, config.iteritems())) + '\n'

write('../libraries/node/config.mk',
      '# Do not edit. Generated by the configure script.\n' + config)

if options.use_ninja:
  gyp_args = ['-f', 'ninja-' + flavor]
elif options.use_xcode:
  gyp_args = ['-f', 'xcode']
elif flavor == 'win':
  gyp_args = ['-f', 'msvs', '-G', 'msvs_version=auto']
else:
  gyp_args = ['-f', 'make-' + flavor]

subprocess.call([sys.executable, 'tools/gyp_tint'] + gyp_args)

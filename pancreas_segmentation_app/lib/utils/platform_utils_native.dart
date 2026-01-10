import 'dart:io' show Platform;

/// Native platform implementation
bool isDesktopPlatformImpl() {
  return Platform.isWindows || Platform.isLinux || Platform.isMacOS;
}

bool isMobilePlatformImpl() {
  return Platform.isAndroid || Platform.isIOS;
}

String getPathSeparatorImpl() {
  return Platform.pathSeparator;
}

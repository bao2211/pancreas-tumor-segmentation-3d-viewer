import 'package:flutter/foundation.dart' show kIsWeb;
import 'platform_utils_native.dart'
    if (dart.library.html) 'platform_utils_web.dart' as platform_impl;

/// Platform detection utilities that work on all platforms including web
class PlatformUtils {
  static bool get isWeb => kIsWeb;
  
  static bool get isDesktop {
    if (kIsWeb) return false;
    return platform_impl.isDesktopPlatformImpl();
  }
  
  static bool get isMobile {
    if (kIsWeb) return false;
    return platform_impl.isMobilePlatformImpl();
  }
  
  static String get pathSeparator {
    if (kIsWeb) return '/';
    return platform_impl.getPathSeparatorImpl();
  }
  
  /// Extract filename from path (works on all platforms)
  static String getFileName(String path) {
    final separator = path.contains('\\') ? '\\' : '/';
    return path.split(separator).last;
  }
}

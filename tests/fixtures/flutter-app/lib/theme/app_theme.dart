import 'package:flutter/material.dart';

class AppColors {
  static const Color forest = Color(0xFF2E7D32);
  static const Color sunrise = Color(0xFFFFA000);
  static const Color slate = Color(0xFF263238);
}

class AppTheme {
  static ThemeData get light => ThemeData(
        useMaterial3: true,
        fontFamily: 'Nunito',
        colorScheme: const ColorScheme(
          brightness: Brightness.light,
          primary: Color(0xFF2E7D32),
          onPrimary: Color(0xFFFFFFFF),
          secondary: Color(0xFF00695C),
          onSecondary: Color(0xFFFFFFFF),
          tertiary: Color(0xFFFFA000),
          error: Color(0xFFC62828),
          onError: Color(0xFFFFFFFF),
          surface: Color(0xFFF4F7F2),
          onSurface: Color(0xFF263238),
        ),
        scaffoldBackgroundColor: Color(0xFFFFFFFF),
      );

  static ThemeData get dark => ThemeData(
        useMaterial3: true,
        fontFamily: 'Nunito',
        brightness: Brightness.dark,
        colorSchemeSeed: Color(0xFF2E7D32),
      );
}

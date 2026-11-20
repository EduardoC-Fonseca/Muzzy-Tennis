import 'package:material_ui/material_ui.dart';

class AppTheme {
  static const Color fundoPreto = Color(0xFF1A1B1E);
  static const Color superficiePreta = Color(0xFF222325);
  static const Color verdeMuzziTennis = Color(0xFF7DC242);
  static const Color textoBranco = Color(0xFFF0F1F3);
  static const Color textoCinza = Color(0xFF8A9099);
  static const Color bordaPreta = Color(0xFF2F3134);

  static ThemeData get muzziTennisTheme {
    return ThemeData.dark().copyWith(
      scaffoldBackgroundColor: fundoPreto,
      colorScheme: const ColorScheme.dark(
        primary: verdeMuzziTennis,
        surface: superficiePreta,
        onSurface: textoBranco,
      ),
    );
  }
}
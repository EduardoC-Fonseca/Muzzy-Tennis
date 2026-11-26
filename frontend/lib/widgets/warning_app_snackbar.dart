import 'package:google_fonts/google_fonts.dart';
import 'package:material_ui/material_ui.dart';
import 'package:muzzi_tennis/core/app_theme.dart';

class AppSnackBar {
  static void sucesso(BuildContext context, String mensagem) {
    _mostrar(context, mensagem, cor: AppTheme.verdeMuzziTennis);
  }

  static void erro(BuildContext context, String mensagem) {
    _mostrar(context, mensagem, cor: AppTheme.vermelhoErro);
  }

  static void aviso(BuildContext context, String mensagem) {
    _mostrar(context, mensagem, cor: AppTheme.amareloAviso);
  }

  static void _mostrar(BuildContext context, String mensagem, {
    required Color cor,
  }) {

    final messenger = ScaffoldMessenger.of(context);
    messenger.hideCurrentSnackBar();
    messenger.showSnackBar(
      SnackBar(
        backgroundColor: AppTheme.superficiePreta,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 4),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
          side: BorderSide(
            color: cor,
            width: 1,
          ),
        ),
        content: Row(
          children: [
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                mensagem,
                style: GoogleFonts.barlow(
                  color: AppTheme.textoBranco,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

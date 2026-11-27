import 'package:google_fonts/google_fonts.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:muzzi_tennis/core/app_theme.dart';
import 'package:muzzi_tennis/services/auth_service.dart';
import 'package:muzzi_tennis/services/auth_session.dart';
import 'package:muzzi_tennis/widgets/warning_app_snackbar.dart';

class AppNavebar extends StatelessWidget {
  const AppNavebar({super.key});

  Future<void> _sair(BuildContext context) async {
    try {
      await AuthService().logout();
      AuthSession.instance.encerrarSessao();
      if (!context.mounted) return;
      Navigator.pushNamedAndRemoveUntil(
        context,
        '/login',
        (route) => false,
      );
    } 
    catch (erro) {
      if (!context.mounted) return;
      final mensagem = erro.toString().replaceFirst('Exception: ', '');
      AppSnackBar.erro(context, mensagem);
    }
  }

  @override
  Widget build(BuildContext context) {
    final rotaAtual = ModalRoute.of(context)?.settings.name ?? '/';

    void voltarInicio() {
      Navigator.of(context).popUntil((route) => route.isFirst);
    }

    void navegar(String rota) {
      if (rotaAtual != rota) {
        Navigator.pushNamedAndRemoveUntil(
          context,
          rota,
          (route) => route.isFirst,
        );
      }
    }

    final estiloNavegacao = ButtonStyle(
      textStyle: WidgetStatePropertyAll(
        GoogleFonts.barlowCondensed(
          fontSize: 16,
          fontWeight: FontWeight.w700,
          letterSpacing: 1,
        ),
      ),
      foregroundColor: WidgetStateProperty.resolveWith<Color>(
        (states) {
          if (states.contains(WidgetState.hovered)) {
            return AppTheme.verdeMuzziTennis;
          }
          return AppTheme.textoBranco;
        },
      ),
      overlayColor: const WidgetStatePropertyAll(Colors.transparent),
      backgroundColor: const WidgetStatePropertyAll(Colors.transparent),
      side: const WidgetStatePropertyAll(BorderSide.none),
    );

    return Container(
      height: 64,
      color: AppTheme.superficiePreta,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Row(
        children: [
          Expanded(
            child: Align(
              alignment: Alignment.centerLeft,
              child: InkWell(
                onTap: voltarInicio,
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SvgPicture.asset(
                      'lib/assets/muzzi_logo.svg',
                      width: 50,
                      height: 50,
                    ),
                    const SizedBox(width: 8),
                    Text.rich(
                      TextSpan(
                        children: [
                          TextSpan(
                            text: 'MUZZI ',
                            style: GoogleFonts.barlowCondensed(
                              fontSize: 24,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 1,
                              color: AppTheme.textoBranco,
                            ),
                          ),
                          TextSpan(
                            text: 'TENNIS',
                            style: GoogleFonts.barlowCondensed(
                              fontSize: 24,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 1,
                              color: AppTheme.verdeMuzziTennis,
                            ),
                          ),
                        ],
                      ),
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Expanded(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                TextButton(
                  style: estiloNavegacao,
                  onPressed: voltarInicio,
                  child: const Text('INÍCIO'),
                ),
                const SizedBox(width: 24),
                TextButton(
                  style: estiloNavegacao,
                  onPressed: () => navegar('/quadras'),
                  child: const Text('QUADRAS'),
                ),
              ],
            ),
          ),
          Expanded(
            child: AnimatedBuilder(
              animation: AuthSession.instance,
              builder: (context, child) {
                final sessao = AuthSession.instance;
                final nome = sessao.usuario?['nome']?.toString().trim() ?? '';
                final primeiroNome = nome.isEmpty ? 'Usuário' : nome.split(RegExp(r'\s+')).first;

                return Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    OutlinedButton(
                      onPressed: () => navegar(
                        sessao.autenticado ? '/cadastro-quadras' : '/login',
                      ),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.verdeMuzziTennis,
                        side: const BorderSide(
                          color: AppTheme.verdeMuzziTennis,
                        ),
                        textStyle: GoogleFonts.barlowCondensed(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: const Text('ANUNCIAR QUADRA'),
                    ),

                    const SizedBox(width: 12),
                    if (sessao.autenticado) ...[
                      ConstrainedBox(
                        constraints: const BoxConstraints(
                          maxWidth: 120,
                        ),
                        child: Text(
                          'OLÁ, ${primeiroNome.toUpperCase()}',
                          overflow: TextOverflow.ellipsis,
                          maxLines: 1,
                          style: GoogleFonts.barlow(
                            color: AppTheme.textoBranco,
                            fontSize: 14,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                    ],
                    ElevatedButton(
                      onPressed: sessao.autenticado ? () => _sair(context) : () => navegar('/login'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTheme.verdeMuzziTennis,
                        foregroundColor: AppTheme.fundoPreto,
                        textStyle: GoogleFonts.barlowCondensed(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: Text(
                        sessao.autenticado ? 'SAIR' : 'LOGIN',
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
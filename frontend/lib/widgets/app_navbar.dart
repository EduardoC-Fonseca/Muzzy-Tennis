
import 'package:material_ui/material_ui.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:muzzi_tennis/core/app_theme.dart';

class AppNavebar extends StatelessWidget {
  const AppNavebar({super.key});

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

    return Container(
      height: 64,
      color: AppTheme.fundoPreto,
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
                            style: TextStyle(
                              color: AppTheme.textoBranco,
                            ),
                          ),
                          TextSpan(
                            text: 'TENNIS',
                            style: TextStyle(
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
                  onPressed: voltarInicio,
                  child: const Text('INÍCIO'),
                ),
                const SizedBox(width: 24),
                TextButton(
                  onPressed: () => navegar('/quadras'),
                  child: const Text('QUADRAS'),
                ),
              ],
            ),
          ),
          Expanded(
            child: Align(
              alignment: Alignment.centerRight,
              child: OutlinedButton(
                onPressed: () => navegar('/cadastro'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppTheme.verdeMuzziTennis,
                  side: const BorderSide(
                    color: AppTheme.verdeMuzziTennis,
                  ),
                ),
                child: const Text('ANUNCIAR QUADRA'),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

import 'package:google_fonts/google_fonts.dart';
import 'package:material_ui/material_ui.dart';
import 'package:muzzi_tennis/core/app_theme.dart';
import 'package:muzzi_tennis/widgets/search_bar.dart';

class HeroSection extends StatelessWidget {
  const HeroSection({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
        horizontal: 48,
        vertical: 50,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'PLATAFORMA DE RESERVA DE QUADRAS',
            style: GoogleFonts.barlowCondensed(
              fontSize: 16,
              fontWeight: FontWeight.w700,
              letterSpacing: 2,
              color: AppTheme.verdeMuzziTennis,
            ),
          ),

          const SizedBox(height: 24),

          Text.rich(
            TextSpan(
              children: [
                const TextSpan(text: 'JOGUE ONDE\n'),
                TextSpan(
                  text: 'QUISER,\n',
                  style: TextStyle(
                    color: AppTheme.verdeMuzziTennis,
                  ),
                ),
                const TextSpan(text: 'QUANDO QUISER.'),
              ],
            ),
            style: GoogleFonts.barlowCondensed(
              fontSize: 80,
              fontWeight: FontWeight.w900,
              color: AppTheme.textoBranco,
              height: 0.95,
            ),
          ),

          const SizedBox(height: 24),
          Text('Encontre a quadra perfeita para sua próxima partida\nExplore espaços disponíveis, escolha o melhor horário\ne reserve de forma simples e rápida.',
            style: GoogleFonts.barlow(
              fontSize: 18,
              fontWeight: FontWeight.w400,
              color: AppTheme.textoCinza,
              height: 1.6,
            ),
          ),
          const SizedBox(height: 30),
          const SearchBarMuzziTennis()
        ],
      ),
    );
  }
}
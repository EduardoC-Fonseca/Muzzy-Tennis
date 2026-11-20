import 'package:material_ui/material_ui.dart';
import 'package:muzzi_tennis/core/app_theme.dart';
import 'package:muzzi_tennis/pages/cadastro_quadras_page.dart';
import 'package:muzzi_tennis/pages/inicio_page.dart';
import 'package:muzzi_tennis/pages/login_page.dart';
import 'package:muzzi_tennis/pages/quadras_page.dart';

void main() {
  runApp(const MuzziTennisApp());
}

class MuzziTennisApp extends StatelessWidget {
  const MuzziTennisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Muzzi Tennis',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.muzziTennisTheme,
      home: const InicioPage(),
      routes: {
        '/quadras': (context) => const QuadrasPage(),
        '/cadastro':(context) => const CadastroQuadrasPage(),
        '/login': (context) => const LoginPage()
      },
    );
  }
}
import 'package:material_ui/material_ui.dart';
import 'package:muzzi_tennis/widgets/app_navbar.dart';

class InicioPage extends StatelessWidget {
  const InicioPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const AppNavebar(),
          const Expanded(
            child: Center(
              child: Text('Página Home'),
            ),
          ),
        ],
      ),
    );
  }
}